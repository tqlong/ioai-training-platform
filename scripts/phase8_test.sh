#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

running_services="$(docker compose ps --status running --services)"
if grep -Eq '^(learn|studio)$' <<<"$running_services"; then
  printf 'Stop Learn and Studio before this test-only production-build gate to avoid shared .next output conflicts.\n' >&2
  exit 1
fi

printf 'Running Phase 8 non-deployment quality gates\n'
bash scripts/foundation_quality.sh
bash scripts/foundation_migration_check.sh
bash scripts/public_isolation_check.sh

if [[ "${PHASE8_E2E:-0}" == "1" ]]; then
  printf 'Running learner browser baseline against the already-deployed stack\n'
  bash scripts/test_learner_e2e.sh
else
  printf 'Browser baseline skipped; set PHASE8_E2E=1 after separate deployment.\n'
fi

printf 'Phase 8 test gates passed.\n'
