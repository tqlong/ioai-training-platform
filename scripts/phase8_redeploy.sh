#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32"* ]]; then
  export LOCAL_UID=1000
  export LOCAL_GID=1000
else
  export LOCAL_UID="$(id -u)"
  export LOCAL_GID="$(id -g)"
fi
printf 'Redeploying Phase 8 database without deleting its persistent volume\n'
docker compose up -d --force-recreate --wait postgres

printf 'Applying database migrations and canonical vocabulary synchronization\n'
bash scripts/dev_migrate.sh
bash scripts/dev_seed.sh

printf 'Recreating backend and both frontend services\n'
docker compose up -d --force-recreate --remove-orphans --wait api learn studio

printf 'Checking the separately deployed runtime\n'
bash scripts/dev_health.sh
printf 'Phase 8 deployment is healthy.\n'
