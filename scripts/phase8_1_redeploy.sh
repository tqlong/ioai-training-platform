#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32"* ]]; then
  export LOCAL_UID=1000
  export LOCAL_GID=1000
else
  export LOCAL_UID="$(id -u)"
  export LOCAL_GID="$(id -g)"
fi

printf 'Phase 8.1 step 1/6: recreating PostgreSQL without deleting its volume\n'
docker compose up -d --force-recreate --wait postgres

printf 'Phase 8.1 step 2/6: applying Alembic migrations\n'
bash scripts/dev_migrate.sh

printf 'Phase 8.1 step 3/6: synchronizing canonical vocabulary\n'
bash scripts/dev_seed.sh

printf 'Phase 8.1 step 4/6: checking legacy manual-assessment compatibility\n'
docker compose run --rm api bash -lc \
  "PYTHONPATH=/app/backend/src uv run --with sqlalchemy,psycopg[binary] python scripts/manual_assessment_preflight.py"

printf 'Phase 8.1 step 5/6: recreating backend and frontend services\n'
docker pull ghcr.io/astral-sh/uv:python3.12-bookworm-slim
docker pull node:22-bookworm
docker compose up -d --pull never --force-recreate --remove-orphans --wait \
  api learn studio

printf 'Phase 8.1 step 6/6: checking API, Learn, and Studio routes\n'
bash scripts/dev_health.sh
printf 'Phase 8.1 redeploy complete and healthy.\n'
