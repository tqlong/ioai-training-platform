#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export LOCAL_UID="$(id -u)"
export LOCAL_GID="$(id -g)"

printf 'Redeploying IOAI Release 0 local stack\n'
printf 'Recreating PostgreSQL without removing its data volume\n'
docker compose up -d --force-recreate --wait postgres

bash scripts/dev_migrate.sh
bash scripts/dev_seed.sh

printf 'Recreating API, Learn, and Studio services\n'
docker compose up -d --force-recreate --remove-orphans --wait api learn studio
bash scripts/dev_health.sh
printf 'Redeploy complete and healthy.\n'
