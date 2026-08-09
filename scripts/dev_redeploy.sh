#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

printf 'Redeploying IOAI Release 0 local stack\n'
printf 'Recreating PostgreSQL without removing its data volume\n'
docker compose up -d --force-recreate postgres

bash scripts/dev_migrate.sh

printf 'Recreating API, Learn, and Studio services\n'
docker compose up -d --force-recreate --remove-orphans api learn studio
printf 'Redeploy complete. Use bash scripts/dev_health.sh to check readiness.\n'
