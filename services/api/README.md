# Application API

Planned responsibility: safe upload orchestration, document state, product-fact validation, versioned risk rules, deterministic calculations, understanding attempts, and report snapshots.

Proposed stack: FastAPI + Python. Calculation modules must remain pure and model-independent. Provider integrations sit behind adapters with deterministic fixtures.

Before implementation, document exact environment, lint, type-check, test, and local-run commands here and in `AGENTS.md`.
