#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -d frontend/apps/learn/.next ]]; then
  find frontend/apps/learn/.next -mindepth 1 -delete
fi

pnpm --filter @ioai/learn build

if rg -q \
  'Draft preview - not public|Editorial history|correct_choice_id|hidden_tests|revision-secret' \
  frontend/apps/learn/.next; then
  printf 'Learner build contains author-only or hidden-assessment markers\n' >&2
  exit 1
fi

printf 'Learner production build contains no known author-only markers\n'
