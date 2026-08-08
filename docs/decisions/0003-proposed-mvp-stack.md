# ADR-0003: Proposed MVP Stack

- Status: Proposed
- Date: 2026-08-06

## Context

Two people need to build and deploy a competition MVP quickly while preserving clear boundaries for accessible UI, document processing, deterministic Python rules/calculations, and AWS deployment.

## Proposal

- Monorepo.
- Next.js 16, TypeScript, Node.js 24 LTS, and npm for the responsive accessible web application.
- FastAPI and Python 3.12 using `venv`, pip, and a fully pinned `requirements.txt` for document orchestration, rules, and calculations.
- Docker Compose MinIO as the local S3-compatible document store.
- In-memory metadata persistence for the walking skeleton.
- S3-compatible object storage for temporary documents in the demo environment.
- A managed data store chosen after a one-hour access-pattern spike.
- GitHub Actions with short-lived AWS federation for CI/CD.
- Local and demo environments only.
- Printable HTML as the P0 report; PDF generation is deferred until P0 is stable.
- Public anonymous demo access with explicit rate, retention, concurrency, budget, and kill-switch limits.

Prefer API Gateway/Lambda for short stateless requests. Use a queued worker or container runtime if measured OCR/model execution, streaming, or file processing does not fit that model.

QM remains in a separate deployment repository and communicates through GitHub/Slack; Money Lens must not depend on QM at runtime.

## Alternatives

- Full TypeScript stack: fewer languages but weaker alignment with existing extraction/calculation libraries.
- Full Python server-rendered UI: simpler backend integration but slower rich accessible UI iteration for this team.
- Always-on container and relational database: familiar but creates standing cost and operations before access patterns are known.

## Acceptance Test Before Marking Accepted

- Deploy an accessible page and `/health` through CI.
- Upload one fixture and round-trip safe metadata.
- Measure one OCR/model request and decide sync versus async.
- Validate local MinIO lifecycle behavior, including the 24-hour retention deadline and explicit deletion.
- Confirm local development works on both team machines.
