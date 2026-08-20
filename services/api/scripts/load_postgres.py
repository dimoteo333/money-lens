"""Load a collection manifest into PostgreSQL.

Usage:
    export DATABASE_URL=postgres://money_lens:...@localhost:5432/money_lens
    .venv/bin/python -m scripts.load_postgres --manifest path/to/manifest.json

Idempotent per run: re-loading the same manifest updates last_seen markers
without duplicating rows. New document content (sha256) creates a
document_version row — that is the 약관 개정 signal for the daily batch.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Optional

import psycopg
from psycopg.types.json import Jsonb

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"


def ensure_schema(conn: psycopg.Connection) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.transaction():
        conn.execute(sql)


def load_manifest(conn: psycopg.Connection, manifest: dict,
                  manifest_path: str) -> int:
    bank_code = manifest["bank_code"]
    bank_name = manifest.get("bank_name", bank_code)
    collected_at = manifest["collected_at"]

    with conn.transaction():
        conn.execute(
            "INSERT INTO bank (code, name) VALUES (%s, %s) "
            "ON CONFLICT (code) DO NOTHING",
            (bank_code, bank_name),
        )
        run_id_row = conn.execute(
            """INSERT INTO collection_run
                   (bank_code, collected_at, manifest_path, n_products, n_documents, notes)
               VALUES (%s, %s::timestamptz, %s, %s, %s, %s)
               RETURNING id""",
            (bank_code, collected_at, manifest_path,
             len(manifest.get("products", [])),
             len(manifest.get("documents", [])),
             Jsonb(manifest.get("notes", []))),
        ).fetchone()
        run_id = run_id_row[0]

        product_ids: dict[str, int] = {}
        for p in manifest.get("products", []):
            row = conn.execute(
                """INSERT INTO product
                       (bank_code, product_code, product_name, category_code,
                        category_name, summary, sale_start, sale_end,
                        source_api, source_page, raw,
                        first_seen_run, last_seen_run, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true)
                   ON CONFLICT (bank_code, product_code) DO UPDATE SET
                       product_name = EXCLUDED.product_name,
                       category_code = EXCLUDED.category_code,
                       category_name = EXCLUDED.category_name,
                       summary = EXCLUDED.summary,
                       sale_start = EXCLUDED.sale_start,
                       sale_end = EXCLUDED.sale_end,
                       source_api = EXCLUDED.source_api,
                       source_page = EXCLUDED.source_page,
                       raw = EXCLUDED.raw,
                       last_seen_run = EXCLUDED.last_seen_run,
                       is_active = true
                   RETURNING id""",
                (bank_code, p["product_code"], p["product_name"],
                 p.get("category_code", ""), p.get("category_name", ""),
                 p.get("summary", ""), p.get("sale_start", ""),
                 p.get("sale_end", ""), p.get("source_api", ""),
                 p.get("source_page", ""), Jsonb(p.get("raw", {})),
                 run_id, run_id),
            ).fetchone()
            product_ids[p["product_code"]] = row[0]

        n_versions = 0
        for d in manifest.get("documents", []):
            pid = product_ids.get(d["product_code"])
            if pid is None:
                continue  # orphan doc without product record — skip loudly? note it
            row = conn.execute(
                """INSERT INTO document
                       (product_id, form_id, title, doc_category_code, file_url,
                        local_path, current_sha256, current_bytes, source_api, raw,
                        first_seen_run, last_seen_run)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (product_id, form_id) DO UPDATE SET
                       title = EXCLUDED.title,
                       doc_category_code = EXCLUDED.doc_category_code,
                       file_url = EXCLUDED.file_url,
                       local_path = EXCLUDED.local_path,
                       current_sha256 = EXCLUDED.current_sha256,
                       current_bytes = EXCLUDED.current_bytes,
                       source_api = EXCLUDED.source_api,
                       raw = EXCLUDED.raw,
                       last_seen_run = EXCLUDED.last_seen_run
                   RETURNING id""",
                (pid, d["form_id"], d["title"], d.get("category_code", ""),
                 d.get("file_url", ""), d.get("local_path"),
                 d.get("sha256"), d.get("bytes"), d.get("source_api", ""),
                 Jsonb(d.get("raw", {})), run_id, run_id),
            ).fetchone()
            doc_id = row[0]
            if d.get("sha256"):
                vrow = conn.execute(
                    """INSERT INTO document_version
                           (document_id, sha256, bytes, file_url, local_path,
                            collected_at, run_id)
                       VALUES (%s,%s,%s,%s,%s,%s::timestamptz,%s)
                       ON CONFLICT (document_id, sha256) DO NOTHING
                       RETURNING id""",
                    (doc_id, d["sha256"], d.get("bytes"), d.get("file_url", ""),
                     d.get("local_path"), collected_at, run_id),
                ).fetchone()
                if vrow is not None:
                    n_versions += 1

        # products absent from this run are no longer sold through this channel
        conn.execute(
            """UPDATE product SET is_active = false
               WHERE bank_code = %s AND last_seen_run < %s""",
            (bank_code, run_id),
        )
    return n_versions


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    ap.add_argument("--skip-schema", action="store_true")
    args = ap.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL is required (env or --database-url)")
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    with psycopg.connect(args.database_url) as conn:
        if not args.skip_schema:
            ensure_schema(conn)
        n_versions = load_manifest(conn, manifest, args.manifest)
        row = conn.execute(
            "SELECT count(*) FROM product WHERE bank_code = %s",
            (manifest["bank_code"],),
        ).fetchone()
        docs = conn.execute(
            "SELECT count(*) FROM document d JOIN product p ON p.id = d.product_id "
            "WHERE p.bank_code = %s",
            (manifest["bank_code"],),
        ).fetchone()
        print(json.dumps({
            "bank": manifest["bank_code"],
            "products": row[0],
            "documents": docs[0],
            "new_document_versions": n_versions,
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
