# First Commit Checklist

Before committing this package:

- [x] Record team ownership in `docs/TEAM_SETUP.md`; Min's GitHub username is intentionally pending.
- [x] Confirm the proposed stack direction in ADR-0003; keep the ADR `Proposed` until its acceptance spike passes.
- [x] Choose the primary deposit reference and P0 early-termination simulation.
- [x] Set the actual upload, retention, processing, rate, and budget limits in `.env.example`.
- [x] Create GitHub labels: `P0`, `P1`, `P2`, `mvp`, `safety`, `accessibility`, `infra`, `bug`.
- [x] Enable PR review and CI checks on `main` when the GitHub plan supports them.
- [x] Create issues from `docs/TASKS.md`, beginning with Milestone 0 only.
- [x] Verify the workflow passes on the empty-code repository.
- [x] Commit with a message such as `chore: establish Money Lens product and agent contracts`.

Do not scaffold application code until the primary fixture, P0 simulation, and ADR-0003 acceptance spike are assigned.
