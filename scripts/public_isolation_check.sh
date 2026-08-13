#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if rg -n \
  'frontend/apps/studio|@ioai/studio|/api/v1/author/|Draft preview - not public' \
  frontend/apps/learn/app frontend/apps/learn/src; then
  printf 'Learner source references Studio or author-only paths\n' >&2
  exit 1
fi

if [[ -d frontend/apps/learn/.next ]]; then
  find frontend/apps/learn/.next -mindepth 1 -delete
fi

pnpm --filter @ioai/learn build

if rg -q \
  'Draft preview - not public|Editorial history|correct_choice_id|hidden_tests|reviewer_guidance|PRIVATE_REVIEWER_GUIDANCE|revision-secret' \
  frontend/apps/learn/.next; then
  printf 'Learner build contains author-only or hidden-assessment markers\n' >&2
  exit 1
fi

printf 'Learner production build contains no known author-only markers\n'
