# ADR-0004: Retriever embedding — local multilingual MiniLM on pgvector

- Status: Accepted
- Date: 2026-08-20
- Issue: #13

## Context

RAG stage 3 needs chunk embeddings for semantic retrieval over Korean
banking terms (약관·상품설명서). The corpus is public text, ~1k chunks today,
growing with each bank adapter. Constraints:

- MVP runs locally (docker compose Postgres, MinIO); no managed vector DB.
- Cost policy (M0-05) prefers zero-marginal-cost local inference for the
  demo path.
- Retrieval feeds the extraction stage; every hit must carry page/span
  provenance regardless of similarity backend.

## Decision

1. Store embeddings in the existing Postgres via **pgvector**
   (`vector(384)`, HNSW cosine index). Compose ships
   `pgvector/pgvector:pg16`. A schema-level `real[]` + cosine-function
   fallback keeps bare-Postgres dev boxes working; application code is
   identical across backends.
2. Default embedder: **paraphrase-multilingual-MiniLM-L12-v2** (384-dim,
   Korean-capable, CPU-friendly, Apache-2.0) via sentence-transformers,
   loaded locally. Embedders are pluggable behind one protocol
   (`app/ingestion/embedder.py`); a deterministic hashing embedder covers
   tests and wiring checks with no model download.
3. `chunk.embedding_model` records which model produced each vector.
   Retrieval refuses to mix models; changing model means re-embedding all
   chunks (`--force`).
4. Query-time and document-time vectors both L2-normalized so cosine is a
   dot product and the same literal fits either storage backend.

## Consequences

- Dim (384) is a schema commitment: swapping to bge-m3 (1024-d) or an API
  embedder later means `ALTER` the column and re-embed everything — an
  offline batch, not data loss.
- MiniLM quality is adequate for clause-level retrieval smoke tests, not a
  final quality claim. Before the demo we should A/B: MiniLM vs bge-m3
  vs API embeddings on a labeled question set; tsvector lexical search is
  indexed as the lexical baseline.
- No customer data ever leaves the boundary: only public 약관 text is
  embedded, locally.
