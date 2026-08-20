# Application API

FastAPI + Python 3.12 walking skeleton (M0-02). Responsibility will grow to: safe upload orchestration, document state, product-fact validation, versioned risk rules, deterministic calculations, understanding attempts, and report snapshots.

Calculation modules must remain pure and model-independent. Provider integrations sit behind adapters with deterministic fixtures.

## Local commands

```bash
cd services/api
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

# run
.venv/bin/uvicorn app.main:app --reload --port 8000
curl http://localhost:8000/health

# test
.venv/bin/python -m pytest tests/ -q
```

MinIO (from the repository root):

```bash
docker compose up -d
docker compose ps
```

## PostgreSQL collection store

```bash
docker compose up -d          # minio + postgres
cp .env.example .env          # set POSTGRES_* / DATABASE_URL

# daily batch: collect then load
.venv/bin/python -m scripts.collect_shinhan --out ../../data/ingestion
.venv/bin/python -m scripts.load_postgres \
    --manifest ../../data/ingestion/shinhan/<YYYYMMDD>/manifest.json
.venv/bin/python -m scripts.chunk_postgres --data-root ../../data/ingestion

# stage 3: embed chunks (local multilingual MiniLM, 384-dim)
.venv/bin/pip install sentence-transformers   # optional, real model
.venv/bin/python -m scripts.embed_postgres

# retrieval smoke test with citation provenance
.venv/bin/python -m scripts.retrieve "중도해지하면 이자는 어떻게 되나요" -k 5
```

Schema: `db/schema.sql` — bank / collection_run / product / document /
document_version. A new sha256 for the same form_id creates a
document_version row (약관 개정 signal). Loading is idempotent per manifest.
