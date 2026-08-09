#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR

printf 'Running backend quality gates\n'
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest

printf 'Running frontend quality gates\n'
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build

printf 'Checking generated vocabulary and API contracts\n'
bash scripts/vocabulary_drift_check.sh
bash scripts/openapi_drift_check.sh

printf 'Checking alembic head\n'
uv run --group backend python backend/scripts/check_alembic_head.py
