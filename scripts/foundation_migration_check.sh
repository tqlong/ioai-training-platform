#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR

python3 -m backend.scripts.check_alembic_head
printf 'Alembic head check passed\n'
