#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"

learn_base=${LEARN_BASE_URL:-http://127.0.0.1:3000}
api_base=${API_BASE_URL:-http://127.0.0.1:8000/api/v1}
production_port=${IOAI_LEARN_PRODUCTION_PORT:-3100}
production_base="http://127.0.0.1:${production_port}"
playwright_image=${IOAI_PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright:v1.55.0-noble}
local_uid=$(id -u)
local_gid=$(id -g)
production_log=$(mktemp)
production_pid=''
frontends_stopped=0

cleanup() {
  if [[ -n "$production_pid" ]]; then
    kill "$production_pid" 2>/dev/null || true
    wait "$production_pid" 2>/dev/null || true
  fi
  rm -f "$production_log"
  if [[ "$frontends_stopped" == "1" ]]; then
    docker compose up -d learn studio >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

curl --fail --silent --show-error http://127.0.0.1:8000/health/ready >/dev/null
curl --fail --silent --show-error "$learn_base/problems" >/dev/null

printf 'Running learner desktop and mobile browser matrix\n'
LEARN_BASE_URL="$learn_base" API_BASE_URL="$api_base" \
  pnpm exec playwright test frontend/tests/e2e/learner-solving-loop.spec.ts \
    --project=chromium --project=mobile-chrome \
    --grep 'browse, filter|restores bilingual|covers direct URLs|keeps solving usable'

docker run --rm --pull=missing --network host --ipc=host \
  --user "$local_uid:$local_gid" \
  -e CI=true -e LEARN_BASE_URL="$learn_base" -e API_BASE_URL="$api_base" \
  -v "$repo_dir:/work" -w /work "$playwright_image" \
  corepack pnpm exec playwright test \
    frontend/tests/e2e/learner-solving-loop.spec.ts \
    --project=firefox --project=webkit --project=mobile-safari \
    --grep 'browse, filter|restores bilingual|covers direct URLs|keeps solving usable'

printf 'Running the browser-independent abuse boundary once\n'
LEARN_BASE_URL="$learn_base" API_BASE_URL="$api_base" \
  pnpm exec playwright test frontend/tests/e2e/learner-solving-loop.spec.ts \
    --project=chromium --grep 'bounded anonymous abuse'

printf 'Building and starting an isolated learner production server\n'
docker compose stop learn studio >/dev/null
frontends_stopped=1
pnpm --filter @ioai/learn build
API_INTERNAL_BASE=http://127.0.0.1:8000 \
  pnpm --filter @ioai/learn start --hostname 127.0.0.1 --port "$production_port" \
  >"$production_log" 2>&1 &
production_pid=$!

for _ in $(seq 1 60); do
  if curl --fail --silent "$production_base/problems" >/dev/null; then
    break
  fi
  if ! kill -0 "$production_pid" 2>/dev/null; then
    cat "$production_log" >&2
    exit 1
  fi
  sleep 1
done
curl --fail --silent --show-error "$production_base/problems" >/dev/null

printf 'Measuring cold normal-broadband production budgets\n'
LEARN_BASE_URL="$production_base" API_BASE_URL="$api_base" \
  IOAI_RUN_LEARNER_PERFORMANCE=1 \
  pnpm exec playwright test frontend/tests/e2e/learner-performance.spec.ts \
    --project=learner-performance

printf 'Learner browser and production performance checks passed.\n'
