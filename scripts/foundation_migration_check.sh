#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR

uv run --group backend python backend/scripts/check_alembic_head.py
printf 'Alembic head check passed\n'
