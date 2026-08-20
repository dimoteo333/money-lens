"""Chunk document_versions from PostgreSQL (RAG stage 2).

Reads every document_version that has a local PDF, chunks it with
structure-aware boundaries (제N조), and stores chunks with page/char-span
provenance. Idempotent per version: already-chunked versions are skipped
unless --force re-chunks them (replacing their chunks atomically).

Usage:
    export DATABASE_URL=postgres://money_lens:...@localhost:5432/money_lens
    .venv/bin/python -m scripts.chunk_postgres \
        --data-root ../../data/ingestion [--limit N] [--force]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.chunker import ChunkingError, chunk_pdf  # noqa: E402

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"

INSERT_CHUNK = """
    INSERT INTO chunk
        (document_version_id, seq, heading, text,
         page_start, page_end, char_start, char_end, n_articles)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def ensure_chunk_table(conn: psycopg.Connection) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.transaction():
        conn.execute(sql)


def chunk_pending(conn: psycopg.Connection, data_root: Path,
                  limit: int | None = None, force: bool = False) -> dict:
    where = "" if force else """
        AND NOT EXISTS (SELECT 1 FROM chunk c
                        WHERE c.document_version_id = dv.id)"""
    sql = f"""
        SELECT dv.id,
               regexp_replace(cr.manifest_path, '/[^/]*$', '') || '/' || dv.local_path,
               d.title
        FROM document_version dv
        JOIN document d ON d.id = dv.document_id
        JOIN collection_run cr ON cr.id = dv.run_id
        WHERE dv.local_path IS NOT NULL {where}
        ORDER BY dv.id
    """
    rows = conn.execute(sql).fetchall()
    if limit:
        rows = rows[:limit]

    stats = {"versions": len(rows), "chunked": 0, "chunks": 0,
             "missing_files": 0, "errors": []}
    for version_id, rel_path, title in rows:
        pdf = Path(rel_path)
        if not pdf.is_absolute():
            pdf = data_root / rel_path
        if not pdf.exists():
            stats["missing_files"] += 1
            continue
        try:
            _, chunks = chunk_pdf(pdf)
        except ChunkingError as e:
            stats["errors"].append({"version_id": version_id, "title": title,
                                    "error": str(e)})
            continue
        with conn.transaction():
            conn.execute("DELETE FROM chunk WHERE document_version_id = %s",
                         (version_id,))
            with conn.cursor() as cur:
                cur.executemany(
                    INSERT_CHUNK,
                    [(version_id, c.seq, c.heading, c.text, c.page_start,
                      c.page_end, c.char_start, c.char_end, c.n_articles)
                     for c in chunks],
                )
        stats["chunked"] += 1
        stats["chunks"] += len(chunks)
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="../../data/ingestion")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true",
                    help="re-chunk versions that already have chunks")
    args = ap.parse_args()

    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is required")
    data_root = Path(args.data_root)

    with psycopg.connect(url) as conn:
        ensure_chunk_table(conn)
        stats = chunk_pending(conn, data_root, args.limit, args.force)
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
