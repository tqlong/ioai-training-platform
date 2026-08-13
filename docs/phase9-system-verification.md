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
| FastAPI | Versioned public and author routers for vocabulary, proposals, problems, publication, submissions, feedback, and manual assessment; health routes and safe error DTOs | Most HTTP tests use injected fakes; a complete real-app/real-PostgreSQL contract suite is missing |
| Public isolation | Dedicated published reader, public DTOs, OpenAPI schema checks, repository tests, and `scripts/public_isolation_check.sh` | Leak-path fixtures do not yet cover every private field, stale/archive path, generated client, server fetch, and result/assessment path together |
| Generated contracts | Deterministic OpenAPI JSON, `openapi-typescript` output, vocabulary artifacts, generation script, and drift script | Handwritten client wrappers are not comprehensively exercised against a running API |
| Learn components | Unit/component coverage for URL discovery, table/cards, detail, five response forms, local progress, feedback, continuation, and submission history | No automated accessibility scanner; responsive and keyboard proof is distributed across tests and manual notes |
| Studio components | Unit/component coverage for list/editor sections, validation, preview, editorial review, rubric editor, assessment queue, and assessment decisions | No automated accessibility scanner or complete route-width regression |
| Browser workflows | `learner-solving-loop.spec.ts` and `editorial-publication.spec.ts`, including the manual-assessment path currently embedded in the learner specification | Playwright config runs Chromium desktop only; browser/mobile matrix and full performance budgets are not proved |
| Health and observability | Liveness/readiness routes, request-ID response middleware, readiness integration tests, and Compose health checks | Readiness returns a successful HTTP status when degraded; Compose waits on process startup in places; structured completion/operation events and redaction proof are absent |
| Local operations | Compose topology plus start, stop, migrate, seed, redeploy, phase-specific test, smoke, and backup/restore commands | PostgreSQL is host-published broadly, API author exposure and CORS are permissive, no clean/persisted lifecycle rehearsal exists, and restore is not verified in a disposable database |
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
| `AC-R0-015-09` | Transactional migration-DDL rollback plus unit-of-work and atomic publication rollback tests | Injected failure through the real HTTP boundary remains | `R0-09002` complete; `R0-09003` |
| `AC-R0-015-10` | Public DTO/schema isolation and guessed-ID tests | Every leak path plus a concrete no-auth topology preventing the learner surface from reaching author commands | `R0-09004`, `R0-09005` |
| `AC-R0-015-11` | Studio host port maps to `127.0.0.1:3001` and documentation rejects port-as-auth | Automated configuration/topology proof and safe API author exposure | `R0-09005`, `R0-09013` |
| `AC-R0-015-12` | Bounded progress, submission, feedback, receipt, and throttle tests | Full persistence/log review and no-auth boundary integration tests | `R0-09003`, `R0-09005`, `R0-09007` |
| `AC-R0-015-13` | Safe error DTOs, public-isolation checks, and UI safe-state assertions | Cross-route adversarial errors and structured-log redaction | `R0-09004`, `R0-09007` |
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
