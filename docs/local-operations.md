# Local operations (Release 0 foundation)

## Start/stop

- `bash scripts/dev_start.sh` starts PostgreSQL, applies migrations, and starts API, Learn, and Studio services.
- `bash scripts/dev_redeploy.sh` recreates PostgreSQL, applies migrations, and recreates API, Learn, and Studio while preserving the database volume.
- `bash scripts/dev_stop.sh` stops all services.

## Migration and seed

- `bash scripts/dev_migrate.sh` runs Alembic migration head application.
- `bash scripts/dev_seed.sh` runs deterministic fixture seeding placeholders for later phases.

## Health and smoke checks

- `bash scripts/dev_health.sh` probes health endpoints and key route shells.

## Recovery and maintenance

- `bash scripts/foundation_quality.sh` runs baseline quality gates.
- `bash scripts/db_backup_restore.sh backup` creates a PostgreSQL dump.
- `bash scripts/db_backup_restore.sh restore <file>` restores from backup.
- `bash scripts/db_backup_restore.sh reset` recreates stack data by removing local volumes.

## Notes

- API readiness is not marked healthy when database migration checks fail.
- Backup/restore applies only to PostgreSQL data; browser-local progress is intentionally not stored there.
