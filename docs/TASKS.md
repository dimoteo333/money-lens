# Initial Backlog

Create GitHub issues from these tasks. Do not start P1 until the P0 release gate passes.

## Milestone 0 — Repository and Walking Skeleton

- [ ] M0-01 Annotate the selected 2026-06-15 deposit reference and verify its expected evidence and authoritative calculation inputs.
- [ ] M0-02 Scaffold Next.js 16, FastAPI/Python 3.12, Docker Compose MinIO, and local development commands.
- [ ] M0-03 Add CI for lint, type-check, unit tests, build, and schema validation.
- [ ] M0-04 Deploy `/health` and a static accessible web shell to the demo environment.
- [ ] M0-05 Configure MinIO lifecycle, secrets, anonymous rate limits, KRW 5,000 daily budget, logs, kill switch, and automatic deletion.

Exit: the browser reaches the deployed UI and API through CI/CD.

## Milestone 1 — Evidence-Linked Review

- [ ] M1-01 Create the synthetic primary deposit document and golden annotation.
- [ ] M1-02 Implement file validation and temporary storage.
- [ ] M1-03 Implement OCR/layout adapter and fixture adapter.
- [ ] M1-04 Implement structured extraction and product-fact validation.
- [ ] M1-05 Display conditions with page excerpt and `needs_review` state.
- [ ] M1-06 Add golden-document regression tests.

Exit: the primary document produces verified, traceable facts without calculations or LLM explanation.

## Milestone 2 — Rules and Money Scenario

- [ ] M2-01 Define versioned deposit risk rules.
- [ ] M2-02 Implement preferential-rate or early-cancellation formula.
- [ ] M2-03 Add independently calculated fixtures and boundary tests.
- [ ] M2-04 Build accessible simulation input and result views.
- [ ] M2-05 Show matched rule, formula version, inputs, units, assumptions, and rounding.

Exit: changing one input changes a deterministic, independently verified result.

## Milestone 3 — Explanation and Understanding

- [ ] M3-01 Implement grounded explanation input/output schema.
- [ ] M3-02 Implement Plain, Number-First, and Example-First modes.
- [ ] M3-03 Add cross-mode fact and number consistency checks.
- [ ] M3-04 Generate three material understanding questions.
- [ ] M3-05 Implement incorrect/unsure targeted re-explanation and re-check.

Exit: wording adapts without changing evidence, facts, severity, or numbers.

## Milestone 4 — Report and Demo Hardening

- [ ] M4-01 Build printable one-page report.
- [ ] M4-02 Add privacy notice, disclaimer, retention display, and delete action.
- [ ] M4-03 Complete keyboard, screen-reader, zoom, and mobile checks.
- [ ] M4-04 Add labeled preprocessed and cached-explanation fallbacks.
- [ ] M4-05 Run two clean end-to-end rehearsals and record timing.
- [ ] M4-06 Freeze versions, document rollback, and prepare teardown.

Exit: all P0 release gates and README demo-success criteria pass.

## Issue Assignment Rule for Two People

- One person owns user flow and presentation for a slice.
- The other owns contract, backend, and validation for the same slice.
- Switch reviewer roles on the next slice.
- Agents may implement isolated issues, but a human owns acceptance and merge.
