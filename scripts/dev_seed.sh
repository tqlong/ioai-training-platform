#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

printf 'Synchronizing validated canonical vocabulary\n'
docker compose run --rm api bash -lc \
  "PYTHONPATH=/app/backend/src uv run --group backend python backend/scripts/sync_vocabulary.py"
