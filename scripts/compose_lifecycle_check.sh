#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32"* ]]; then
  export LOCAL_UID=${LOCAL_UID:-1000}
  export LOCAL_GID=${LOCAL_GID:-1000}
else
  export LOCAL_UID=${LOCAL_UID:-$(id -u)}
  export LOCAL_GID=${LOCAL_GID:-$(id -g)}
fi

project=${IOAI_SYSTEM_COMPOSE_PROJECT:-ioai-r0-system}
source_ref=${IOAI_SYSTEM_SOURCE_REF:-HEAD}
if [[ "$project" != ioai-r0-system ]]; then
  printf 'Refusing non-disposable Compose project: %s\n' "$project" >&2
  exit 1
fi
if ! git cat-file -e "${source_ref}^{commit}" 2>/dev/null; then
  printf 'System source ref is not a commit: %s\n' "$source_ref" >&2
  exit 1
fi

system_dir=$(mktemp -d)
readiness_file="$system_dir/readiness.json"
compose=(docker compose -p "$project" -f "$system_dir/docker-compose.yml" -f "$system_dir/docker-compose.system.yml")
cleanup() {
  "${compose[@]}" down --volumes --remove-orphans >/dev/null 2>&1 || true
  rm -rf -- "$system_dir"
}
trap cleanup EXIT

printf 'Exporting clean system source from %s\n' "$source_ref"
git archive "$source_ref" | tar -x -C "$system_dir"

printf 'Removing only the validated disposable project and volumes\n'
existing_projects=$(docker compose ls --format json)
if grep -q '"Name":"ioai-training-platform"' <<<"$existing_projects"; then
  printf 'Development project detected and left untouched.\n'
fi
"${compose[@]}" down --volumes --remove-orphans

printf 'Verifying frozen dependency installation from committed locks\n'
(cd "$system_dir" && UV_PROJECT_ENVIRONMENT="$system_dir/.venv-system" uv sync --frozen --all-groups)
(cd "$system_dir" && CI=true pnpm install --frozen-lockfile)

printf 'Starting fresh PostgreSQL, then explicitly migrating and synchronizing\n'
"${compose[@]}" up -d --wait postgres
"${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync alembic -c backend/alembic.ini upgrade head"
"${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync python backend/scripts/sync_vocabulary.py"
"${compose[@]}" up -d --wait api learn studio

curl -fsS http://127.0.0.1:58000/health/ready >/dev/null
curl -fsS http://127.0.0.1:53000/problems >/dev/null
curl -fsS http://127.0.0.1:53001/author/problems >/dev/null

printf 'Creating public, author, feedback, attempt, and assessment records\n'
(
  cd "$system_dir"
  API_BASE_URL=http://127.0.0.1:58000/api/v1 \
  LEARN_BASE_URL=http://127.0.0.1:53000 \
  STUDIO_BASE_URL=http://127.0.0.1:53001 \
    pnpm exec playwright test frontend/tests/e2e/compose-lifecycle.spec.ts \
      --project=chromium
)

database_counts() {
  "${compose[@]}" exec -T postgres psql -U ioai -d ioai -Atc \
    "SELECT json_build_object(
      'vocabulary', (SELECT count(*) FROM vocabulary_record),
      'problems', (SELECT count(*) FROM problem),
      'revisions', (SELECT count(*) FROM problem_revision),
      'snapshots', (SELECT count(*) FROM published_snapshot),
      'attempts', (SELECT count(*) FROM learner_attempt),
      'feedback', (SELECT count(*) FROM problem_feedback),
      'decisions', (SELECT count(*) FROM assessment_decision)
    )::text"
}
before_counts=$(database_counts)
printf 'Counts before restart: %s\n' "$before_counts"

printf 'Stopping without deleting data, then restarting through explicit operations\n'
"${compose[@]}" stop
"${compose[@]}" up -d --wait postgres
"${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync alembic -c backend/alembic.ini upgrade head"
"${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync python backend/scripts/sync_vocabulary.py"
"${compose[@]}" up -d --wait api learn studio
after_counts=$(database_counts)
printf 'Counts after restart: %s\n' "$after_counts"
test "$before_counts" = "$after_counts"
curl -fsS http://127.0.0.1:58000/api/v1/problems/compose-lifecycle-persisted \
  | grep -q 'compose-lifecycle-persisted'
curl -fsS 'http://127.0.0.1:58000/api/v1/author/assessments?status=ASSESSED&problem=compose-lifecycle-persisted' \
  | grep -q 'compose-lifecycle-persisted'

printf 'Injecting a disposable unknown migration revision\n'
head_revision=$("${compose[@]}" exec -T postgres psql -U ioai -d ioai -Atc \
  'SELECT version_num FROM alembic_version')
test -n "$head_revision"
"${compose[@]}" exec -T postgres psql -U ioai -d ioai -v ON_ERROR_STOP=1 -c \
  "UPDATE alembic_version SET version_num = 'missing_system_revision'" >/dev/null
if "${compose[@]}" run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync alembic -c backend/alembic.ini upgrade head"; then
  printf 'Expected the injected migration state to fail.\n' >&2
  exit 1
fi
"${compose[@]}" up -d --force-recreate --no-deps api
for _ in $(seq 1 30); do
  readiness_code=$(curl -sS -o "$readiness_file" -w '%{http_code}' \
    http://127.0.0.1:58000/health/ready || true)
  if [[ "$readiness_code" == 503 ]]; then break; fi
  sleep 1
done
test "$readiness_code" = 503
grep -q 'not_ready' "$readiness_file"
if grep -Eqi 'postgresql|password|traceback|sqlalchemy|/app/' "$readiness_file"; then
  printf 'Degraded readiness leaked infrastructure details.\n' >&2
  exit 1
fi

printf 'Restoring the disposable schema marker and readiness\n'
"${compose[@]}" exec -T postgres psql -U ioai -d ioai -v ON_ERROR_STOP=1 -c \
  "UPDATE alembic_version SET version_num = '${head_revision}'" >/dev/null
"${compose[@]}" up -d --force-recreate --wait api learn studio
curl -fsS http://127.0.0.1:58000/health/ready >/dev/null

printf 'Validating isolated topology and Release 0 service exclusions\n'
rendered=$("${compose[@]}" config)
test "$("${compose[@]}" port api 8000)" = '127.0.0.1:58000'
test "$("${compose[@]}" port postgres 5432)" = '127.0.0.1:55432'
test "$("${compose[@]}" port studio 3001)" = '127.0.0.1:53001'
grep -q 'http://api:8000' <<<"$rendered"
if grep -Eqi '^  (redis|celery|docling|minio|vector|gpu):' <<<"$rendered"; then
  printf 'Out-of-scope infrastructure appeared in Release 0 Compose.\n' >&2
  exit 1
fi
for required_key in \
  IOAI_DATABASE_URL \
  IOAI_ALLOWED_ORIGINS \
  IOAI_ENVIRONMENT \
  API_INTERNAL_BASE \
  IOAI_TEST_DATABASE_URL; do
  grep -q "^${required_key}=" "$system_dir/.env.example"
done

printf 'Compose clean/persisted lifecycle check passed.\n'
