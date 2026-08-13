#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"

action=${1:-help}
active_database=ioai
expected_volume=ioai-training-platform_postgres-data

is_disposable_database() {
  [[ "$1" =~ ^ioai_restore_[a-z0-9_]+$ ]]
}

if [[ "$action" == backup ]]; then
  output=${2:-"backups/ioai-release0-$(date -u +%Y%m%dT%H%M%SZ).dump"}
  if [[ -e "$output" ]]; then
    printf 'Refusing to overwrite backup: %s\n' "$output" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$output")"
  partial="${output}.partial.$$"
  trap 'rm -f -- "$partial"' EXIT
  umask 077
  docker compose exec -T postgres pg_dump \
    --format=custom --no-owner --no-privileges \
    --username=ioai --dbname="$active_database" >"$partial"
  mv "$partial" "$output"
  trap - EXIT
  printf 'Created PostgreSQL backup: %s\n' "$output"
  exit 0
fi

if [[ "$action" == restore ]]; then
  backup_file=${2:-}
  target_database=${3:-}
  confirmation=${4:-}
  if ! is_disposable_database "$target_database"; then
    printf 'Refusing non-disposable restore target: %s\n' "${target_database:-<missing>}" >&2
    exit 1
  fi
  if [[ "$confirmation" != "--confirm-database=${target_database}" ]]; then
    printf 'Restore requires --confirm-database=%s\n' "$target_database" >&2
    exit 1
  fi
  if [[ ! -f "$backup_file" ]]; then
    printf 'Backup file does not exist: %s\n' "${backup_file:-<missing>}" >&2
    exit 1
  fi
  exists=$(docker compose exec -T postgres psql -U ioai -d postgres -Atc \
    "SELECT 1 FROM pg_database WHERE datname = '${target_database}'")
  if [[ "$exists" == 1 ]]; then
    printf 'Refusing to overwrite existing database: %s\n' "$target_database" >&2
    exit 1
  fi
  docker compose exec -T postgres createdb -U ioai "$target_database"
  if ! docker compose exec -T postgres pg_restore \
    --exit-on-error --no-owner --no-privileges \
    --username=ioai --dbname="$target_database" <"$backup_file"; then
    docker compose exec -T postgres dropdb -U ioai --if-exists "$target_database"
    exit 1
  fi
  printf 'Restored only into disposable database: %s\n' "$target_database"
  exit 0
fi

if [[ "$action" == drop-restore ]]; then
  target_database=${2:-}
  confirmation=${3:-}
  if ! is_disposable_database "$target_database"; then
    printf 'Refusing non-disposable restore target: %s\n' "${target_database:-<missing>}" >&2
    exit 1
  fi
  if [[ "$confirmation" != "--confirm-database=${target_database}" ]]; then
    printf 'Drop requires --confirm-database=%s\n' "$target_database" >&2
    exit 1
  fi
  docker compose exec -T postgres dropdb -U ioai --if-exists "$target_database"
  printf 'Dropped disposable restore database: %s\n' "$target_database"
  exit 0
fi

if [[ "$action" == reset ]]; then
  target_volume=${2:-}
  confirmation=${3:-}
  if [[ "$target_volume" != "$expected_volume" ]] \
    || [[ "$confirmation" != "--confirm-volume=${expected_volume}" ]]; then
    printf 'Reset requires explicit volume confirmation: %s --confirm-volume=%s\n' \
      "$expected_volume" "$expected_volume" >&2
    exit 1
  fi
  container_id=$(docker compose ps -q postgres)
  if [[ -z "$container_id" ]]; then
    printf 'PostgreSQL container is not running; refusing unresolved reset.\n' >&2
    exit 1
  fi
  mounted_volume=$(docker inspect "$container_id" --format \
    '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}')
  if [[ "$mounted_volume" != "$expected_volume" ]]; then
    printf 'Resolved PostgreSQL volume does not match confirmation: %s\n' "$mounted_volume" >&2
    exit 1
  fi
  docker compose down
  docker volume rm "$expected_volume"
  bash scripts/dev_start.sh
  printf 'Reset and reinitialized confirmed development volume: %s\n' "$expected_volume"
  exit 0
fi

cat <<'USAGE'
Usage:
  db_backup_restore.sh backup [backups/name.dump]
  db_backup_restore.sh restore <file.dump> <ioai_restore_name> --confirm-database=<ioai_restore_name>
  db_backup_restore.sh drop-restore <ioai_restore_name> --confirm-database=<ioai_restore_name>
  db_backup_restore.sh reset ioai-training-platform_postgres-data --confirm-volume=ioai-training-platform_postgres-data
USAGE
exit 1
