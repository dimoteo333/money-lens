# ADR-0001: Deterministic Financial Results

- Status: Accepted
- Date: 2026-08-06

## Context

Money Lens presents personalized money scenarios. A fluent but incorrect value could materially mislead a user. General-purpose language models are probabilistic and are not an authoritative calculation engine.

## Decision

All financial values shown as results are produced by versioned, deterministic, tested functions. Each result stores formula ID/version, inputs, units, assumptions, rounding policy, output, and supporting product-fact IDs.

An LLM may explain a stored result but cannot calculate, modify, or replace it. Explanations that contain numbers must be checked against the authoritative input/result set.

## Consequences

- Formulas require more product-specific engineering and fixtures.
- The same inputs and version always produce the same output.
- Incorrect formulas are traceable and can be disabled or superseded.
- Adding a new product simulation requires tests and an explicit formula contract.
