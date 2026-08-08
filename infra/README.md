# Infrastructure

Infrastructure is managed as code. Use one tool for the product deployment; do not combine unrelated IaC frameworks.

Initial environments:

- `local`: local adapters and synthetic fixtures.
- `demo`: AWS-hosted competition environment.

Required properties:

- CI uses short-lived AWS federation, not stored access keys.
- Raw documents are private, encrypted, and automatically deleted.
- Runtime secrets live in a managed secret store.
- Logs exclude document content and secrets.
- Public processing has rate/spend limits and a kill switch.
- Resources have `Project`, `Environment`, `Owner`, and `ExpiresAt` tags.
- QM infrastructure and state are kept in a separate repository.

Choose the AWS compute and data services only after the walking-skeleton and latency spike described by ADR-0003.
