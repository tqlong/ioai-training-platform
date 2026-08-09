#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

printf 'Starting IOAI Release 0 local stack\n'
docker compose up -d postgres
bash scripts/dev_migrate.sh
bash scripts/dev_seed.sh
docker compose up -d api learn studio
printf 'Stack started. Use bash scripts/dev_health.sh to check readiness.\n'
