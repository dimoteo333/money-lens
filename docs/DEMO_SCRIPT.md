# Competition Demo Script

## Goal

Demonstrate one trustworthy decision-support flow in approximately three minutes. Do not spend demo time explaining every planned product category.

## Primary Fixture

The reference source is the Shinhan SOLmate fixed-term deposit product description,
version 2026-06-15. The original PDF is local-only and must not be committed or
redistributed from this repository.

The golden annotation must cover:

- 12-month maturity and the applicable base rate.
- Preferential-rate conditions and the rule that the bonus does not apply to early termination.
- Early-termination reduction brackets and the minimum annual rate.
- Exact evidence for the deposit-insurance clause.
- The unresolved elapsed-month and leap-year day-count definitions as `needs_review`
  until official confirmation is independently verified.

## Run of Show

| Time | Action | Proof shown |
|---|---|---|
| 0:00–0:20 | Upload or select the deposit brochure | PDF/image intake and processing status |
| 0:20–0:50 | Open the key-conditions view | Preferential-rate caution, confirmed protection, exact page evidence |
| 0:50–1:20 | Switch Plain → Number-First → Example-First | Wording changes while facts and values remain identical |
| 1:20–1:55 | Enter deposit amount, opening date, and early-termination date | Deterministic interest delta; inputs, assumptions, rounding, and formula version |
| 1:55–2:25 | Answer one material question incorrectly | Targeted re-explanation and respectful re-check |
| 2:25–2:50 | Open the one-page report | Facts, assumptions, unresolved item, questions to ask |
| 2:50–3:00 | Close with guardrail | “Decision support, not product recommendation” |

## Narration Anchor

> Financial disclosure is not the same as financial understanding. Money Lens connects each explanation to source evidence, uses deterministic calculations for money, and checks whether the user understood the conditions that matter.

## Failure Fallbacks

- Live OCR failure: select a visibly labeled preprocessed demo fixture and explain that it preserves the same OCR output contract.
- Model timeout: use cached grounded explanations tied to the same fact-set hash.
- Report download failure: open the printable report route.
- Network failure: run the local demo fixture; do not pretend a live service responded.

## Pre-Demo Checklist

- Use only synthetic, licensed, authorized, or approved local reference documents with no real customer data.
- Warm the demo environment and verify health.
- Clear previous sessions and uploaded files.
- Test keyboard-only flow and browser zoom at 200%.
- Verify every highlighted clause opens the correct page.
- Independently calculate the displayed money scenario.
- Keep a local screen recording as a last-resort submission artifact.
