# Release 0 Foundation Baseline (Phase 4)

## Scope implemented in this phase

- Executable repository foundations for Python (`uv`) and frontend (`pnpm`).
- Backend package boundaries with API health/openAPI shell and SQLAlchemy/Alembic scaffolding.
- Learner/Studio app shells in separate Next.js apps.
- Shared frontend package placeholders and typed fixtures.
- Docker Compose topology with local PostgreSQL, API, Learn, and Studio services.
- Local operation scripts for start/stop, migration, canonical vocabulary sync,
  health checks, and backup/restore.
- Foundation smoke checks and CI skeleton.

## Deferred until later phases

- Advanced content workflows, scoring implementations, public detail pages, and editorial automations.
- Advanced storage, retrieval, or async execution services.
- Vocabulary-driven author editor controls and learner discovery filters remain
  deferred to Phases 6 and 7; deterministic client generation and drift
  enforcement are implemented in Phase 5.
