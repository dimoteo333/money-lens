# Demo Release Checklist

## Scope and Evidence

- [ ] P0 primary deposit flow passes; no P1 item is required for the demo.
- [ ] Every displayed high-impact fact opens the correct source page and excerpt.
- [ ] Ambiguous fixture content is labeled `needs_review`.
- [ ] No recommendation, eligibility decision, or guaranteed outcome appears.

## Rules and Calculations

- [ ] Rule IDs/versions and matched facts are stored.
- [ ] Formula IDs/versions, inputs, units, assumptions, and rounding are visible.
- [ ] Primary scenario is independently recalculated and matches the UI.
- [ ] LLM/model access is absent from authoritative calculation code paths.

## Experience

- [ ] Plain, Number-First, and Example-First modes preserve facts and numbers.
- [ ] Incorrect and unsure answers both trigger appropriate re-explanation.
- [ ] One-page report separates facts, assumptions, and review items.
- [ ] Keyboard-only, screen-reader, 200% zoom, and mobile checks pass.

## Security and Operations

- [ ] Only synthetic/authorized documents are present.
- [ ] Secrets are outside repository, browser bundles, and logs.
- [ ] File limits, rate limits, retention, deletion, budget alerts, and kill switch are tested.
- [ ] Demo resources have owner and expiration tags.
- [ ] Product deployment works without QM.

## Reliability

- [ ] Live processing path is healthy.
- [ ] Labeled preprocessed fallback is tested.
- [ ] Two clean end-to-end rehearsals pass from fresh browser sessions.
- [ ] Release commit is tagged and all relevant versions are recorded.
- [ ] Rollback and post-competition teardown steps are known.
