# Two-Person Team Operating Guide

## Shared Systems

- GitHub is the source of truth for code, issues, decisions, and release state.
- Slack is for fast coordination and agent interaction, not final decisions.
- QM is a development accelerator, not a runtime dependency of Money Lens.
- AWS hosts the demo environment; agents submit PRs instead of deploying directly.

Recommended Slack channels:

- `#money-lens-build`: daily work, questions, and QM shared scope.
- `#money-lens-alerts`: CI, deploy, cost, and health notifications.

## Daily Rhythm

1. Ten-minute check: current demo blocker and one outcome per person.
2. Work from GitHub issues with explicit acceptance criteria.
3. Integrate at least once per day; do not let frontend and backend diverge.
4. Review each other’s PRs, especially formula and evidence changes.
5. End with a deployed demo check and updated risk/task state.

## Git Rules

- Short-lived branches and small PRs.
- `main` always deployable.
- One human approval plus CI before squash merge.
- Revert a bad merge rather than repairing production manually.
- Tag the competition release and record schema/rule/formula/model versions.

## Agent Request Pattern

```text
Implement issue #<number> only.
Read AGENTS.md and the linked product documents first.
Restate the acceptance criteria and propose a short plan.
Do not change external contracts or add dependencies without approval.
Run the required checks and open a PR. Do not deploy.
```

Use one agent workspace per issue or branch. Do not let two agents modify the same files concurrently without a human-owned integration plan.

## Ownership

The bootstrap commit records the known GitHub username. Min's username remains
intentionally blank until it is confirmed.

| Area | Primary | Reviewer |
|---|---|---|
| Product scope and demo | Min | Jun (`@dimoteo333`) |
| Accessible web experience | Min | Jun (`@dimoteo333`) |
| Document and extraction pipeline | Jun (`@dimoteo333`) | Min |
| Rules and calculations | Jun (`@dimoteo333`) | Min |
| AWS, CI/CD, security, and cost | Jun (`@dimoteo333`) | Min |

Primary ownership is coordination, not exclusive permission. Critical calculations and safety changes always require the other person’s review.
