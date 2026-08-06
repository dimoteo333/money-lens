# ADR-0002: Evidence-First Facts and Explicit Uncertainty

- Status: Accepted
- Date: 2026-08-06

## Context

Document extraction may fail because of OCR errors, complex layout, missing clauses, ambiguous wording, or conflicting sections. A confidence score does not make an unsupported claim safe.

## Decision

Every displayed high-impact fact must have a source reference. Facts are validated into explicit statuses. Low-confidence, missing-evidence, ambiguous, or conflicting facts become `needs_review` or `not_found`; they are not silently inferred.

Risk findings store matched rule and fact IDs. Reports separate verified facts, assumptions, and review items.

## Consequences

- Some documents produce incomplete answers, which is expected behavior.
- The UI must make source evidence and uncertainty usable rather than hiding them.
- Golden tests prioritize material-fact recall and unsupported-claim prevention over prose quality.
