"""Shinhan Bank collection adapter — stage 1 (collection batch).

Reverse-engineered from the bank's public mobile web (m.shinhan.com), which
serves all retail-product data through one JSON endpoint:

    POST https://m.shinhan.com/serviceEndpoint/httpDigital

with a service code in dataBody.ricInptRootInfo.serviceCode. Verified
service codes used here:

    RSRDE0700A06  product list per category (GBN: S01 입출금 / S02 예금 / S03 적금·청약)
    RSRDE0700A08  product detail
    RSRFO0401A01  per-product document list (약관 / 상품설명서 PDF URLs)

Term/explanatory PDFs are static files under img.shinhan.com and download
with plain HTTP GET. No browser is required for any of this.

Boundaries: this adapter only collects PUBLIC marketing/terms material and
records provenance. It never produces verified facts (validation stage) and
never touches customer data.
"""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlsplit

import httpx

from .models import DocumentRecord, ProductRecord

BASE = "https://m.shinhan.com"
PC_BASE = "https://bank.shinhan.com"
PC_ENDPOINT = PC_BASE + "/serviceEndpoint/httpDigital"
ENDPOINT = BASE + "/serviceEndpoint/httpDigital"

MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)

CATEGORIES = {
    "S01": "입출금",
    "S02": "예금",
    "S03": "적금/청약",
}

_SAFE_NAME = re.compile(r"[^0-9A-Za-z가-힣._-]+")


class ShinhanCollectionError(RuntimeError):
    pass


class ShinhanClient:
    """Thin JSON-API client with pluggable transport (for tests)."""

    def __init__(self, transport: Optional[httpx.BaseTransport] = None,
                 delay_seconds: float = 1.0, timeout: float = 30.0):
        self._client = httpx.Client(
            transport=transport,
            timeout=timeout,
            headers={
                "User-Agent": MOBILE_UA,
                "Origin": BASE,
                "Referer": BASE + "/",
                "Content-Type": "application/json",
            },
        )
        self._delay = max(0.0, delay_seconds)
        self._last_call = 0.0

    def close(self) -> None:
        self._client.close()

    def _throttle(self) -> None:
        now = time.monotonic()
        wait = self._delay - (now - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def call(self, service_code: str, web_uri: str, body: dict,
             program_id: str = "") -> dict:
        self._throttle()
        payload = {
            "dataBody": {
                **body,
                "ricInptRootInfo": {
                    "serviceCode": service_code,
                    "serviceType": "TG",
                    "webUri": web_uri,
                },
            },
            "dataHeader": {
                "channelGbn": "DX",
                "language": "ko",
                "subChannel": "52",
                "trxCd": service_code,
                **({"programId": program_id} if program_id else {}),
            },
        }
        resp = self._client.post(ENDPOINT, json=payload)
        resp.raise_for_status()
        data = resp.json()
        header = data.get("dataHeader", {})
        if header.get("result") != "SUCCESS":
            raise ShinhanCollectionError(
                f"{service_code} failed: {header.get('result')} "
                f"{header.get('resultCode')} {header.get('resultMsg')}"
            )
        return data.get("dataBody", {})

    def pc_call(self, service_code: str, web_uri: str, body: dict) -> dict:
        """Call a PC-web (bank.shinhan.com) service through the same gateway."""
        self._throttle()
        payload = {
            "dataBody": {
                **body,
                "ricInptRootInfo": {
                    "serviceType": "TG",
                    "serviceCode": service_code,
                    "webUri": web_uri,
                    "language": "ko",
                    "isRule": "N",
                },
            },
            "dataHeader": {
                "trxCd": "RSRIC1000A65",
                "language": "ko",
                "subChannel": "49",
                "channelGbn": "D0",
            },
        }
        resp = self._client.post(PC_ENDPOINT, json=payload)
        resp.raise_for_status()
        data = resp.json()
        header = data.get("dataHeader", {})
        if header.get("result") != "SUCCESS":
            raise ShinhanCollectionError(
                f"{service_code} failed: {header.get('result')} {header.get('resultCode')}"
            )
        return data.get("dataBody", {})

    def download(self, url: str, dest_dir: Path) -> Path:
        self._throttle()
        name = Path(urlsplit(url).path).name or "document.bin"
        dest = dest_dir / name
        with self._client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in resp.iter_bytes(65536):
                    fh.write(chunk)
        return dest


class ShinhanAdapter:
    """Bank adapter for the collection batch. Same shape as future adapters."""

    bank_code = "shinhan"
    bank_name = "신한은행"

    def __init__(self, client: ShinhanClient):
        self.client = client

    def list_products(self, category_code: str) -> list[ProductRecord]:
        if category_code not in CATEGORIES:
            raise ValueError(f"unknown category {category_code}")
        body = self.client.call(
            "RSRDE0700A06",
            "/mw/pg/PR0200S0000F01",
            {
                "COM_SUBCHN_KBN": "",
                "C_JUMIN_NO": "",
                "GBN": category_code,
                "ORDER_GBN": "etc",
                "RESERVE_NEW_YN": "",
            },
        )
        items = body.get("PRD_DEP_NEW_LIST") or []
        page = f"{BASE}/mw/pg/PR0200S0000F01"
        out = []
        for it in items:
            code = str(it.get("상품코드") or "").strip()
            if not code:
                continue
            out.append(ProductRecord(
                bank_code=self.bank_code,
                product_code=code,
                product_name=(it.get("상품명") or "").strip(),
                category_code=str(it.get("상품구분") or category_code),
                category_name=(it.get("상품구분명") or CATEGORIES.get(category_code, "")).strip(),
                summary=re.sub(r"<[^>]+>", " ", it.get("상품안내") or "").strip(),
                sale_start=str(it.get("판매시작일자") or ""),
                sale_end=str(it.get("판매종료일자") or ""),
                source_api="RSRDE0700A06",
                source_page=page,
                raw=it,
            ))
        return out

    def list_online_products(self) -> list[ProductRecord]:
        """All online-sellable products (PC 온라인신규 list, TDT1018).

        Includes products the mobile category list omits (e.g. SOL메이트
        index-linked deposits). Categories are inferred from product-code
        prefix because this API has no category field.
        """
        body = self.client.pc_call(
            "TDT1018", "/index.jsp",
            {
                "product_gubun": 1,
                "product_srch_category": "",
                "product_order": "2",
                "product_srch": "",
                "product_srch_name": "",
                "product_srch_gubun": "1",
                "C_JUMIN_NO": "BXM_SESSION_system:cid",
            },
        )
        items = body.get("HPE_PRODUCT") or []
        out = []
        for it in items:
            code = str(it.get("F_PROD_ID") or "").strip()
            if not code:
                continue
            cat = code[:1] if code[:1] in ("1", "2") else ""
            # 11xxxxx/21xxxxx 수신(입출금/적금·청약), 20xxxxx 예금(거치/지수연동)
            if code.startswith("20"):
                cat_code, cat_name = "S02", "예금"
            elif code.startswith("23"):
                cat_code, cat_name = "S03", "적금/청약"
            elif code.startswith("22"):
                cat_code, cat_name = "S03", "적금/청약"
            else:
                cat_code, cat_name = "S01", "입출금"
            out.append(ProductRecord(
                bank_code=self.bank_code,
                product_code=code,
                product_name=(it.get("F_PROD_NAME") or "").strip(),
                category_code=cat_code,
                category_name=cat_name,
                summary=re.sub(r"<[^>]+>", " ", it.get("PRDT_INFORMATION") or "").strip(),
                sale_start=str(it.get("SELL_START_DT") or ""),
                sale_end=str(it.get("SELL_END_DT") or ""),
                source_api="TDT1018",
                source_page=PC_BASE + "/index.jsp?cr=020102010000",
                raw={k: v for k, v in it.items() if isinstance(v, (str, int, float, bool))},
            ))
        return out

    def product_documents(self, product: ProductRecord) -> list[DocumentRecord]:
        web_uri = "/mw/fin/pg/PR0100S0000F01"
        body = self.client.call(
            "RSRFO0401A01",
            web_uri,
            {"C_PROD_ID": product.product_code},
            program_id="PR0100S0000F01",
        )
        forms = body.get("FORM_LIST") or []
        out = []
        for f in forms:
            url = (f.get("PDF_FILE_NM") or "").strip()
            if not url:
                continue
            out.append(DocumentRecord(
                bank_code=self.bank_code,
                product_code=product.product_code,
                form_id=str(f.get("FORM_ID") or ""),
                title=(f.get("제목") or "").strip(),
                category_code=str(f.get("FORM_CATE_CD") or ""),
                file_url=url,
                source_api="RSRFO0401A01",
                raw=f,
            ))
        return out


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_filename(product_code: str, title: str, url: str) -> str:
    ext = Path(urlsplit(url).path).suffix or ".pdf"
    stem = _SAFE_NAME.sub("_", f"{product_code}_{title}").strip("_")[:80]
    return f"{stem}{ext}"


def collect_shinhan(out_root: Path, categories: Iterable[str] = ("S02",),
                    download: bool = True, client: Optional[ShinhanClient] = None,
                    limit_per_category: Optional[int] = None,
                    collected_at: str = "") -> dict:
    """Collect Shinhan products + document metadata (+ PDFs) into out_root.

    Layout: out_root/shinhan/<YYYYMMDD>/manifest.json, docs/<file>
    Returns the manifest dict.
    """
    from datetime import datetime, timezone, timedelta

    KST = timezone(timedelta(hours=9))
    now = collected_at or datetime.now(KST).isoformat(timespec="seconds")
    day = datetime.fromisoformat(now).strftime("%Y%m%d")

    base_dir = out_root / "shinhan" / day
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    cli = client or ShinhanClient()
    own_client = client is None
    adapter = ShinhanAdapter(cli)
    try:
        manifest = {
            "bank_code": "shinhan",
            "bank_name": "신한은행",
            "collected_at": now,
            "base_dir": str(base_dir),
            "products": [],
            "documents": [],
            "notes": [
                "stage 1 collection: public site data only, not verified facts",
                "endpoint: POST m.shinhan.com/serviceEndpoint/httpDigital",
            ],
        }
        seen_products: set[str] = set()
        # PC online-new list first: superset that includes index-linked deposits
        # the mobile category list omits. Mobile list data overrides (richer raw).
        try:
            online = adapter.list_online_products()
        except Exception as e:
            online = []
            manifest["notes"].append(f"online list failed: {e!r}")
        mobile_first: dict[str, dict] = {}
        for cat in categories:
            products = adapter.list_products(cat)
            if limit_per_category:
                products = products[:limit_per_category]
            for p in products:
                mobile_first[p.product_code] = p.to_dict()
        for code, rec in mobile_first.items():
            if code not in seen_products:
                seen_products.add(code)
                manifest["products"].append(rec)
        for p in online:
            if p.product_code in seen_products:
                continue
            seen_products.add(p.product_code)
            manifest["products"].append(p.to_dict())

        all_products = [ProductRecord(**rec) for rec in manifest["products"]]
        for p in all_products:
            if limit_per_category and p.source_api == "TDT1018" and p.product_code not in mobile_first:
                continue  # respect smoke-test limits for online-only products
            docs = adapter.product_documents(p)
            for d in docs:
                if download:
                    dest = docs_dir / safe_filename(p.product_code, d.title, d.file_url)
                    try:
                        path = cli.download(d.file_url, docs_dir)
                        path.rename(dest)
                        d.local_path = str(dest.relative_to(base_dir))
                        d.sha256 = sha256_of(dest)
                        d.bytes = dest.stat().st_size
                    except httpx.HTTPError as e:
                        manifest["notes"].append(
                            f"download failed: {d.title} {d.file_url}: {e!r}"
                        )
                manifest["documents"].append(d.to_dict())
        import json
        (base_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        return manifest
    finally:
        if own_client:
            cli.close()
