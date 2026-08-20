"""Retrieval smoke-test CLI (RAG stage 3).

Embeds the query with the same model stored on the chunks, returns the
top-k chunks with full citation provenance (bank / product / document /
article heading / page / char span) — the same evidence fields the
extraction stage will cite for high-impact facts.

Usage:
    .venv/bin/python -m scripts.retrieve "중도해지하면 이자는?" -k 5
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


def similarity_expr(col_type: str) -> str:
    """Similarity SQL with a %s placeholder for the query vector.

    The literal goes in as a bind parameter (never str.format — array
    braces collide). pgvector: 1 - cosine distance. real[]: dot product of
    L2-normalized vectors via the schema's ml_cosine_sim.
    """
    if col_type.startswith("vector"):
        return "1 - (c.embedding <=> %(q)s::vector)"
    return "ml_cosine_sim(c.embedding, %(q)s::real[])"


def retrieve(conn: psycopg.Connection, query: str, k: int,
             embedder, include_forms: bool = False) -> list[dict]:
    row = conn.execute(
        """SELECT format_type(a.atttypid, a.atttypmod)
           FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
           WHERE c.relname = 'chunk' AND a.attname = 'embedding'"""
    ).fetchone()
    col_type = row[0]
    qvec = embedder.embed([query])[0]
    style = "array" if col_type.startswith("real") else "vector"
    q = vector_literal(qvec, style)
    sim = similarity_expr(col_type)

    sql = f"""
        SELECT b.name,
               p.product_name,
               d.title,
               c.heading,
               c.page_start, c.page_end,
               c.char_start, c.char_end,
               {sim} AS score,
               c.text
        FROM chunk c
        JOIN document_version dv ON dv.id = c.document_version_id
        JOIN document d ON d.id = dv.document_id
        JOIN product p ON p.id = d.product_id
        JOIN bank b ON b.code = p.bank_code
        WHERE c.embedding IS NOT NULL
          AND (%(forms)s OR d.doc_category_code <> 'F02')
        ORDER BY {sim} DESC
        LIMIT %(k)s
    """
    rows = conn.execute(sql, {"q": q, "forms": include_forms, "k": k}).fetchall()
    keys = ("bank", "product", "document", "heading",
            "page_start", "page_end", "char_start", "char_end",
            "score", "text")
    return [dict(zip(keys, r)) for r in rows]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--provider", default="local", choices=["local", "hash"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--include-forms", action="store_true",
                    help="also search F02 양식/동의서 (default: excluded)")
    args = ap.parse_args()

    db = os.environ.get("DATABASE_URL")
    if not db:
        raise SystemExit("DATABASE_URL is required")

    embedder = get_embedder(args.provider, args.model)
    with psycopg.connect(db) as conn:
        # guard: chunks must be embedded with the model we query with
        other = conn.execute(
            "SELECT DISTINCT embedding_model FROM chunk "
            "WHERE embedding IS NOT NULL "
            "AND embedding_model IS DISTINCT FROM %s LIMIT 1",
            (embedder.name,),
        ).fetchone()
        if other:
            raise SystemExit(
                f"chunks embedded with {other[0]!r} but querying with "
                f"{embedder.name!r} — re-embed with --force or use the "
                "stored model"
            )
        hits = retrieve(conn, args.query, args.k, embedder,
                        include_forms=args.include_forms)

    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
        return
    for i, h in enumerate(hits, 1):
        print(f"[{i}] score={h['score']:.4f}  {h['bank']} · {h['product']}")
        print(f"    {h['document']} · {h['heading'] or '(전문)'} "
              f"· p.{h['page_start']}-{h['page_end']} "
              f"· span {h['char_start']}..{h['char_end']}")
        excerpt = h['text'][:180].replace("\n", " / ")
        print(f"    {excerpt}")
        print()


if __name__ == "__main__":
    main()
