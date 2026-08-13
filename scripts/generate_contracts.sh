#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export PYTHONPATH=backend/src
uv run --group backend python backend/scripts/generate_vocabulary.py
uv run --group backend python backend/scripts/dump_openapi.py
pnpm exec openapi-typescript \
  backend/generated/openapi.json \
  -o frontend/packages/api-client/src/generated/openapi.ts
cp backend/generated/vocabulary.json \
  frontend/packages/vocabulary/src/generated/vocabulary.json
