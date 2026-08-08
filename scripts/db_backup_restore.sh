#!/usr/bin/env bash
set -euo pipefail

set +u
ACTION=${1:-help}
set -u

if [ "$ACTION" = "backup" ]; then
  printf 'Backing up PostgreSQL to backups/ioai-release0-$(date +%Y%m%d%H%M%S).sql\n'
  mkdir -p backups
  docker compose exec -T postgres pg_dump -U ioai ioai > "backups/ioai-release0-$(date +%Y%m%d%H%M%S).sql"
  exit 0
fi

if [ "$ACTION" = "restore" ]; then
  BACKUP_FILE="$2"
  printf 'Restoring PostgreSQL from %s\n' "$BACKUP_FILE"
  docker compose exec -T postgres psql -U ioai ioai < "$BACKUP_FILE"
  exit 0
fi

if [ "$ACTION" = "reset" ]; then
  printf 'Resetting local stack explicitly\n'
  docker compose down -v
  docker compose up -d
  exit 0
fi

cat <<'USAGE'
Usage: db_backup_restore.sh [backup|restore <file>|reset]
USAGE
exit 1
