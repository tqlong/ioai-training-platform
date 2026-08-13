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
curl --fail --silent --show-error "$studio_base/author/problems" >/dev/null
curl --fail --silent --show-error "$learn_base/problems" >/dev/null

printf 'Running the complete Chromium author system workflow\n'
STUDIO_BASE_URL="$studio_base" LEARN_BASE_URL="$learn_base" API_BASE_URL="$api_base" \
  pnpm exec playwright test frontend/tests/e2e/editorial-publication.spec.ts \
    --project=chromium

printf 'Running the full workflow on Firefox and WebKit\n'
docker run --rm --pull=missing --network host --ipc=host \
  --user "$local_uid:$local_gid" \
  -e CI=true -e STUDIO_BASE_URL="$studio_base" \
  -e LEARN_BASE_URL="$learn_base" -e API_BASE_URL="$api_base" \
  -v "$repo_dir:/work" -w /work "$playwright_image" \
  corepack pnpm exec playwright test \
    frontend/tests/e2e/editorial-publication.spec.ts \
    --project=firefox --project=webkit \
    --grep 'full editorial publication'

printf 'Running the smallest mobile Studio preview checks\n'
STUDIO_BASE_URL="$studio_base" LEARN_BASE_URL="$learn_base" API_BASE_URL="$api_base" \
  pnpm exec playwright test frontend/tests/e2e/editorial-publication.spec.ts \
    --project=mobile-chrome --grep 'mobile Studio viewport'
docker run --rm --pull=missing --network host --ipc=host \
  --user "$local_uid:$local_gid" \
  -e CI=true -e STUDIO_BASE_URL="$studio_base" \
  -e LEARN_BASE_URL="$learn_base" -e API_BASE_URL="$api_base" \
  -v "$repo_dir:/work" -w /work "$playwright_image" \
  corepack pnpm exec playwright test \
    frontend/tests/e2e/editorial-publication.spec.ts \
    --project=mobile-safari --grep 'mobile Studio viewport'

printf 'Author browser system checks passed.\n'
