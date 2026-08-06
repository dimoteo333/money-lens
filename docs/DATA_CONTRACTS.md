# Data Contracts and Provenance

## 1. Contract Goals

The data model must make it difficult to display an unsupported financial claim. Facts, risks, calculations, explanations, questions, and reports all reference the same immutable review snapshot.

The machine-readable starting point is `schemas/product-facts.schema.json`.

## 2. Core Entities

| Entity | Purpose | Required provenance |
|---|---|---|
| `Document` | Source metadata and retention state | Hash, media type, received time, deletion deadline |
| `SourceReference` | Evidence within a document | Page, exact excerpt, and coordinates when available |
| `ProductFact` | Normalized condition | Value, unit, confidence, status, source references |
| `RiskFinding` | Deterministic rule result | Rule ID/version, matched facts, severity, evidence |
| `CalculationResult` | Authoritative scenario | Formula ID/version, inputs, units, assumptions, rounding, source facts |
| `Explanation` | Mode-specific language | Fact-set hash, referenced findings/results, model metadata |
| `UnderstandingAttempt` | Learning interaction | Question basis, answer, outcome, re-explanation mode |
| `ReviewSnapshot` | Immutable review state | Extraction, schema, rule, and formula versions |

## 3. Fact Status

| Status | Meaning | UI behavior |
|---|---|---|
| `verified` | Evidence and validation support the normalized value | May be used by rules, calculations, and explanations |
| `needs_review` | Low confidence, ambiguity, conflict, or missing evidence | Display uncertainty; exclude from authoritative calculation unless explicitly handled |
| `not_found` | Required condition was not located | State that absence in extraction is not proof of absence |
| `not_applicable` | Condition does not apply to the product type | Explain only when useful |

Confidence is not the same as status. A confidence score alone cannot promote a fact to `verified`; validators and product-specific requirements decide status.

## 3.1 Review Level

Fact status and the user-facing review level are separate contracts.

| Review level | Meaning |
|---|---|
| `critical` | A supported condition may cause major loss or remove expected protection |
| `caution` | The user impact depends on timing, eligibility, or another supported condition |
| `confirmed` | A protection or material condition is clearly established |
| `needs_review` | Evidence does not support a definitive review level |

A `verified` fact can contribute to a deterministic `critical`, `caution`, or
`confirmed` finding. A fact with status `needs_review` cannot be converted into
a definitive finding by explanation text.

## 4. Numeric Rules

- Store money as decimal strings with explicit ISO currency, never binary floating point.
- Store rates as decimal strings with explicit basis and period.
- Store dates as ISO 8601 dates and timestamps as UTC.
- Never mix days, months, and years without an explicit conversion assumption.
- Every calculation defines rounding timing and method.
- UI formatting must not change stored values.

## 5. Source Reference Requirements

Each displayed high-impact fact requires:

- `document_id`
- 1-indexed `page`
- exact `excerpt`
- character offsets or bounding box when available
- OCR confidence when OCR was used

The excerpt is evidence for the user, not a license for the model to infer unrelated meaning.

## 6. Review Snapshot

A snapshot records:

```text
document hash
+ extraction model/prompt version
+ product schema version
+ normalized facts
+ rule-set version
+ available formula versions
= review snapshot ID
```

Reprocessing creates a new snapshot. Existing reports and understanding attempts continue to point to the snapshot they used.

## 7. Example Fact

```json
{
  "id": "fact-preferential-rate",
  "type": "preferential_rate",
  "status": "verified",
  "value": {
    "kind": "rate",
    "decimal": "0.01",
    "period": "annual"
  },
  "confidence": 0.94,
  "source_refs": [
    {
      "document_id": "doc-123",
      "page": 2,
      "excerpt": "All preferential conditions add up to 1.0%p per year.",
      "bbox": [0.12, 0.38, 0.84, 0.44]
    }
  ]
}
```
