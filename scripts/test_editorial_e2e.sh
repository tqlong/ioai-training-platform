#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

curl -fsS http://127.0.0.1:8000/health/ready >/dev/null
curl -fsS http://127.0.0.1:3001/author/problems >/dev/null

pnpm exec playwright test frontend/tests/e2e/editorial-publication.spec.ts
