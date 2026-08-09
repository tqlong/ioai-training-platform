#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export LOCAL_UID="$(id -u)"
export LOCAL_GID="$(id -g)"

printf 'Starting IOAI Release 0 local stack\n'
docker compose up -d --wait postgres
bash scripts/dev_migrate.sh
bash scripts/dev_seed.sh
docker compose up -d --wait api learn studio
bash scripts/dev_health.sh
printf 'Stack started and healthy.\n'
