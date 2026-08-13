#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RESPONSE_FILE="$(mktemp)"
POSTGRES_PAUSED=false
cleanup() {
  if [[ "$POSTGRES_PAUSED" == true ]]; then
    docker compose unpause postgres >/dev/null 2>&1 || true
  fi
  rm -f "$RESPONSE_FILE"
}
trap cleanup EXIT

printf 'Verifying healthy API, Learn, and Studio surfaces\n'
curl --fail --silent --show-error http://127.0.0.1:8000/health/live >/dev/null
curl --fail --silent --show-error http://127.0.0.1:8000/health/ready >/dev/null
curl --fail --silent --show-error http://127.0.0.1:3000/problems >/dev/null
curl --fail --silent --show-error http://127.0.0.1:3001/author/problems >/dev/null

printf 'Pausing PostgreSQL to verify liveness/readiness separation\n'
docker compose pause postgres >/dev/null
POSTGRES_PAUSED=true

curl --fail --silent --show-error http://127.0.0.1:8000/health/live >/dev/null
STATUS_CODE="$(
  curl --silent --show-error --max-time 10 \
    --output "$RESPONSE_FILE" --write-out '%{http_code}' \
    http://127.0.0.1:8000/health/ready
)"
if [[ "$STATUS_CODE" != 503 ]]; then
  printf 'Expected readiness 503 while PostgreSQL is paused, found %s\n' \
    "$STATUS_CODE" >&2
  exit 1
fi
if ! rg --fixed-strings '"status":"not_ready"' "$RESPONSE_FILE" >/dev/null \
  || ! rg --fixed-strings '"database":"unavailable"' "$RESPONSE_FILE" >/dev/null \
  || ! rg --fixed-strings '"schema":"unknown"' "$RESPONSE_FILE" >/dev/null; then
  printf 'Readiness failure was not the safe machine-readable contract\n' >&2
  exit 1
fi

docker compose unpause postgres >/dev/null
POSTGRES_PAUSED=false
for attempt in {1..20}; do
  if curl --fail --silent --max-time 5 \
    http://127.0.0.1:8000/health/ready >/dev/null; then
    printf 'Readiness recovered after PostgreSQL resumed\n'
    exit 0
  fi
  sleep 1
done

printf 'API readiness did not recover after PostgreSQL resumed\n' >&2
exit 1
