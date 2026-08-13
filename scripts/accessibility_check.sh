#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"

learn_base=${LEARN_BASE_URL:-http://127.0.0.1:3000}
studio_base=${STUDIO_BASE_URL:-http://127.0.0.1:3001}
api_base=${API_BASE_URL:-${IOAI_SYSTEM_API_BASE:-http://127.0.0.1:8000/api/v1}}
api_origin=${api_base%/api/v1}

curl --fail --silent --show-error "$learn_base/problems" >/dev/null
curl --fail --silent --show-error "$studio_base/author/problems" >/dev/null
curl --fail --silent --show-error "$api_origin/health/ready" >/dev/null

LEARN_BASE_URL="$learn_base" \
STUDIO_BASE_URL="$studio_base" \
API_BASE_URL="$api_base" \
  pnpm exec playwright test \
    frontend/tests/e2e/accessibility-responsive.spec.ts \
    --project=chromium
