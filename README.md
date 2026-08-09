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

## Baseline release commands

- Python:
  - `uv sync --all-groups`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run pyright`
  - `bash scripts/backend_test.sh` (isolated PostgreSQL test environment)
- Frontend:
  - `pnpm install --frozen-lockfile`
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - `pnpm test:e2e`
  - `pnpm build`
- Foundation scripts:
  - `bash scripts/foundation_quality.sh`
  - `bash scripts/foundation_migration_check.sh`
  - `bash scripts/backend_test.sh`
  - `bash scripts/phase7_quality.sh`
  - `bash scripts/test_editorial_e2e.sh`
  - `bash scripts/public_isolation_check.sh`
  - `bash scripts/dev_start.sh`
  - `bash scripts/dev_redeploy.sh`
  - `bash scripts/dev_stop.sh`
  - `bash scripts/dev_migrate.sh`
  - `bash scripts/dev_seed.sh`
  - `bash scripts/dev_health.sh`
  - `bash scripts/generate_contracts.sh`
  - `bash scripts/openapi_drift_check.sh`
  - `bash scripts/vocabulary_drift_check.sh`
  - `bash scripts/db_backup_restore.sh <backup|restore|reset>`

## Setup status

The executable foundation and canonical vocabulary vertical slice are
implemented. The vocabulary APIs and generated packages are foundations for the
author editor in Phase 6 and learner discovery UI in Phase 7; Phase 5 does not
claim those screens are complete.
