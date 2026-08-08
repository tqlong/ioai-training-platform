#!/usr/bin/env bash
set -euo pipefail

printf 'Stopping IOAI Release 0 local stack\n'
docker compose down
