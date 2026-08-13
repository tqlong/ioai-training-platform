# Local operations (Release 0 foundation)

## Start/stop

- `bash scripts/dev_start.sh` starts PostgreSQL, applies migrations, synchronizes
  canonical vocabulary, and starts API, Learn, and Studio services.
- `bash scripts/dev_redeploy.sh` recreates PostgreSQL, applies migrations,
  synchronizes canonical vocabulary, and recreates API, Learn, and Studio while
  preserving the database volume.
- `bash scripts/dev_stop.sh` stops all services.
- `bash scripts/phase8_redeploy.sh` performs the Phase 8 deployment-only path:
  recreate PostgreSQL without deleting its volume, apply migrations, synchronize
  vocabulary, recreate API/Learn/Studio, and check health. It does not run tests.

Default host exposure is intentionally narrow for the no-auth editorial pilot:

- Learn is available on `0.0.0.0:3000` for approved classroom testing.
- PostgreSQL and FastAPI bind to host loopback at `127.0.0.1:5432` and
  `127.0.0.1:8000`.
- Studio binds to host loopback at `127.0.0.1:3001`.
- The Learn same-origin proxy returns a uniform public 404 for every
  `/api/v1/author/...` path. Studio reaches those commands through its local
  proxy and the internal Compose API service.

These controls limit local network exposure; they are not authentication or a
production authorization model. Do not expose Studio or the API publicly in
Release 0.

## Migration and seed

- `bash scripts/dev_migrate.sh` runs Alembic migration head application.
- `bash scripts/dev_seed.sh` validates and idempotently synchronizes the generated
  canonical vocabulary artifact. Repeated runs report records as unchanged.
- `bash scripts/generate_contracts.sh` regenerates deterministic OpenAPI,
  OpenAPI-derived TypeScript, and the frontend canonical vocabulary artifact.
- `bash scripts/openapi_drift_check.sh` verifies all generated contracts and
  frontend vocabulary data are current without changing checked-in files.
- `bash scripts/client_contract_check.sh` runs deterministic drift, generated-
  type/wrapper compatibility, unit contract, and running-API contract checks.
  It defaults to `http://127.0.0.1:8000/api/v1`; override
  `IOAI_SYSTEM_API_BASE` for another local verification API. The running check
  creates one empty draft to prove the author command/validation contract.
- `bash scripts/vocabulary_drift_check.sh` verifies `vocab.md` and the backend
  canonical artifact are synchronized.

## Health and smoke checks

- `bash scripts/dev_health.sh` probes health endpoints, public and author
  vocabulary projections, and key route shells.
- `bash scripts/observability_check.sh` sends a correlated health request and
  verifies the API emitted one structured completion event without logging the
  query value.
- API request logs are compact JSON allowlists. They contain environment,
  request ID, route template, method, status, outcome, and duration only.
  Publication, submission, feedback, and assessment events additionally contain
  a canonical problem slug and one-way operation digest. Request/response bodies,
  answers, notes, receipts, credentials, SQL, object keys, and raw exception
  details are excluded. Uvicorn access logging is disabled to avoid raw-query
  duplication; use the structured request event for correlation.
- `bash scripts/health_dependency_check.sh` verifies API liveness and dependency
  readiness separately, probes Learn and Studio, briefly pauses only the
  development PostgreSQL container, confirms a safe readiness 503 while
  liveness remains 200, resumes PostgreSQL, and requires readiness recovery.
- `bash scripts/accessibility_check.sh` runs the representative learner and
  Studio WCAG scan, required breakpoint/reflow assertions, 200% text zoom, and
  dialog keyboard/focus checks against an already healthy stack. Human-assisted
  checks and honest environment limitations are recorded in
  `docs/phase9-accessibility-checklist.md`.
- `bash scripts/learner_system_check.sh` runs the learner-critical desktop and
  mobile Chromium/Firefox/WebKit matrix, then stops the mounted frontends,
  builds and starts an isolated production Learn server, and measures the cold
  normal-broadband 2 s/3 s budgets. Its exit trap stops the production process
  and restarts the Compose frontends. Firefox/WebKit run in the pinned matching
  Playwright container because their host libraries are unavailable; see
  `docs/phase9-browser-performance-matrix.md`.
- Public canonical vocabulary is available from `GET /api/v1/vocabulary` with a
  required `vocabulary_type`; author-safe values and availability are available
  from `GET /api/v1/author/vocabulary`.
- Missing-value proposals use `POST /api/v1/author/vocabulary/proposals` and are
  reviewable through `GET /api/v1/author/vocabulary/proposals`.

## Recovery and maintenance

- `bash scripts/foundation_quality.sh` runs baseline quality gates.
- `bash scripts/backend_test.sh` starts a profile-scoped PostgreSQL service on
  `127.0.0.1:5433`, uses the dedicated `ioai_test` database and volume, and
  runs pytest. Destructive migration tests refuse a database whose name does
  not end in `_test`; they never fall back to the development `ioai` database.
- `bash scripts/phase7_quality.sh` stops API/frontend development services,
  runs the complete editorial-publication quality and isolation gates,
  redeploys the database/migrations/backend/frontends, and runs the focused
  Chromium workflow.
- `bash scripts/test_editorial_e2e.sh` runs the editorial publication browser
  workflow against an already healthy local stack.
- `bash scripts/phase8_test.sh` runs the Phase 8 non-deployment quality gates.
  With `PHASE8_E2E=1`, it additionally runs the learner browser baseline against
  an already deployed stack; it never redeploys services. Stop Learn and Studio
  first for its production builds because the mounted development servers and
  host build otherwise compete for the same `.next` directories.
- `bash scripts/test_learner_e2e.sh` runs only the learner browse, solve,
  feedback, progress, and continue workflow against an already healthy stack.
- `bash scripts/db_backup_restore.sh backup` creates a PostgreSQL dump.
- `bash scripts/db_backup_restore.sh restore <file>` restores from backup.
- `bash scripts/db_backup_restore.sh reset` recreates stack data by removing local volumes.

## Notes

- API readiness is not marked healthy when database migration checks fail.
- Studio is published on host loopback at `127.0.0.1:3001`; this is not
  authentication or production authorization.
- FastAPI accepts only the explicit local origins in `IOAI_ALLOWED_ORIGINS`,
  rejects wildcard configuration, and does not enable credentialed CORS.
- Backup/restore applies only to PostgreSQL data; browser-local progress is intentionally not stored there.
- Playwright failure traces, screenshots, and the HTML report are local ignored
  artifacts under `test-results/` and `playwright-report/`.
