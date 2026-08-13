#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"

studio_base=${STUDIO_BASE_URL:-http://127.0.0.1:3001}
learn_base=${LEARN_BASE_URL:-http://127.0.0.1:3000}
api_base=${API_BASE_URL:-http://127.0.0.1:8000/api/v1}
playwright_image=${IOAI_PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright:v1.55.0-noble}
local_uid=$(id -u)
local_gid=$(id -g)

curl --fail --silent --show-error http://127.0.0.1:8000/health/ready >/dev/null
curl --fail --silent --show-error "$studio_base/author/assessments" >/dev/null
curl --fail --silent --show-error "$learn_base/submissions" >/dev/null

printf 'Running complete cross-application assessment checks in Chromium\n'
STUDIO_BASE_URL="$studio_base" LEARN_BASE_URL="$learn_base" API_BASE_URL="$api_base" \
  pnpm exec playwright test frontend/tests/e2e/manual-assessment.spec.ts \
    --project=chromium

printf 'Running the critical human/correction path in Firefox and WebKit\n'
docker run --rm --pull=missing --network host --ipc=host \
  --user "$local_uid:$local_gid" \
  -e CI=true -e STUDIO_BASE_URL="$studio_base" \
  -e LEARN_BASE_URL="$learn_base" -e API_BASE_URL="$api_base" \
  -v "$repo_dir:/work" -w /work "$playwright_image" \
  corepack pnpm exec playwright test frontend/tests/e2e/manual-assessment.spec.ts \
    --project=firefox --project=webkit \
    --grep 'snapshot-bound human queue'

printf 'Running storage-disabled keyboard assessment on mobile profiles\n'
STUDIO_BASE_URL="$studio_base" LEARN_BASE_URL="$learn_base" API_BASE_URL="$api_base" \
  pnpm exec playwright test frontend/tests/e2e/manual-assessment.spec.ts \
    --project=mobile-chrome --grep 'storage-disabled mobile'
docker run --rm --pull=missing --network host --ipc=host \
  --user "$local_uid:$local_gid" \
  -e CI=true -e STUDIO_BASE_URL="$studio_base" \
  -e LEARN_BASE_URL="$learn_base" -e API_BASE_URL="$api_base" \
  -v "$repo_dir:/work" -w /work "$playwright_image" \
  corepack pnpm exec playwright test frontend/tests/e2e/manual-assessment.spec.ts \
    --project=mobile-safari --grep 'storage-disabled mobile'

printf 'Manual-assessment system checks passed.\n'
