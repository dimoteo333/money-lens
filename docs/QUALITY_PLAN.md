# Quality and Evaluation Plan

## 1. Quality Priorities

1. Material-fact recall and source traceability.
2. Calculation correctness.
3. Honest uncertainty.
4. Consistency across explanation modes.
5. Accessibility and demo reliability.

Fluent wording is not evidence of quality.

## 2. Golden Dataset

Create versioned fixtures under a private or licensed data location. Repository metadata may describe them, but do not commit restricted documents.

For every golden document store:

- Document ID, product type, license/source, and synthetic/real-looking status.
- Expected sections and high-impact facts.
- Exact evidence page and excerpt.
- Expected fact status, rule finding, and simulation availability.
- Known ambiguity and expected `needs_review` behavior.

Start with three deposit fixtures. Expand only after the primary demo fixture passes reliably.

## 3. Required Automated Tests

### Contracts

- Schema accepts valid product facts.
- Missing evidence rejects a verified high-impact fact.
- Invalid units, dates, currencies, and rate representations fail validation.

### Rules

- Each rule has positive, negative, boundary, missing-data, and conflicting-data cases.
- Matched results include rule ID/version and source fact IDs.

### Calculations

- Normal, zero, minimum/maximum, invalid, rounding, and unit-conversion cases.
- Expected results are independently calculated and stored as fixtures.
- No model call is reachable from calculation functions.

### Explanations

- Generated claims are limited to the supplied fact/result identifiers.
- All numbers in an explanation match authoritative inputs or results.
- Mode changes do not alter fact status, severity, or numeric values.

### End to end

- Primary deposit fixture completes upload-to-report.
- OCR/model failure produces an explicit state and safe fallback.
- Deleting a document makes its source unavailable.
- Cross-session access is denied.

## 4. MVP Metrics and Gates

| Metric | P0 release gate |
|---|---|
| High-impact fact source coverage | 100% |
| Authoritative calculation provenance | 100% |
| Primary golden document critical-fact recall | 100% |
| Unsupported definitive claims in golden run | 0 |
| Cross-mode fact/number inconsistencies | 0 |
| Formula unit tests | 100% pass |
| Demo flow repeatability | 2 consecutive clean runs |
| Keyboard-only critical blockers | 0 |

These gates apply to the curated competition set; they are not claims of general production accuracy.

## 5. Human Review Rubric

Reviewers mark each output:

- `supported`: directly supported by evidence or deterministic output.
- `partially_supported`: wording overstates or loses a condition.
- `unsupported`: introduces a new claim, number, guarantee, or recommendation.
- `needs_review_handled`: uncertainty is correctly surfaced.
- `needs_review_missed`: ambiguous evidence is presented as definitive.

Every `unsupported` or `needs_review_missed` result blocks the primary demo fixture.

## 6. Demo-Day Verification

- Pin model, prompts, schemas, rules, and formulas.
- Save safe hashes and versions, not full sensitive prompts or documents, in logs.
- Test external-provider quota and failure responses.
- Verify fallback fixtures use the same data contract.
- Confirm report labels generation time and all assumptions.
