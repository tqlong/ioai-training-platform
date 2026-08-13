#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"
export UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/ioai-release0-uv-cache}
export COMPOSE_PROGRESS=${COMPOSE_PROGRESS:-plain}
frontends_stopped=0

restore_frontend_writers() {
  if [[ "$frontends_stopped" == 1 ]]; then
    docker compose up -d learn studio >/dev/null 2>&1 || true
    frontends_stopped=0
  fi
}
trap restore_frontend_writers EXIT

mode=${1:-all}
case "$mode" in
  quality|postgres|browser|compose|recovery|all) ;;
  *)
    printf 'Usage: release0_verification.sh [quality|postgres|browser|compose|recovery|all]\n' >&2
    exit 2
    ;;
esac

install_dependencies() {
  printf 'Installing exactly from committed lockfiles\n'
  uv sync --frozen --all-groups
  CI=true pnpm install --frozen-lockfile
}

run_quality() {
  printf 'Running backend formatting, lint, typing, and unit gates\n'
  uv run --frozen --no-sync ruff format --check .
  uv run --frozen --no-sync ruff check .
  uv run --frozen --no-sync pyright
  uv run --frozen --no-sync pytest backend/tests/unit

  printf 'Running frontend lint, typing, component, drift, leak, and build gates\n'
  running_services=$(docker compose ps --status running --services 2>/dev/null || true)
  if grep -Eq '^(learn|studio)$' <<<"$running_services"; then
    printf 'Stopping mounted frontend writers before production builds\n'
    docker compose stop learn studio
    frontends_stopped=1
  fi
  for build_dir in frontend/apps/learn/.next frontend/apps/studio/.next; do
    if [[ -d "$build_dir" ]]; then
      find "$build_dir" -mindepth 1 -delete
    fi
  done
  pnpm lint
  pnpm typecheck
  pnpm test
  bash scripts/openapi_drift_check.sh
  bash scripts/public_isolation_check.sh
  pnpm build
  restore_frontend_writers
}

run_postgres() {
  printf 'Running all backend tests against isolated PostgreSQL\n'
  bash scripts/backend_test.sh
  bash scripts/foundation_migration_check.sh
}

run_browser() {
  printf 'Installing the committed Playwright Chromium engine\n'
  pnpm exec playwright install chromium
  bash scripts/dev_redeploy.sh
  bash scripts/client_contract_check.sh
  bash scripts/observability_check.sh
  bash scripts/health_dependency_check.sh
  bash scripts/accessibility_check.sh
  bash scripts/learner_system_check.sh
  bash scripts/author_system_check.sh
  bash scripts/assessment_system_check.sh
}

run_compose() {
  pnpm exec playwright install chromium
  bash scripts/compose_lifecycle_check.sh
}

run_recovery() {
  bash scripts/backup_restore_rehearsal.sh
}

install_dependencies
case "$mode" in
  quality) run_quality ;;
  postgres) run_postgres ;;
  browser) run_browser ;;
  compose) run_compose ;;
  recovery) run_recovery ;;
  all)
    run_quality
    run_postgres
    run_browser
    run_compose
    run_recovery
    ;;
esac
printf 'Release 0 verification mode passed: %s\n' "$mode"
