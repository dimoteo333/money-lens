-- Money Lens ingestion schema (PostgreSQL)
-- Stage 1 collection store: public product/terms data with provenance.
-- Nothing here is a verified product fact — facts are promoted by the
-- validation stage, not by collection.

BEGIN;

CREATE TABLE IF NOT EXISTS bank (
    code        TEXT PRIMARY KEY,          -- 'shinhan'
    name        TEXT NOT NULL,             -- '신한은행'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS collection_run (
    id             BIGSERIAL PRIMARY KEY,
    bank_code      TEXT NOT NULL REFERENCES bank(code),
    collected_at   TIMESTAMPTZ NOT NULL,   -- run timestamp from manifest
    manifest_path  TEXT NOT NULL,
    n_products     INTEGER NOT NULL DEFAULT 0,
    n_documents    INTEGER NOT NULL DEFAULT 0,
    notes          JSONB NOT NULL DEFAULT '[]'::jsonb,
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS product (
    id               BIGSERIAL PRIMARY KEY,
    bank_code        TEXT NOT NULL REFERENCES bank(code),
    product_code     TEXT NOT NULL,        -- bank-internal code, e.g. '207013512'
    product_name     TEXT NOT NULL,
    category_code    TEXT NOT NULL DEFAULT '',   -- S01/S02/S03
    category_name    TEXT NOT NULL DEFAULT '',
    summary          TEXT NOT NULL DEFAULT '',
    sale_start       TEXT NOT NULL DEFAULT '',   -- as published (YYYYMMDDHHMM)
    sale_end         TEXT NOT NULL DEFAULT '',
    source_api       TEXT NOT NULL DEFAULT '',
    source_page      TEXT NOT NULL DEFAULT '',
    raw              JSONB NOT NULL DEFAULT '{}'::jsonb,
    first_seen_run   BIGINT NOT NULL REFERENCES collection_run(id),
    last_seen_run    BIGINT NOT NULL REFERENCES collection_run(id),
    is_active        BOOLEAN NOT NULL DEFAULT true,  -- seen in the latest run
    UNIQUE (bank_code, product_code)
);

CREATE TABLE IF NOT EXISTS document (
    id                BIGSERIAL PRIMARY KEY,
    product_id        BIGINT NOT NULL REFERENCES product(id),
    form_id           TEXT NOT NULL,          -- bank form id, stable across revisions
    title             TEXT NOT NULL,
    doc_category_code TEXT NOT NULL DEFAULT '',  -- F01 약관 / F02 양식 / F03 상품설명서
    file_url          TEXT NOT NULL DEFAULT '',
    local_path        TEXT,
    current_sha256    TEXT,
    current_bytes     BIGINT,
    source_api        TEXT NOT NULL DEFAULT '',
    raw               JSONB NOT NULL DEFAULT '{}'::jsonb,
    first_seen_run    BIGINT NOT NULL REFERENCES collection_run(id),
    last_seen_run     BIGINT NOT NULL REFERENCES collection_run(id),
    UNIQUE (product_id, form_id)
);

-- Immutable content versions: a new sha256 for the same form means the bank
-- revised the document (약관 개정). This is the daily-batch diff source.
CREATE TABLE IF NOT EXISTS document_version (
    id             BIGSERIAL PRIMARY KEY,
    document_id    BIGINT NOT NULL REFERENCES document(id),
    sha256         TEXT NOT NULL,
    bytes          BIGINT,
    file_url       TEXT NOT NULL DEFAULT '',
    local_path     TEXT,
    collected_at   TIMESTAMPTZ NOT NULL,
    run_id         BIGINT NOT NULL REFERENCES collection_run(id),
    UNIQUE (document_id, sha256)
);

CREATE INDEX IF NOT EXISTS idx_product_bank_category ON product(bank_code, category_code);
CREATE INDEX IF NOT EXISTS idx_document_product ON document(product_id);
CREATE INDEX IF NOT EXISTS idx_document_version_doc ON document_version(document_id, collected_at DESC);


-- Stage 2: structure-aware chunks with page/char-span provenance.
-- One chunk = one or more 제N조 units (or a split of an oversized unit),
-- so retrieval answers can cite (title, page, span) in the actual PDF.
CREATE TABLE IF NOT EXISTS chunk (
    id                  BIGSERIAL PRIMARY KEY,
    document_version_id BIGINT NOT NULL REFERENCES document_version(id) ON DELETE CASCADE,
    seq                 INTEGER NOT NULL,       -- order within the version
    heading             TEXT NOT NULL DEFAULT '',
    text                TEXT NOT NULL,
    page_start          INTEGER NOT NULL,
    page_end            INTEGER NOT NULL,
    char_start          INTEGER NOT NULL,       -- span into assembled doc text
    char_end            INTEGER NOT NULL,
    n_articles          INTEGER NOT NULL DEFAULT 1,
    chunked_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_version_id, seq)
);

CREATE INDEX IF NOT EXISTS idx_chunk_version ON chunk(document_version_id, seq);
-- Stage 3: embeddings. pgvector when available (compose ships
-- pgvector/pgvector:pg16), real[] + cosine helper otherwise (bare
-- Postgres dev boxes). Both backends take the same literal '[a,b,c]'.
ALTER TABLE chunk ADD COLUMN IF NOT EXISTS embedding_model TEXT;

DO $embed$
DECLARE
    has_vector boolean;
BEGIN
    SELECT EXISTS (SELECT 1 FROM pg_available_extensions
                   WHERE name = 'vector') INTO has_vector;
    IF has_vector THEN
        CREATE EXTENSION IF NOT EXISTS vector;
        EXECUTE 'ALTER TABLE chunk ADD COLUMN IF NOT EXISTS embedding vector(384)';
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_chunk_embedding_hnsw
                 ON chunk USING hnsw (embedding vector_cosine_ops)';
    ELSE
        RAISE NOTICE 'pgvector not available: using real[] fallback (dev only)';
        ALTER TABLE chunk ADD COLUMN IF NOT EXISTS embedding real[];
    END IF;
END
$embed$;

-- Fallback cosine similarity over real[] (dot of normalized vectors).
-- Used by retrieval when the column type is real[]; pgvector uses <=>.
CREATE OR REPLACE FUNCTION ml_cosine_sim(a real[], b real[]) RETURNS real
LANGUAGE sql IMMUTABLE AS $$
    SELECT COALESCE((
        SELECT sum(x * y) FROM unnest(a, b) AS t(x, y)
    ), 0)
$$;

-- Lexical fallback search (stage 3 retrieval A/B).
CREATE INDEX IF NOT EXISTS idx_chunk_text_search
    ON chunk USING gin (to_tsvector('simple', text));

COMMIT;
