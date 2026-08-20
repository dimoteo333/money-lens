"""Stage 1 collection tests — parse against recorded fixtures, no network."""

import json
from pathlib import Path

import httpx
import pytest

from app.ingestion.shinhan import (
    ShinhanClient, ShinhanAdapter, collect_shinhan, safe_filename,
)

FIX = Path(__file__).parent / "fixtures" / "shinhan"


def _mock_client(list_body, docs_body):
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        code = payload["dataBody"]["ricInptRootInfo"]["serviceCode"]
        if code == "RSRDE0700A06":
            return httpx.Response(200, json=list_body)
        if code == "RSRFO0401A01":
            return httpx.Response(200, json=docs_body)
        return httpx.Response(500, json={"dataHeader": {"result": "FAIL"}})
    return ShinhanClient(transport=httpx.MockTransport(handler), delay_seconds=0)


def test_list_products_parses_fields():
    adapter = ShinhanAdapter(_mock_client(
        json.loads((FIX / "prd_list.json").read_text()), None))
    products = adapter.list_products("S03")
    assert len(products) == 2
    p = products[0]
    assert p.bank_code == "shinhan"
    assert p.product_code == "230011985"
    assert p.product_name == "신한 알.쏠 적금"
    assert p.category_code == "S03"
    assert p.source_api == "RSRDE0700A06"
    assert "<" not in p.summary  # html stripped


def test_product_documents_parses_pdf_urls():
    adapter = ShinhanAdapter(_mock_client(
        json.loads((FIX / "prd_list.json").read_text()),
        json.loads((FIX / "prd_docs.json").read_text())))
    products = adapter.list_products("S03")
    docs = adapter.product_documents(products[0])
    assert len(docs) == 4
    yak = [d for d in docs if "약관" in d.title]
    assert yak, "expected terms docs in fixture"
    for d in docs:
        assert d.file_url.startswith("https://img.shinhan.com/")
        assert d.source_api == "RSRFO0401A01"
        assert d.product_code == products[0].product_code


def test_collect_manifest_and_dedupe(tmp_path):
    list_body = json.loads((FIX / "prd_list.json").read_text())
    docs_body = json.loads((FIX / "prd_docs.json").read_text())
    client = _mock_client(list_body, docs_body)
    manifest = collect_shinhan(
        tmp_path, categories=("S03", "S03"), download=False, client=client,
        collected_at="2026-08-20T13:00:00+09:00",
    )
    codes = [p["product_code"] for p in manifest["products"]]
    assert len(codes) == len(set(codes)), "duplicate products must be deduped"
    assert manifest["collected_at"].startswith("2026-08-20")
    assert manifest["bank_code"] == "shinhan"
    out = tmp_path / "shinhan" / "20260820" / "manifest.json"
    assert out.exists()
    saved = json.loads(out.read_text())
    assert len(saved["documents"]) == len(manifest["documents"]) == 8


def test_error_raises_on_failed_header():
    failing = {"dataHeader": {"result": "FAIL", "resultCode": "E1", "resultMsg": "boom"},
               "dataBody": {}}
    client = ShinhanClient(transport=httpx.MockTransport(
        lambda r: httpx.Response(200, json=failing)), delay_seconds=0)
    adapter = ShinhanAdapter(client)
    with pytest.raises(Exception):
        adapter.list_products("S03")


def test_safe_filename():
    name = safe_filename("207013512", "쏠편한 정기예금 특약 ",
                         "https://img.shinhan.com/x/abc.PDF?123")
    assert name.endswith(".PDF")
    assert " " not in name
    assert name.startswith("207013512")
