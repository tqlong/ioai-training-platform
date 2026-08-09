#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR
export PYTHONPATH=backend/src

uv run python backend/scripts/generate_vocabulary.py --check
