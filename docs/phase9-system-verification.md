# Phase 9 system-verification baseline

## Purpose and evidence status

This baseline maps the implemented Release 0 system to the integration and
system evidence required by `R0-011` through `R0-017`, especially
`AC-R0-015-01` through `AC-R0-015-19`. It was produced by inspecting the
repository at the start of `R0-09001`; it does not treat the presence of a test
or script as proof that the test currently passes.

Phase 9 extends the existing Phase 7, 8, and 8.1 paths. It must not create a
second API, alternate fixtures, or a parallel deployment workflow merely to
make verification easier. Runtime fixes require an observed failing regression
test. Verification-only work records failures and skips without claiming
retroactive test-driven development.

## Current implementation inventory

| Boundary | Present implementation and evidence | Baseline limitation |
| --- | --- | --- |
| PostgreSQL and Alembic | Eight ordered revisions from canonical vocabulary through the Phase 9 system-query indexes; integration tests cover the complete head chain, migrations, repositories, readiness, synchronization, public queries, learner records, publication, supporting index plans, and transactional rollback | API-level persistence and failure coverage remains assigned to `R0-09003` |
| FastAPI | Versioned public and author routers plus a real-app/real-PostgreSQL suite for vocabulary, proposals, drafts, validation/preview, workflow/publication/archive, public queries, all five submissions, feedback, receipts, and manual assessment | Adversarial leak-path, network exposure, structured observability, and dependency-readiness proof remains assigned to later Phase 9 steps |
| Public isolation | Dedicated published reader plus an adversarial PostgreSQL/API suite covering private author notes, successor revisions, archived snapshots, rubric guidance/exemplars, answer keys, hidden tests, object keys, alternate identifiers, result receipts, OpenAPI, learner source, and production build output | No-auth network exposure and structured-log redaction remain assigned to `R0-09005` and `R0-09007` |
| Generated contracts | Deterministic OpenAPI JSON, `openapi-typescript` output, vocabulary artifacts, generation script, and drift script | Handwritten client wrappers are not comprehensively exercised against a running API |
| Learn components | Unit/component coverage for URL discovery, table/cards, detail, five response forms, local progress, feedback, continuation, and submission history | No automated accessibility scanner; responsive and keyboard proof is distributed across tests and manual notes |
| Studio components | Unit/component coverage for list/editor sections, validation, preview, editorial review, rubric editor, assessment queue, and assessment decisions | No automated accessibility scanner or complete route-width regression |
| Browser workflows | `learner-solving-loop.spec.ts` and `editorial-publication.spec.ts`, including the manual-assessment path currently embedded in the learner specification | Playwright config runs Chromium desktop only; browser/mobile matrix and full performance budgets are not proved |
| Health and observability | Liveness/readiness routes, request-ID response middleware, readiness integration tests, and Compose health checks | Readiness returns a successful HTTP status when degraded; Compose waits on process startup in places; structured completion/operation events and redaction proof are absent |
| Local operations | Compose topology plus start, stop, migrate, seed, redeploy, phase-specific test, smoke, and backup/restore commands; PostgreSQL/API/Studio bind to loopback, Learn blocks author proxy paths, and FastAPI uses explicit non-credentialed CORS origins | No clean/persisted lifecycle rehearsal exists and restore is not verified in a disposable database |
| CI and reproducibility | Committed `uv.lock` and `pnpm-lock.yaml`, frozen installs, backend/frontend quality scripts, drift checks, migration checks, and one GitHub Actions workflow | CI selects pnpm 9 while the root manifest declares pnpm 10, does not run browser/accessibility/Compose/recovery gates, and can silently omit browser evidence |

## `R0-015` criterion ownership

| Criterion | Current evidence | Gap to close | Phase 9 owner |
| --- | --- | --- | --- |
| `AC-R0-015-01` | Accessible-role component tests and focused dialog/focus assertions | Automated scan plus route-level keyboard, focus, screen-reader, and state coverage | `R0-09009` |
| `AC-R0-015-02` | Text-backed status/evidence component assertions | Detectable contrast scan and documented grayscale/non-color manual evidence | `R0-09009` |
| `AC-R0-015-03` | Learner Playwright checks at 360, 768, 1024, and 1440 px | Complete learner/Studio route coverage, zoom, overflow, and intermediate layout proof | `R0-09009`–`R0-09012` |
| `AC-R0-015-04` | A local warmed detail-navigation regression | Representative production-build library FCP under the documented broadband profile and no draft/account payload | `R0-09010` |
| `AC-R0-015-05` | Detail navigation and non-blocking component behavior | Representative permanent-detail usability budget and unrelated-reading proof | `R0-09010` |
| `AC-R0-015-06` | Chromium desktop Playwright project | Documented Chromium, Firefox, WebKit, and available mobile-equivalent matrix | `R0-09010`–`R0-09012` |
| `AC-R0-015-07` | Domain invariants, SQLAlchemy model checks, PostgreSQL constraints, append-only assessment history, and verified public/assessment index plans | API-level persistence coverage remains | `R0-09002` complete; `R0-09003` |
| `AC-R0-015-08` | Complete linear empty-database chain, idempotent 343-record canonical sync, representative safe downgrades through manual assessment, and a new forward-only Phase 9 index migration | Clean deployment rehearsal remains | `R0-09002` complete; `R0-09013` |
| `AC-R0-015-09` | Transactional migration-DDL rollback, unit-of-work and atomic publication rollback, plus real HTTP rejected-command non-mutation assertions | Dependency interruption/recovery remains | `R0-09002`–`R0-09003` complete; `R0-09008` |
| `AC-R0-015-10` | Adversarial isolation plus loopback API/database exposure, explicit CORS, and a runtime-tested Learn proxy guard that returns a public 404 for author paths | Clean lifecycle rehearsal remains | `R0-09004`–`R0-09005` complete; `R0-09013` |
| `AC-R0-015-11` | Runtime-confirmed `127.0.0.1` bindings for PostgreSQL, API, and Studio, with documentation that this is not authorization | Clean lifecycle configuration proof remains | `R0-09005` complete; `R0-09013` |
| `AC-R0-015-12` | Real bounded persistence plus explicit no-wildcard/non-credentialed CORS and the learner/author proxy split | Structured-log review remains | `R0-09003`, `R0-09005` complete; `R0-09007` |
| `AC-R0-015-13` | Cross-route adversarial not-found/alternate-ID/rejected-query checks expose no private values or infrastructure details | Structured-log redaction remains | `R0-09004` complete; `R0-09007` |
| `AC-R0-015-14` | Backup, restore, and reset command branches plus a short runbook | Disposable restore rehearsal comparing all system-of-record entities; safe confirmed reset | `R0-09014` |
| `AC-R0-015-15` | Request-ID response propagation | Structured request/operation completion events, duration/outcome fields, propagation, and redaction | `R0-09007` |
| `AC-R0-015-16` | Separate health routes, database probe, and service health checks | Non-success degraded readiness, migration-head proof, dependency waiting, interruption/recovery smoke | `R0-09008`, `R0-09013` |
| `AC-R0-015-17` | Lockfiles and foundation/phase quality scripts | One clean deterministic system entrypoint, aligned tool versions, browser/Compose/recovery CI jobs | `R0-09013`, `R0-09015` |
| `AC-R0-015-18` | Project TDD policy and phase baseline records | Enforce a recorded red step for every Phase 9 runtime fix; never infer prior red evidence | Every behavior-changing Phase 9 step |
| `AC-R0-015-19` | OpenAPI/vocabulary/client drift script in local and CI quality gates | Running-API wrapper compatibility and a single authoritative deterministic CI gate | `R0-09006`, `R0-09015` |

## Functional cross-system ownership

| Requirement group | Existing vertical evidence | Phase 9 system proof |
| --- | --- | --- |
| `R0-011` learner discovery | Public query/API tests, Learn component tests, and learner Chromium flow | PostgreSQL-backed API, leak-path, accessibility, browser, responsive, and performance evidence in `R0-09003`–`R0-09004` and `R0-09009`–`R0-09010` |
| `R0-012` solving loop | Assessment/feedback/recommendation tests, local-progress components, and learner Chromium flow | Real persistence/API failures, privacy/isolation, cross-browser learner journey, and recovery behavior in `R0-09003`–`R0-09005`, `R0-09007`, and `R0-09010` |
| `R0-013` authoring | Domain/application/API tests and Studio editor/preview components | Real persistence/API, accessibility, cross-browser editorial journey, and Compose exposure in `R0-09003`, `R0-09005`, `R0-09009`, `R0-09011`, and `R0-09013` |
| `R0-014` publication | Workflow/publication/repository isolation tests and editorial Chromium flow | Transaction failure, adversarial isolation, and complete system publication/archive/republish flow in `R0-09002`–`R0-09004` and `R0-09011` |
| `R0-015` quality and operations | Distributed quality scripts, focused integration tests, health checks, and runbooks | Criterion ownership above, consolidated by `R0-09015` and audited by `R0-09016` |
| `R0-016` governance | Governing documents, delivery plan, and traceability index | This baseline, per-step commits/checkmarks, and the final criterion audit in `R0-09016` |
| `R0-017` manual assessment | Rubric/decision/API/component tests and one combined Chromium path | PostgreSQL-backed API/isolation, accessibility, and a dedicated cross-application browser journey in `R0-09003`–`R0-09004`, `R0-09009`, and `R0-09012` |

## Execution rules

- Complete Phase 9 in plan order. Mark and commit one `R0-09xxx` item only
  after its stated evidence passes.
- Use the existing generated contract, canonical seed, published snapshot, and
  application entrypoint paths. Do not introduce test-only product paths.
- Keep tests and redeployment separate where concurrent Next.js development and
  production builds would share `.next` output.
- Put repeatable database, migration, backend, frontend, and redeployment
  commands under `scripts/`; document exact prerequisites and destructive
  boundaries.
- The final baseline records every unavailable browser or manual check as a
  limitation. A required silent skip keeps the owning Phase 9 item incomplete.

## Completed step evidence

### `R0-09002`

- Red observed: the focused PostgreSQL tests failed because migration
  `20260813_09002` and indexes `ix_published_snapshot_slug` and
  `ix_learner_attempt_outcome_submitted` did not exist.
- Green observed: 122 affected PostgreSQL/domain/model tests passed, including
  the complete migration chain, latest downgrade/re-upgrade, idempotent
  canonical synchronization, append-only assessment decisions, publication and
  migration rollback, and forced index-plan checks.
- Static gates: Ruff format/check, Pyright, and the Alembic-head check passed.

### `R0-09003`

- Added 10 integration tests through the default FastAPI wiring and isolated
  PostgreSQL, with 343 synchronized canonical vocabulary records.
- Covered public and author vocabulary, proposals, draft save/list,
  validation/preview, review/change/approval/publication/archive, stable current
  snapshots, public list/filter/sort/page/detail/recommendation, all five
  response families, idempotent feedback/submission, private result receipts,
  pending assessment, decision/correction history, and safe rejected-command
  non-mutation.
- The first verification run passed 8 of 9 cases; the sole failure identified
  that the new test used unsupported query name `search` instead of the
  documented public contract `q`. The test was corrected without changing
  product behavior, then all 10 focused tests and the full 262-test backend
  suite passed.
- Static gates: backend Ruff format/check and Pyright passed.

### `R0-09004`

- Added a six-case adversarial PostgreSQL/API isolation suite using deliberately
  private author notes, an approved successor, a draft-only problem, an archived
  historical snapshot, answer keys, hidden tests, private rubric guidance and
  exemplar, object key, revision/workflow fields, and alternate identifiers.
- Proved safe current-only list/detail/recommendation, snapshot-bound
  submission/result/feedback, uniform invalid receipt and identifier behavior,
  archive removal with retained history, public OpenAPI separation, and no
  Learn-to-Studio/author-route source dependency.
- Expanded `scripts/public_isolation_check.sh`; the Learn production build and
  generated output scan passed, as did OpenAPI/client/vocabulary drift, 10
  focused isolation/contract tests, Ruff, Pyright, and shell syntax validation.
- `scripts/dev_redeploy.sh` preserved the development volume, applied migration
  `20260813_09002`, idempotently synchronized all 343 vocabulary records, and
  restored healthy PostgreSQL, API, Learn, and Studio services.

### `R0-09005`

- Red observed: focused tests failed because `ApiSettings` had no allowed-origin
  contract, FastAPI used credentialed wildcard CORS, Compose published
  PostgreSQL/API on all interfaces, and Learn had no author-path proxy guard.
- Added validated explicit HTTP(S) origins, bounded CORS methods/headers without
  credentials, loopback host bindings for PostgreSQL/API/Studio, internal-only
  API environment use by Learn, and a uniform safe 404 middleware boundary for
  `/api/v1/author/...` on the learner origin.
- Nine focused backend/configuration tests and all 34 Learn tests passed, along
  with Ruff, Pyright, Learn lint/typecheck, Compose configuration validation,
  two successful Learn production builds, and the public build leak scan.
- `scripts/dev_redeploy.sh` preserved data and returned every service healthy.
  Runtime probes confirmed loopback ports, public Learn API status 200, author
  paths through Learn status 404, configured-origin preflight status 200 with no
  credential header, and unknown-origin preflight status 400.

### `R0-09006`

- Red observed: the API-client regression test failed because stable FastAPI
  errors lost the propagated `x-request-id`; a compile-time compatibility check
  also caught an incorrect assumed success status for learner submission.
- Contract generation now validates/regenerates the canonical vocabulary,
  dumps sorted OpenAPI JSON, generates TypeScript, and copies the frontend
  vocabulary through one command. Drift verification independently generates
  OpenAPI and TypeScript twice and compares both runs and all committed outputs.
- Handwritten query inputs derive their value types from generated operations;
  compile-time assertions bind representative public/author request and response
  wrappers to their exact generated operations. Runtime tests cover pagination,
  all five discriminated submission bodies, idempotency fields, opaque receipt
  headers, request IDs, and stable error decoding.
- `scripts/client_contract_check.sh` passed 24 unit contract tests and three
  running-API public/author/negative cases against the loopback FastAPI service,
  plus lint, strict type checking, vocabulary/OpenAPI/client drift, and repeated
  deterministic generation.

### `R0-09007`

- Red observed: focused tests could not import an application observability
  contract or JSON adapter, the API could not inject a sink, and unsafe request
  IDs were trusted. Runtime rehearsal then exposed two integration defects in
  sequence: the standalone event logger dropped INFO records and Uvicorn access
  logs duplicated the raw query string.
- Added an application-owned, allowlisted `ObservabilityEvent`, request-context
  binding, opaque operation digests, and bounded canonical fields, with a JSON
  logging adapter behind an `EventSink` port. The entrypoint sanitizes or creates
  request IDs, binds them across synchronous use cases, returns the same ID, and
  emits exactly one completion event with a route template rather than raw URL.
- Default publication, learner submission, feedback, and manual-assessment
  services emit success/failure events containing only environment, correlated
  request ID, duration, safe event/outcome, canonical slug, and one-way operation
  digest. Tests explicitly exclude bodies, answers, hidden guidance, notes,
  receipts, raw keys/IDs, SQL/errors, filesystem paths, and object keys.
- The focused 44-test unit/API/PostgreSQL suite, Ruff, Pyright, Compose config,
  shell validation, healthy migration-aware redeploy, and
  `scripts/observability_check.sh` passed. The final runtime log contained the
  structured request event and no supplied query value; Uvicorn access logging
  is disabled to prevent an unstructured query-string leak.

### `R0-09008`

- Red observed: degraded readiness returned HTTP 200, no adapter checked the
  database Alembic version, Compose API health used liveness, and Learn/Studio
  waited only for API process startup. Further regression tests showed probe
  exceptions could escape and OpenAPI omitted the readiness 503 contract.
- Added a dependency-readiness value contract and PostgreSQL adapter that
  requires both a successful connection and an exact match between
  `alembic_version` and repository heads. Missing/outdated schemas return safe
  `database=ready, schema=outdated`; connection or probe failures return safe
  `database=unavailable, schema=unknown`; neither exposes infrastructure detail.
- `/health/live` remains database-independent and status 200. `/health/ready`
  now returns 200 only for a current dependency state and 503 otherwise, with
  both responses in OpenAPI. Compose probes readiness and Learn/Studio require
  an API-healthy condition before starting.
- Twenty focused health, real-PostgreSQL schema, factory, and Compose tests
  passed with Ruff, Pyright, shell/config checks. A migration-aware redeploy
  returned every service healthy and `scripts/health_dependency_check.sh`
  confirmed API/FE readiness, live=200/readiness=503 while PostgreSQL was paused,
  and readiness recovery after PostgreSQL resumed.
