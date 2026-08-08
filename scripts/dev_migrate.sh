#!/usr/bin/env bash
set -euo pipefail

printf 'Running alembic upgrade head\n'
if [ ! -f "backend/alembic.ini" ]; then
  echo "Alembic config not found" >&2
  exit 1
fi

docker compose run --rm api bash -lc "uv run alembic -c backend/alembic.ini upgrade head"
