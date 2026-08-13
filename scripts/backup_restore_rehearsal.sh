#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"
export LOCAL_UID=${LOCAL_UID:-$(id -u)}
export LOCAL_GID=${LOCAL_GID:-$(id -g)}

project=${IOAI_RECOVERY_COMPOSE_PROJECT:-ioai-r0-recovery}
source_database=ioai_recovery_source
restore_database=ioai_restore_verify
if [[ "$project" != ioai-r0-recovery ]]; then
  printf 'Refusing non-disposable recovery project: %s\n' "$project" >&2
  exit 1
fi

work_dir=$(mktemp -d)
backup_file="$work_dir/release-0.dump"
compose=(docker compose -p "$project" -f docker-compose.yml -f docker-compose.recovery.yml)
cleanup() {
  "${compose[@]}" down --volumes --remove-orphans >/dev/null 2>&1 || true
  rm -rf -- "$work_dir"
}
trap cleanup EXIT

printf 'Starting isolated recovery source database\n'
"${compose[@]}" down --volumes --remove-orphans
"${compose[@]}" up -d --wait postgres
"${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync alembic -c backend/alembic.ini upgrade head"
"${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync python backend/scripts/sync_vocabulary.py"
"${compose[@]}" up -d --wait api

printf 'Creating representative revision, snapshot, learner, and assessment history\n'
API_BASE_URL=http://127.0.0.1:58010/api/v1 \
  pnpm exec playwright test frontend/tests/e2e/backup-restore-fixture.spec.ts \
    --project=chromium

table_fingerprints() {
  local database=$1
  local table
  for table in \
    alembic_version \
    vocabulary_record \
    problem \
    problem_revision \
    editorial_transition \
    published_snapshot \
    learner_attempt \
    problem_feedback \
    assessment_decision; do
    "${compose[@]}" exec -T postgres psql -U ioai -d "$database" -Atc \
      "SELECT '${table}|' || count(*) || '|' || md5(coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text)::text, '[]')) FROM ${table} AS t"
  done
}

source_fingerprints=$(table_fingerprints "$source_database")
printf '%s\n' "$source_fingerprints"
grep -Eq '^vocabulary_record\|343\|' <<<"$source_fingerprints"
grep -Eq '^problem\|1\|' <<<"$source_fingerprints"
grep -Eq '^problem_revision\|2\|' <<<"$source_fingerprints"
grep -Eq '^published_snapshot\|2\|' <<<"$source_fingerprints"
grep -Eq '^learner_attempt\|1\|' <<<"$source_fingerprints"
grep -Eq '^problem_feedback\|1\|' <<<"$source_fingerprints"
grep -Eq '^assessment_decision\|2\|' <<<"$source_fingerprints"

printf 'Creating logical backup and restoring only to %s\n' "$restore_database"
"${compose[@]}" exec -T postgres pg_dump \
  --format=custom --no-owner --no-privileges \
  --username=ioai --dbname="$source_database" >"$backup_file"
test -s "$backup_file"
existing=$("${compose[@]}" exec -T postgres psql -U ioai -d postgres -Atc \
  "SELECT 1 FROM pg_database WHERE datname = '${restore_database}'")
test -z "$existing"
"${compose[@]}" exec -T postgres createdb -U ioai "$restore_database"
"${compose[@]}" exec -T postgres pg_restore \
  --exit-on-error --no-owner --no-privileges \
  --username=ioai --dbname="$restore_database" <"$backup_file"

restore_fingerprints=$(table_fingerprints "$restore_database")
test "$source_fingerprints" = "$restore_fingerprints"
"${compose[@]}" exec -T postgres dropdb -U ioai "$restore_database"
remaining=$("${compose[@]}" exec -T postgres psql -U ioai -d postgres -Atc \
  "SELECT 1 FROM pg_database WHERE datname = '${restore_database}'")
test -z "$remaining"
printf 'Backup/restore fingerprints match and disposable target was removed.\n'
