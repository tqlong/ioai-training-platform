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
| Learn components | Unit/component coverage for URL discovery, table/cards, detail, five response forms, local progress, feedback, continuation, and submission history, complemented by a deployed axe/keyboard/width/zoom browser gate | Physical screen-reader and touch checks remain observed-pilot work |
| Studio components | Unit/component coverage for list/editor sections, validation, preview, editorial review, rubric editor, assessment queue, and assessment decisions, complemented by representative route-level accessibility and reflow checks | Physical screen-reader and touch checks remain observed-pilot work |
| Browser workflows | `learner-solving-loop.spec.ts`, `editorial-publication.spec.ts`, and `accessibility-responsive.spec.ts`, including representative Learn/Studio WCAG scanning and required breakpoints | Playwright config still runs Chromium desktop only; cross-browser/mobile journey and full performance budgets remain assigned to `R0-09010`–`R0-09012` |
| Health and observability | Liveness/readiness routes, request-ID response middleware, readiness integration tests, and Compose health checks | Readiness returns a successful HTTP status when degraded; Compose waits on process startup in places; structured completion/operation events and redaction proof are absent |
| Local operations | Compose topology plus start, stop, migrate, seed, redeploy, phase-specific test, smoke, and backup/restore commands; PostgreSQL/API/Studio bind to loopback, Learn blocks author proxy paths, and FastAPI uses explicit non-credentialed CORS origins | No clean/persisted lifecycle rehearsal exists and restore is not verified in a disposable database |
| CI and reproducibility | Committed `uv.lock` and `pnpm-lock.yaml`, frozen installs, backend/frontend quality scripts, drift checks, migration checks, and one GitHub Actions workflow | CI selects pnpm 9 while the root manifest declares pnpm 10, does not run browser/accessibility/Compose/recovery gates, and can silently omit browser evidence |

## `R0-015` criterion ownership

| Criterion | Current evidence | Gap to close | Phase 9 owner |
| --- | --- | --- | --- |
| `AC-R0-015-01` | Deployed axe A/AA scans across six Learn/Studio surfaces; role/name, validation focus, repeated-control, announcement, and dialog keyboard/focus tests | Physical screen-reader and full keyboard traversal are documented observed-pilot checks, not silently treated as passes | `R0-09009` complete; limitation audited by `R0-09016` |
| `AC-R0-015-02` | Detectable axe contrast checks plus text/border/shape-backed state assertions and representative grayscale inspection | Reconfirm grayscale and focus presentation on the pilot display | `R0-09009` complete; limitation audited by `R0-09016` |
| `AC-R0-015-03` | Learner library/detail and Studio editor/assessment route checks at 360, 768, 1024, and 1440 px, including card/table switch, reflow, 200% text zoom, and page-overflow assertions | Cross-browser journey widths remain in `R0-09010`–`R0-09012`; physical touch remains an observed-pilot check | `R0-09009` complete; `R0-09010`–`R0-09012` |
| `AC-R0-015-04` | Cold production library rendered meaningful content in 1,233 ms with 216 public records under the documented 40 ms/10 Mbps profile; initial HTML excluded the private marker/internal fields and browser traffic had no account handshake | Repeat in final clean baseline | `R0-09010` complete; `R0-09016` |
| `AC-R0-015-05` | Cold permanent detail was usable in 316 ms; pending feedback left unrelated objective content readable | Repeat in final clean baseline | `R0-09010` complete; `R0-09016` |
| `AC-R0-015-06` | Learner, author, and assessment matrices passed bundled Chromium 140, Firefox 141, WebKit 26, Pixel 7 mobile-Chrome, and iPhone 15 mobile-Safari profiles | Branded current-stable browser/device checks depend on available pilot environments | `R0-09010`–`R0-09012` complete; limitation audited by `R0-09016` |
| `AC-R0-015-07` | Domain invariants, SQLAlchemy model checks, PostgreSQL constraints, append-only assessment history, and verified public/assessment index plans | API-level persistence coverage remains | `R0-09002` complete; `R0-09003` |
| `AC-R0-015-08` | Complete linear empty-database chain, idempotent 343-record canonical sync, representative safe downgrades through manual assessment, and a new forward-only Phase 9 index migration | Clean deployment rehearsal remains | `R0-09002` complete; `R0-09013` |
| `AC-R0-015-09` | Transactional migration-DDL rollback, unit-of-work and atomic publication rollback, plus real HTTP rejected-command non-mutation assertions | Dependency interruption/recovery remains | `R0-09002`–`R0-09003` complete; `R0-09008` |
| `AC-R0-015-10` | Adversarial isolation plus loopback API/database exposure, explicit CORS, and a runtime-tested Learn proxy guard that returns a public 404 for author paths | Clean lifecycle rehearsal remains | `R0-09004`–`R0-09005` complete; `R0-09013` |
| `AC-R0-015-11` | Runtime-confirmed `127.0.0.1` bindings for PostgreSQL, API, and Studio, with documentation that this is not authorization | Clean lifecycle configuration proof remains | `R0-09005` complete; `R0-09013` |
| `AC-R0-015-12` | Real bounded persistence plus explicit no-wildcard/non-credentialed CORS and the learner/author proxy split | Structured-log review remains | `R0-09003`, `R0-09005` complete; `R0-09007` |
| `AC-R0-015-13` | Cross-route adversarial not-found/alternate-ID/rejected-query checks expose no private values or infrastructure details | Structured-log redaction remains | `R0-09004` complete; `R0-09007` |
| `AC-R0-015-14` | Isolated logical backup/restore rehearsal compares all Release 0 system-of-record histories; restore and reset are exact-target confirmed and fail closed | Provider, retention period, and off-host schedule remain deployment decisions; device-local progress is explicitly unrecoverable | `R0-09014` complete; limitation audited by `R0-09016` |
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

### `R0-09009`

- Red observed: the new browser-width regression first found the 360 px Studio
  editor 216 px wider than the viewport, then found learner-library overflow at
  768 and 1024 px. After those constraints were corrected, the 200% text-zoom
  case exposed a further 105 px Studio tooltip overflow.
- Added `@axe-core/playwright` and a repeatable deployed-system gate covering
  six representative learner/Studio routes, four required viewport widths,
  the below-768 card/table switch, document-level overflow, 200% text zoom, and
  learner/publication dialog focus wrapping, Escape, and focus return.
- Constrained learner table/filter grids and Studio editor fields, fieldsets,
  and help tooltips so intermediate widths and text zoom reflow without
  unintended page scrolling. Existing internal table/code scrolling remains
  intentional.
- `scripts/accessibility_check.sh` passed all four browser cases in 47.8 seconds
  after the final redeploy.
  Frontend lint, strict type checking, 102 component/client tests, and both
  production builds passed. A migration-aware redeploy preserved data,
  synchronized all 343 canonical records unchanged, and returned PostgreSQL,
  API readiness, Learn, and Studio healthy.
- `docs/phase9-accessibility-checklist.md` separates automated evidence from
  human-assisted screen-reader, grayscale, physical-keyboard, and touch checks.
  Representative grayscale pages were inspected; unavailable desktop screen
  reader and physical-touch evidence is explicit rather than silently passed.

### `R0-09010`

- Red observed: the first mobile-Chrome learner journey incorrectly expected a
  desktop table; the new bilingual filter path initially ignored the mobile
  filter sheet and selected a hidden desktop result. The first matrix also
  proved Firefox/WebKit executables and host libraries were unavailable rather
  than silently skipping them.
- Hardened the existing learner workflow for its real card/table and filter-
  sheet interactions. The matrix covers all five response families, automated
  and pending feedback, exactly one continuation, submission history, English/
  Vietnamese search, hierarchical ancestor filtering with explicit descendants,
  query restoration, permanent/direct URLs, corrupt/unavailable storage,
  dependency failure, anonymous feedback limits, and draft/archived isolation.
- Added Playwright projects for Chromium 140.0.7339.16, Firefox 141.0, WebKit
  26.0, Pixel 7 mobile Chromium, and iPhone 15 mobile WebKit. The host passed
  8/8 Chromium cases in 30.3 seconds; the pinned matching Playwright container
  passed 12/12 Firefox/WebKit cases in 50.3 seconds; the abuse check passed 1/1.
- `scripts/learner_system_check.sh` then stopped mounted frontend writers,
  produced a Learn production build, launched it on loopback port 3100, and
  applied a cold 40 ms/10 Mbps down/5 Mbps up profile. Against 216 published
  records, meaningful library content appeared in 1,233 ms (budget 2,000 ms)
  and permanent detail became usable in 316 ms (budget 3,000 ms). Initial HTML
  excluded the private draft marker/internal draft fields, no account handshake
  occurred, and pending feedback did not block reading.

### `R0-09011`

- Red observed: the expanded Chromium journey found that archiving incremented
  the server revision version but the Studio list retained the pre-archive
  version, so its visible `Create new draft` action always submitted a stale
  command and failed. The initial mobile/canonical assertions also exposed test
  assumptions about hidden desktop results and disabled-option matching.
- Studio now records the deterministic post-archive version in list state, so
  re-entry through a new private draft succeeds without weakening the workflow.
  The component regression proves the successor command uses the incremented
  version; all 39 Studio component tests pass.
- The complete browser path now covers creation, structured bilingual content,
  canonical metadata and disabled future values, unsaved desktop/mobile learner
  preview, layered validation focus, review/change-request successor, approval,
  an in-flight atomic-publication isolation check, permanent public visibility,
  private published successor isolation, replacement publication, archive, and
  republish at the same permanent slug. Save, approval, and publication remain
  separate actions throughout.
- Chromium additionally proves failed autosave creates a versioned local copy,
  reload offers explicit recovery, and an external version advance produces a
  conflict requiring an explicit keep-local resolution. The final matrix passed
  4/4 Chromium cases in 43.3 seconds, complete Firefox/WebKit flows in 49.2
  seconds, mobile Chrome in 5.0 seconds, and mobile Safari in 6.4 seconds.

### `R0-09012`

- Red observed: the dedicated mixed-scoring browser path proved that the domain
  and PostgreSQL stored the completed automated component while the pending
  public HTTP projection discarded it. A focused API regression failed with a
  missing `components` field before the projection was corrected. The first
  mobile assertion also exposed the actual storage-disabled empty-state copy.
- Pending mixed submissions now return only their already-computed safe public
  components; they still expose no score claim for unfinished human work. The
  focused API tests and deployed mixed browser check pass, while private
  reviewer guidance, exemplars, and hidden data remain absent from public
  results.
- Moved manual assessment out of the learner catch-all into
  `manual-assessment.spec.ts`. The system path proves opaque receipt persistence,
  missing/wrong receipt behavior, oldest-first queue order, snapshot title and
  rubric after a newer publication, keyboard decision, learner-safe result,
  stale concurrent correction rejection, and append-only versions 1 and 2.
- Mixed scoring preserves the exact automated component across human correction
  without rerunning it. Storage-disabled submission still reaches PostgreSQL,
  leaves no device history, and remains assessable by keyboard without page
  overflow. The matrix passed 3/3 Chromium cases in 16.5 seconds, Firefox/
  WebKit in 24.4 seconds, mobile Chrome in 6.2 seconds, and mobile Safari in
  7.3 seconds. Ruff, Pyright, all 284 backend tests, frontend lint/typecheck and
  102 component/client tests, deterministic contract drift, both production
  builds, and the migration-aware redeploy also passed; all 343 canonical
  records remained unchanged and every service returned healthy.

### `R0-09013`

- Red observed: the committed-lock regression first failed because Compose and
  migration helpers resolved an ad hoc uv environment. The first complete clean
  rehearsal then reached every functional assertion but returned exit 1 because
  the root-running API container left root-owned bytecode in its temporary bind
  mount and the cleanup trap could not remove it.
- Runtime and migration commands now use frozen `uv.lock` resolution. The API
  container runs as the invoking UID/GID with a writable temporary uv cache, so
  the reserved project can cleanly remove its bind mount and volume on success
  or failure.
- `scripts/compose_lifecycle_check.sh` exported a staged commit tree into a
  temporary clean source, installed 31 Python and 261 JavaScript packages from
  the committed locks, migrated all eight Alembic revisions, and synchronized
  343 canonical vocabulary records. Its Chromium flow created one published
  problem/revision/snapshot, learner attempt, feedback record, and assessment
  decision through the deployed API, Learn, and Studio boundaries.
- Counts for vocabulary, problems, revisions, snapshots, attempts, feedback,
  and decisions were byte-for-byte identical before and after stopping all
  services and restarting without deleting the named volume. The public problem
  and assessed queue record remained queryable.
- An injected unknown Alembic revision made explicit migration fail and API
  readiness return the safe 503 contract. Restoring the disposable schema
  marker restored API, Learn, and Studio health. Runtime port inspection proved
  loopback database/API/Studio exposure and internal `http://api:8000` use;
  `.env.example` coverage and the absence of Redis, Celery, Docling, MinIO,
  vector, and GPU services also passed. The final isolated run exited 0 and
  removed only `ioai-r0-system` resources.
- Bash syntax, Compose rendering, focused ESLint, and all nine foundation stack
  tests passed. Linux is the validated platform; Docker Desktop filesystem and
  networking behavior remain explicitly unverified.

### `R0-09014`

- Red observed: the safety regression invoked the legacy unconfirmed `reset`
  branch and proved it immediately ran broad `docker compose down -v`; this
  deleted and recreated the local development PostgreSQL volume. No project
  backup existed, so the previous local records were not recoverable. Source
  files and the separate integration-test volume were unaffected. The test was
  changed to non-executing policy inspection before the replacement was added.
- Restore now accepts only a new `ioai_restore_*` database plus exact repeated
  confirmation, refuses the active `ioai` database and existing targets, and
  removes a partially restored target on failure. Development reset requires
  the exact volume name twice, verifies that it is the running PostgreSQL data
  mount, removes that one volume without a broad `down -v`, then runs the normal
  migrate/synchronize/start path.
- The isolated `ioai-r0-recovery` rehearsal migrated the full eight-revision
  chain and synchronized 343 canonical records. Its API fixture produced one
  stable problem, two revisions, two current/historical snapshots, six
  editorial transitions, one snapshot-bound attempt, one feedback record, and
  two append-only assessment decisions including a correction.
- A PostgreSQL custom-format, no-owner/no-privilege logical dump restored only
  into `ioai_restore_verify`. Counts and deterministic full-row digests matched
  for `alembic_version`, vocabulary, problems, revisions, transitions,
  snapshots, attempts, feedback, and decisions. The target database and
  recovery project/volume were removed after the pass.
- The runbook states that provider, retention, and off-host scheduling remain
  deployment decisions and that browser-local progress/receipt indexes are not
  recoverable from PostgreSQL. Bash syntax, Compose rendering, ESLint, and all
  11 foundation-stack tests passed.
