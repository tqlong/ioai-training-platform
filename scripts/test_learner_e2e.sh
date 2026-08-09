#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

curl -fsS http://127.0.0.1:8000/health/ready >/dev/null
curl -fsS http://127.0.0.1:3000/problems >/dev/null

LEARN_BASE_URL=${LEARN_BASE_URL:-http://127.0.0.1:3000} \
API_BASE_URL=${API_BASE_URL:-http://127.0.0.1:8000/api/v1} \
  pnpm exec playwright test frontend/tests/e2e/learner-solving-loop.spec.ts
