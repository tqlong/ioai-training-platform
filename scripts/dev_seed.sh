#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

printf 'Synchronizing validated canonical vocabulary\n'
docker compose run --rm api bash -lc \
  "uv sync --frozen --only-group backend && PYTHONPATH=/app/backend/src uv run --frozen --no-sync python backend/scripts/sync_vocabulary.py"
