#!/usr/bin/env bash
set -euo pipefail

printf 'API health\n'
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
printf '\nPublic canonical vocabulary\n'
curl -fsS 'http://127.0.0.1:8000/api/v1/vocabulary?vocabulary_type=PATHWAY_STAGE&limit=2'
printf '\nAuthor canonical vocabulary\n'
curl -fsS 'http://127.0.0.1:8000/api/v1/author/vocabulary?vocabulary_type=PATHWAY_STAGE&limit=2'
printf '\nLearn route\n'
curl -fsS http://127.0.0.1:3000/problems
printf '\nStudio route\n'
curl -fsS http://127.0.0.1:3001/author/problems
printf '\nAll checks passed\n'
