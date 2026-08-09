#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DRIFT_DIR="$(mktemp -d)"
trap 'rm -rf "$DRIFT_DIR"' EXIT
export PYTHONPATH=backend/src

uv run --group backend python backend/scripts/dump_openapi.py \
  --output "$DRIFT_DIR/openapi.json"
pnpm exec openapi-typescript \
  "$DRIFT_DIR/openapi.json" \
  -o "$DRIFT_DIR/openapi.ts"

cmp backend/generated/openapi.json "$DRIFT_DIR/openapi.json"
cmp frontend/packages/api-client/src/generated/openapi.ts "$DRIFT_DIR/openapi.ts"
cmp backend/generated/vocabulary.json \
  frontend/packages/vocabulary/src/generated/vocabulary.json

printf 'OpenAPI, generated client, and vocabulary artifacts are current\n'
