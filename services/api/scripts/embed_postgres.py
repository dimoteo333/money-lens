"""Embed pending chunks (RAG stage 3).

Reads chunks whose embedding is missing or was produced by a different
model, embeds them in batches, and updates the chunk rows. Idempotent:
re-running embeds nothing unless the model changed (--force re-embeds all).

Usage:
    export DATABASE_URL=postgres://money_lens:...@localhost:5432/money_lens
    .venv/bin/python -m scripts.embed_postgres                 # local model
    .venv/bin/python -m scripts.embed_postgres --provider hash # tests
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.ingestion.embedder import get_embedder, vector_literal  # noqa: E402

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"

BATCH = 64


def embedding_column_type(conn: psycopg.Connection) -> str:
    row = conn.execute(
        """SELECT format_type(a.atttypid, a.atttypmod)
           FROM pg_attribute a
           JOIN pg_class c ON c.oid = a.attrelid
           WHERE c.relname = 'chunk' AND a.attname = 'embedding'"""
    ).fetchone()
    if row is None:
        raise SystemExit("chunk.embedding column missing — run schema first")
    return row[0]


def pending_chunks(conn: psycopg.Connection, model: str, force: bool):
    if force:
        where, params = "", ()
    else:
        where = ("WHERE embedding IS NULL "
                 "OR embedding_model IS DISTINCT FROM %s")
        params = (model,)
    rows = conn.execute(
        f"""SELECT c.id,
                   p.product_name || ' ' || d.title || ' ' || c.heading
                       || chr(10) || c.text AS embed_input
            FROM chunk c
            JOIN document_version dv ON dv.id = c.document_version_id
            JOIN document d ON d.id = dv.document_id
            JOIN product p ON p.id = d.product_id
            {where.replace('embedding', 'c.embedding').replace('text', 'c.text')}
            ORDER BY c.id""",
        params,
    ).fetchall()
    return rows


def embed_pending(conn: psycopg.Connection, embedder, force: bool) -> dict:
    col_type = embedding_column_type(conn)
    model = embedder.name
    rows = pending_chunks(conn, model, force)
    n = 0
    for start in range(0, len(rows), BATCH):
        batch = rows[start:start + BATCH]
        vecs = embedder.embed([r[1] for r in batch])
        for (chunk_id, _), vec in zip(batch, vecs):
            if len(vec) != embedder.dim:
                raise SystemExit(
                    f"dim mismatch: model {embedder.name} returned {len(vec)}"
                )
            base = col_type.split("[")[0].split("(")[0]  # 'vector' or 'real'
            style = "array" if base == "real" else "vector"
            cast = "real[]" if base == "real" else "vector"
            conn.execute(
                f"UPDATE chunk SET embedding = %s::{cast}, "
                "embedding_model = %s WHERE id = %s",
                (vector_literal(vec, style), model, chunk_id),
            )
        n += len(batch)
        print(f"  embedded {n}/{len(rows)}", flush=True)
    return {"model": model, "dim": embedder.dim, "column": col_type,
            "pending": len(rows), "embedded": n}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="local", choices=["local", "hash"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--dim", type=int, default=384,
                    help="dim for --provider hash")
    ap.add_argument("--force", action="store_true",
                    help="re-embed every chunk (model change)")
    ap.add_argument("--limit", type=int, default=0, help="smoke-test cap")
    args = ap.parse_args()

    db = os.environ.get("DATABASE_URL")
    if not db:
        raise SystemExit("DATABASE_URL is required")

    embedder = get_embedder(args.provider, args.model, args.dim)
    with psycopg.connect(db) as conn:
        conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        stats = embed_pending(conn, embedder, args.force)
        if args.limit:
            stats["note"] = f"limit={args.limit} (ignored; ran full pending set)"
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
