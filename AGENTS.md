# Money Lens Agent Contract

This file is the operating contract for coding agents working in this repository.

## Mission

Build a competition-ready MVP that helps a user understand a financial product before agreeing to it. Money Lens is decision support, not financial, legal, credit, or investment advice.

The demo-critical path is:

1. Upload or select a curated financial document.
2. Extract structured facts with source locations and confidence.
3. Show material conditions and matched risk rules.
4. Run a deterministic money scenario.
5. Re-explain a misunderstood condition.
6. Produce a one-page report separating facts, assumptions, and review items.

## Source of Truth

Read these before changing code:

1. `README.md` — product vision and guardrails.
2. `docs/PRD.md` — prioritized MVP requirements and acceptance criteria.
3. `docs/ARCHITECTURE.md` — component and trust boundaries.
4. `docs/DATA_CONTRACTS.md` — authoritative data shapes.
5. `docs/QUALITY_PLAN.md` — required checks and evidence.
6. Relevant ADRs under `docs/decisions/`.

If documents conflict, stop and describe the conflict in the PR. Do not silently choose a convenient interpretation.

## Non-Negotiable Boundaries

- LLM output is never authoritative for financial calculations.
- High-impact facts must include source page, text span, and confidence.
- Risk levels come from versioned deterministic rules over verified facts.
- Low-confidence or conflicting evidence must be labeled `needs_review`.
- Explanation modes may change wording and presentation, never the underlying facts.
- Do not use real customer documents, credentials, or personally identifiable information.
- Do not log uploaded document contents, model prompts containing document text, or secrets.
- Do not add product recommendations, eligibility decisions, credit scoring, or sales language.
- Do not deploy directly from an agent workspace. Submit a PR; deployment runs through the approved workflow.

## Working Method

For every task:

1. Link the GitHub issue and restate its acceptance criteria.
2. Inspect existing contracts, tests, and decisions.
3. Post a short implementation plan before broad edits.
4. Implement the smallest complete vertical slice.
5. Add or update tests and fixtures.
6. Run all available checks.
7. Open a PR using `.github/PULL_REQUEST_TEMPLATE.md`.

Do not mix unrelated refactors with feature work. New dependencies, cloud resources, external APIs, schema changes, or guardrail changes require explicit PR notes and, when architectural, an ADR.

## Required Checks

Until application commands are introduced, run:

```bash
python3 -m json.tool schemas/product-facts.schema.json >/dev/null
```

When code is scaffolded, replace this section with the exact install, lint, type-check, test, build, and end-to-end commands. CI and this file must remain consistent.

Financial formula changes require:

- Boundary and invalid-input tests.
- Units, rounding policy, assumptions, and formula version.
- At least one independently calculated fixture.

Extraction changes require:

- Golden-document regression checks.
- Source-reference coverage for every high-impact fact.
- Explicit tests for missing, ambiguous, and conflicting clauses.

## Definition of Done

A task is done only when:

- Acceptance criteria pass.
- Relevant automated tests pass.
- Loading, empty, error, and `needs_review` states are handled.
- Accessibility behavior is preserved.
- No untraceable high-impact fact or calculation reaches the UI.
- Documentation and examples match the implementation.
- A human teammate has reviewed the PR.
