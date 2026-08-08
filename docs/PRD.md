# Money Lens MVP Product Requirements

## 1. Purpose

Money Lens helps a person understand material financial-product conditions before enrollment. It converts a curated PDF or image into evidence-linked facts, deterministic money scenarios, adaptive explanations, an understanding check, and a one-page review report.

It does not decide whether a product is good, recommend enrollment, determine eligibility, or replace a qualified professional.

## 2. Competition Outcome

The demo succeeds when a reviewer can complete one credible end-to-end flow in under four minutes and observe all of the following:

- A real-looking source document is processed.
- A material condition is linked to its exact evidence.
- A money result changes when a user input changes.
- Three explanation modes preserve the same underlying facts.
- A wrong or unsure answer triggers targeted re-explanation.
- A report separates confirmed facts, assumptions, and review items.

## 3. Target Users

Primary competition persona:

> A first-time or low-confidence financial customer who can read a document but struggles to translate clauses into personal consequences.

Accessibility needs include older age, limited financial vocabulary, non-native language, low vision, screen-reader use, cognitive load, and preference for concrete examples.

The MVP must not infer a disability or intelligence level. Users select an explanation mode directly.

## 4. Scope Priority

### P0 — Demo-critical

- One fully validated fixed-term deposit document and two additional deposit fixtures.
- PDF and image input, with a preloaded fallback if live processing fails.
- Extraction of principal protection, deposit insurance, preferential-rate requirements, maturity, base rate, and early termination conditions.
- Evidence link for every displayed condition.
- `critical`, `caution`, `confirmed`, and `needs_review` states.
- Plain Language, Number-First, and Example-First modes.
- One deterministic scenario: interest lost when a fixed-term deposit is terminated early.
- Three understanding questions with targeted re-explanation.
- Printable HTML one-page report.
- Keyboard navigation, text scaling, visible focus, and screen-reader labels.

### P1 — Include when P0 is stable

- Loan interest-rate increase and monthly-payment simulation.
- Insurance exclusion or reduced-benefit extraction.
- Ten curated documents across deposits, loans, and insurance.
- Optional browser text-to-speech.
- Multilingual presentation for one selected language.

### P2 — Explicitly deferred

- Bank account, open-banking, or MyData integration.
- Product comparison, ranking, or recommendation.
- Real enrollment or transaction execution.
- Credit, suitability, or eligibility scoring.
- Production ingestion of arbitrary customer documents.
- Automated professional or regulatory conclusions.

## 5. Functional Requirements

### FR-1 Document intake

- Accept PDF, PNG, and JPEG within a configured size limit.
- Validate file signature and media type; do not trust the extension alone.
- Display processing state and a recoverable failure state.
- Preserve page and source coordinates through the pipeline.

### FR-2 Structured facts

- Normalize values, units, dates, rates, and product type.
- Attach confidence and one or more source references to every fact.
- Reject or mark missing, ambiguous, and conflicting required fields.
- Never render a high-impact fact without evidence.

### FR-3 Risk review

- Apply versioned deterministic rules to verified facts.
- Show severity, user impact, matched rule, and evidence.
- Use `needs_review` when evidence does not support a definitive result.

### FR-4 Explanation modes

- Produce three presentations from the same verified fact set.
- Plain Language minimizes terminology and sentence length.
- Number-First surfaces amounts, rates, dates, and deltas before prose.
- Example-First starts with a concrete scenario and then explains the clause.
- Mode changes must not alter numbers, severity, or fact status.

### FR-5 Money scenario

- Accept explicit user inputs with units and validation.
- P0 accepts principal, opening date, and early-termination date.
- Run a deterministic, versioned formula.
- Display inputs, assumptions, formula description, rounding, and result.
- The LLM may explain the stored result but may not calculate or replace it.
- Do not enable the authoritative P0 calculation until the source product's
  elapsed-month and annual day-count definitions have official, independently
  reviewed evidence.

### FR-6 Understanding check

- Ask three short questions prioritizing the highest-impact conditions.
- Accept `unsure` as a valid, non-penalized learning signal.
- On incorrect or unsure answers, explain the same evidence using a simpler or alternate mode and check again.
- Describe the score as a learning aid only.

### FR-7 One-page report

- Include confirmed facts, unresolved items, money scenarios, questions to ask, and a pre-enrollment checklist.
- Clearly label source, assumption, formula version, and generation time.
- Include the decision-support disclaimer.

## 6. Non-Functional Requirements

- Traceability: 100% of displayed high-impact facts and results have evidence, rule, or formula provenance.
- Safety: no definitive answer is produced from low-confidence or conflicting evidence.
- Accessibility: target WCAG 2.2 AA for the demo path.
- Privacy: curated or synthetic documents only; no real customer PII.
- Public demo access: anonymous sessions with explicit per-session, per-IP,
  concurrency, retention, budget, and kill-switch limits.
- Reliability: the demo can fall back to preprocessed fixtures without fabricating a live result.
- Performance target: preprocessed fixture opens within two seconds; live processing exposes progress and completes within the 60-second demo timeout.

## 7. Release Gate

P0 is releasable only when all six README demo-success criteria pass on the primary golden document and the demo can be repeated twice from a clean browser session without manual data repair.
