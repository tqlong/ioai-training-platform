#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/uv-cache}
export UV_CACHE_DIR
export IOAI_TEST_DATABASE_URL=${IOAI_TEST_DATABASE_URL:-postgresql+psycopg://ioai_test:ioai_test@127.0.0.1:5433/ioai_test}
export IOAI_DATABASE_URL="$IOAI_TEST_DATABASE_URL"

printf 'Starting isolated PostgreSQL integration-test environment\n'
docker compose --profile test up -d --wait postgres-test
printf 'Running pytest against database ioai_test on port 5433\n'
uv run pytest "$@"
