#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SYSTEM_API_BASE=${IOAI_SYSTEM_API_BASE:-http://127.0.0.1:8000/api/v1}

bash scripts/openapi_drift_check.sh
pnpm --filter @ioai/api-client lint
pnpm --filter @ioai/api-client typecheck
pnpm --filter @ioai/api-client test
IOAI_SYSTEM_API_BASE="$SYSTEM_API_BASE" \
  pnpm --filter @ioai/api-client test:system-contract
