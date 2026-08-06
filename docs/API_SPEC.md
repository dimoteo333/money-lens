# Initial API Contract

Status: Draft. The transport may change, but safety and provenance fields are required.

## Conventions

- Base path: `/v1`
- IDs are opaque UUIDs.
- Timestamps use UTC ISO 8601.
- Rates use decimal fractions in storage (`0.035` means 3.5%) and explicitly named display units.
- Money includes ISO currency.
- Every error has `code`, `message`, `request_id`, and optional safe `details`.
- Document text and secrets must never appear in operational error logs.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness without provider or secret details |
| `POST` | `/v1/documents` | Upload a supported document and return processing ID |
| `GET` | `/v1/documents/{document_id}` | Read safe metadata and processing state |
| `GET` | `/v1/documents/{document_id}/review` | Get verified facts, risks, evidence, and available simulations |
| `POST` | `/v1/documents/{document_id}/simulations/{simulation_id}` | Run a deterministic scenario |
| `POST` | `/v1/documents/{document_id}/checks` | Start an understanding check from the review snapshot |
| `POST` | `/v1/checks/{check_id}/answers` | Submit an answer and receive targeted feedback |
| `POST` | `/v1/documents/{document_id}/reports` | Create a report from an immutable review snapshot |
| `DELETE` | `/v1/documents/{document_id}` | Delete document and derived user data where permitted |

## Example: Simulation Request

```json
{
  "review_snapshot_id": "6ff4b20a-5052-4bb8-870b-9fc8f89a8748",
  "inputs": {
    "principal": { "value": "10000000", "currency": "KRW" },
    "opened_on": "2026-06-15",
    "early_termination_on": "2026-12-15"
  }
}
```

The planned P0 simulation ID is `deposit-early-termination-interest`. Its
authoritative response contract and independently calculated expected fixture
must not be finalized until the bank's elapsed-month and annual day-count
definitions are verified.

Until that verification is complete, the API must fail closed rather than infer
a financial result:

```json
{
  "code": "calculation_contract_pending",
  "message": "The authoritative early-termination formula is not yet verified.",
  "request_id": "b479b8bc-b20b-4ea0-95dc-23f1f562cc7f",
  "details": {
    "simulation_id": "deposit-early-termination-interest",
    "fact_status": "needs_review"
  }
}
```

## Processing States

`uploaded → parsing → extracting → validating → ready`

Terminal or partial states:

- `failed`: no trustworthy review can be produced.
- `partial`: some sections are usable; affected facts are `needs_review`.
- `expired`: source and derived session data passed retention.

Clients must not infer readiness from elapsed time.
