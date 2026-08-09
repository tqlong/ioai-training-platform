# Local operations (Release 0 foundation)

## Start/stop

- `bash scripts/dev_start.sh` starts PostgreSQL, applies migrations, synchronizes
  canonical vocabulary, and starts API, Learn, and Studio services.
- `bash scripts/dev_redeploy.sh` recreates PostgreSQL, applies migrations,
  synchronizes canonical vocabulary, and recreates API, Learn, and Studio while
  preserving the database volume.
- `bash scripts/dev_stop.sh` stops all services.

## Migration and seed

- `bash scripts/dev_migrate.sh` runs Alembic migration head application.
- `bash scripts/dev_seed.sh` validates and idempotently synchronizes the generated
  canonical vocabulary artifact. Repeated runs report records as unchanged.
- `bash scripts/generate_contracts.sh` regenerates deterministic OpenAPI,
  OpenAPI-derived TypeScript, and the frontend canonical vocabulary artifact.
- `bash scripts/openapi_drift_check.sh` verifies all generated contracts and
  frontend vocabulary data are current without changing checked-in files.
- `bash scripts/vocabulary_drift_check.sh` verifies `vocab.md` and the backend
  canonical artifact are synchronized.

## Health and smoke checks

- `bash scripts/dev_health.sh` probes health endpoints, public and author
  vocabulary projections, and key route shells.
- Public canonical vocabulary is available from `GET /api/v1/vocabulary` with a
  required `vocabulary_type`; author-safe values and availability are available
  from `GET /api/v1/author/vocabulary`.
- Missing-value proposals use `POST /api/v1/author/vocabulary/proposals` and are
  reviewable through `GET /api/v1/author/vocabulary/proposals`.

## Recovery and maintenance

- `bash scripts/foundation_quality.sh` runs baseline quality gates.
- `bash scripts/db_backup_restore.sh backup` creates a PostgreSQL dump.
- `bash scripts/db_backup_restore.sh restore <file>` restores from backup.
- `bash scripts/db_backup_restore.sh reset` recreates stack data by removing local volumes.

## Notes

- API readiness is not marked healthy when database migration checks fail.
- Studio is published on host loopback at `127.0.0.1:3001`; this is not
  authentication or production authorization.
- Backup/restore applies only to PostgreSQL data; browser-local progress is intentionally not stored there.
