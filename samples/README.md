# Sample Document Policy

Do not commit real customer or confidential financial documents.

Allowed samples:

- Fully synthetic documents created for Money Lens.
- Public-domain or openly licensed documents with the license recorded.
- Documents whose owner explicitly authorized this use and redistribution.
- Derived text fixtures that contain no personal data and respect source rights.

For every sample, record in a sibling metadata file:

```yaml
id: deposit-primary-001
product_type: deposit
source_type: synthetic
license: project-owned
contains_pii: false
purpose: primary-demo-golden-fixture
expected_review_snapshot: tests/fixtures/deposit-primary-001.expected.json
```

The P0 set should begin with three deposits: primary happy path, poor OCR/layout case, and ambiguous/conflicting-clause case.

## P0 reference source

- Product: Shinhan SOLmate fixed-term deposit
- Version date: 2026-06-15
- Public reference URL: `https://img.shinhan.com/sbank2016/seol/20260114000000090003LC000030.PDF?1781450435777`
- Repository policy: reference metadata only; do not commit or redistribute the original PDF.
- P0 scenario: early-termination interest.
- Blocking verification: the official elapsed-month definition and annual day-count denominator, including leap years.

Public accessibility is not proof of redistribution permission. A future
committed golden document must be synthetic, openly licensed, or explicitly
authorized, with its license recorded.
