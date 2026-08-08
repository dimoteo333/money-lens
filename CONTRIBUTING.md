# Contributing

## Branch and PR Flow

- `main` must remain deployable.
- Use short-lived branches: `feature/<issue>-<slug>`, `fix/<issue>-<slug>`, or `docs/<issue>-<slug>`.
- Prefer one issue and one vertical outcome per PR.
- Require CI and one human review before squash merge.
- Never commit directly to `main`, force-push it, or commit secrets.

## Issue Quality

An implementation issue needs:

- User outcome.
- In-scope and out-of-scope behavior.
- Testable acceptance criteria.
- Relevant guardrails and dependencies.
- Demo relevance: `P0`, `P1`, or `P2`.

## Decision Records

Create an ADR under `docs/decisions/` when changing:

- Authoritative calculation or risk boundaries.
- Data contracts used across components.
- Cloud/runtime architecture.
- Storage, retention, authentication, or privacy posture.
- A technology choice that is costly to reverse.

Use the next four-digit number. Do not rewrite accepted ADR history; add a superseding ADR.

## Review Priorities

Review in this order:

1. Financial and user harm risk.
2. Traceability and uncertainty handling.
3. Privacy and security.
4. Accessibility.
5. Correctness and tests.
6. Maintainability and style.
