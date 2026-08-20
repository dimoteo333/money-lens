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
