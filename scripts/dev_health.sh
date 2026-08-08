#!/usr/bin/env bash
set -euo pipefail

printf 'API health\n'
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
printf '\nLearn route\n'
curl -fsS http://127.0.0.1:3000/problems
printf '\nStudio route\n'
curl -fsS http://127.0.0.1:3001/author/problems
printf '\nAll checks passed\n'
