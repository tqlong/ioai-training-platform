#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

printf 'Stopping frontend/API development services before production builds\n'
docker compose stop api learn studio

bash scripts/foundation_quality.sh
bash scripts/foundation_migration_check.sh
bash scripts/public_isolation_check.sh

printf 'Redeploying database, migrations, API, Learn, and Studio for browser verification\n'
bash scripts/dev_redeploy.sh
bash scripts/test_editorial_e2e.sh

printf 'Phase 7 editorial publication baseline passed.\n'
