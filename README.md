# IOAI Training Platform — Release 0

This repository is governed by:

- [AGENTS.md](AGENTS.md)
- [master_plan.md](master_plan.md)
- [ui_release_0.md](ui_release_0.md)
- [vocab.md](vocab.md)
- [code_standard.md](code_standard.md)
- [plan_release_0.md](plan_release_0.md)

Release 0 is an editorial pilot where authors draft/review/approve/publish
problems and learners browse and solve only published problems.

## Planned repository shape

Release 0 keeps a monorepo boundary with separate learner and Studio apps:

```text
backend/
  src/ioai/
    domain/
    application/
    adapters/
    entrypoints/api/
    workers/
  tests/
    unit/
    integration/
  alembic/
frontend/
  apps/
    learn/
    studio/
  packages/
    api-client/
    ui/
    vocabulary/
  tests/e2e/
```

## Local development assumptions

- Python: `3.12+`
- Node: compatible with the Next.js toolchain used by the frontend workspace
- PostgreSQL for all authoritative Release 0 data
- Redis/Celery/Docling/object storage are intentionally out of scope until an
  accepted requirement requires them

## Command policy

Use only managed tool entrypoints for reproducible environments:

- Python environment, dependency management, and Python command execution via
  `uv`
- Frontend dependency and script execution via `pnpm`

Avoid ad hoc global environment scripts when these project-managed tools are
available.

## Setup status

This baseline currently captures Release 0 planning and governance. Code scaffolding
commands may be added as the repository is implemented in later phases.

