#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CHECK_ID="phase9-observability-check"
FORBIDDEN_QUERY="phase9-answer-must-not-appear"
LOG_FILE="$(mktemp)"
trap 'rm -f "$LOG_FILE"' EXIT

curl --fail --silent --show-error \
  --header "x-request-id: $CHECK_ID" \
  "http://127.0.0.1:8000/health/live?answer=$FORBIDDEN_QUERY" >/dev/null

docker compose logs --no-log-prefix --since 30s api >"$LOG_FILE"

if ! rg --fixed-strings "\"request_id\": \"$CHECK_ID\"" "$LOG_FILE" >/dev/null; then
  printf 'Missing structured request completion event for %s\n' "$CHECK_ID" >&2
  exit 1
fi
if rg --fixed-strings "$FORBIDDEN_QUERY" "$LOG_FILE" >/dev/null; then
  printf 'Structured logs exposed the request query\n' >&2
  exit 1
fi

printf 'Structured request event is present and excludes request query data\n'
