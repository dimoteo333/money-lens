# Open Questions

Resolve only the questions that block the next vertical slice. Record durable answers in an ADR or PRD update.

## Resolved for the repository bootstrap

- Primary reference: Shinhan SOLmate fixed-term deposit product description, version 2026-06-15.
- Source handling: the original PDF is local-only and must not be committed or redistributed from this repository.
- P0 scenario: early-termination interest using explicit principal, opening date, and termination date inputs.
- P0 report: printable one-page HTML.
- Demo access: public anonymous access with the limits recorded in `.env.example`.
- Local document store: Docker Compose MinIO.
- Walking-skeleton metadata store: in-memory adapter.
- Ownership: Jun (`@dimoteo333`) owns extraction, calculations, AWS, and CI; Min owns product, demo, web, and accessibility.
- Daily live-processing budget: KRW 5,000; warn at 70% and stop new live processing at 100%.

## Product

- What is the exact competition demo time limit and judging rubric?
- Which language, if any, is the first multilingual P1 mode?

## Data and AI

- Which OCR/layout engine performs best on the chosen Korean fixture?
- Which fields are required before a deposit review can be `ready`?
- What confidence and validation combination leads to `verified` versus `needs_review`?
- Are grounded explanations generated live, cached, or hybrid during the demo?
- How will output claims and numbers be mechanically checked against the verified snapshot?
- How does Shinhan define elapsed months and the annual day-count denominator, including leap years, for this product's early-termination calculation?
- Which official bank response or account-calculation evidence independently confirms the authoritative expected fixture?

## Architecture

- Does measured processing latency require an asynchronous queue and worker?
- Do access patterns justify PostgreSQL, or is a document/key-value store simpler?
- How will the frontend display PDF evidence consistently on mobile and desktop?

## Team and Operations

- What is Min's GitHub username?
- What date freezes model, prompt, schema, rule, and formula versions?
- When are the two mandatory clean demo rehearsals scheduled?
