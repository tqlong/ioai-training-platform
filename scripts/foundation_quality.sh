#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR

printf 'Running backend quality gates\n'
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest

printf 'Running frontend quality gates\n'
pnpm lint
pnpm typecheck
pnpm test

printf 'Generating OpenAPI contract\n'
UV_CACHE_DIR="$UV_CACHE_DIR" python3 backend/scripts/dump_openapi.py

printf 'Checking alembic head\n'
python3 backend/scripts/check_alembic_head.py
