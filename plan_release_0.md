# Release 0 Delivery Plan

## How to use this plan

- One checklist item is one meaningful Git commit unless the item explicitly
  says it is a release checkpoint.
- Check an item only after its acceptance conditions are met and relevant
  quality gates pass. Include the checkbox update in that step's commit.
- Keep every commit reviewable and green. For behavior changes, observe a
  failing test first, implement the minimum passing code, refactor, then commit.
- Do not batch unrelated checklist items into one commit. If a step grows too
  large, split it here before implementing it.
- Use conventional, imperative commit subjects such as
  `feat(authoring): create draft problem`.
- Record material scope or architecture decisions in the relevant Release 0
  document before implementation.
- Follow `AGENTS.md`, `code_standard.md`, `master_plan.md`,
  `ui_release_0.md`, and `vocab.md` throughout.

## Completion gates for every implementation step

Before checking an implementation item:

1. The expected behavior and linked user story are clear.
2. The smallest relevant test was observed failing for the expected reason.
3. The minimum implementation makes that test pass.
4. Refactoring leaves all affected tests green.
5. Formatting, linting, and type checks pass for the affected workspace.
6. API, migration, fixture, and documentation changes are included when needed.
7. The commit contains no secrets, local artifacts, or unrelated changes.

## Phase 0 — Repository and governance baseline

- [x] **R0-000 — Initialize the Git baseline.** Confirm the repository uses the
  `main` branch; add `.gitignore`; commit `AGENTS.md`, `code_standard.md`,
  `master_plan.md`, `ui_release_0.md`, `vocab.md`, and this delivery plan as the
  governing Release 0 baseline. Suggested commit:
  `chore(repo): initialize release 0 planning baseline`.
- [x] **R0-001 — Add repository contribution guidance.** Create a concise
  `README.md` describing the product, governing documents, planned workspace
  layout, prerequisite tool versions, and the rule that commands must use `uv`
  or `pnpm`. Do not claim setup commands work before scaffolding exists.
  Suggested commit: `docs(repo): add release 0 contribution guide`.
- [x] **R0-002 — Add decision and traceability indexes.** Create a lightweight
  `docs/decisions/README.md` for architecture decision records and a traceability
  table mapping user-story IDs to analysis, design, implementation, and tests.
  Suggested commit: `docs(governance): add decision and traceability indexes`.

## Phase 1 — Requirements in user stories

Deliverable: `requirement_release_0.md`.

- [x] **R0-010 — Establish the requirements document.** Define Release 0 goals,
  personas, assumptions, terminology, in-scope behavior, explicit exclusions,
  success measures, story-ID convention, and acceptance-criteria format.
  Reconcile scope with `master_plan.md` and `ui_release_0.md`. Suggested commit:
  `docs(requirements): define release 0 scope and personas`.
- [x] **R0-011 — Specify learner discovery stories.** Add user stories and
  Given/When/Then acceptance criteria for viewing published problems, stage
  selection, bilingual search, hierarchical topic filtering, sorting,
  responsive table/cards, empty/error states, and permanent URLs. Suggested
  commit: `docs(requirements): add learner discovery stories`.
- [x] **R0-012 — Specify learner solving-loop stories.** Add stories for opening
  a problem, viewing objectives and prerequisites, submitting each accepted
  Release 0 response type, receiving scoring feedback, recording anonymous
  local progress, sending feedback, and continuing to the editorially
  recommended problem. Decide the exact Release 0 task-type and compute-tier
  availability here. Suggested commit:
  `docs(requirements): add learner solving stories`.
- [x] **R0-013 — Specify authoring stories.** Add stories for the author problem
  list, creating and editing a structured draft, bilingual content, canonical
  metadata selection, prerequisites, response/scoring configuration, autosave,
  recovery, validation, and learner-format preview. Suggested commit:
  `docs(requirements): add authoring stories`.
- [x] **R0-014 — Specify editorial and publication stories.** Add stories for
  submitting a draft, requesting changes, approving, publishing, revising a
  published problem, archiving, audit notes, validation blockers, unique slugs,
  stable URLs, and strict draft/public isolation. Suggested commit:
  `docs(requirements): add editorial workflow stories`.
- [x] **R0-015 — Specify operational and quality requirements.** Add measurable
  requirements for accessibility, responsive widths, performance budgets,
  browser support, data integrity, privacy, local-only Studio exposure, backup
  assumptions, observability, deterministic builds, migration safety, and test
  coverage of changed behavior. Suggested commit:
  `docs(requirements): add release 0 quality requirements`.
- [x] **R0-016 — Review and baseline requirements.** Resolve duplicates and
  contradictions, number all acceptance criteria, identify deferred stories,
  and complete the requirements-to-source traceability table. Record unresolved
  product decisions instead of guessing. Suggested commit:
  `docs(requirements): baseline release 0 requirements`.

## Phase 2 — Analysis

Deliverable: `analysis_release_0.md`.

- [ ] **R0-020 — Analyze actors, context, and system boundary.** Describe learner,
  author, reviewer, and curriculum-owner responsibilities; external systems;
  trust boundaries; anonymous use; local Studio access; and what remains outside
  Release 0. Link every conclusion to requirement IDs. Suggested commit:
  `docs(analysis): define actors and system boundary`.
- [ ] **R0-021 — Analyze the domain model.** Define problem, problem revision,
  published snapshot, vocabulary record, prerequisite, scoring component,
  editorial transition, learner attempt, local progress, recommendation, and
  feedback. Distinguish learner status, learning evidence, editorial status,
  and publication state. Suggested commit:
  `docs(analysis): model release 0 domain concepts`.
- [ ] **R0-022 — Analyze vocabulary ingestion and governance.** Explain how
  `vocab.md` becomes deterministic structured data, how composite identity and
  topic hierarchy are validated, how bilingual aliases resolve, how Release 0
  availability differs from canonical completeness, and how drift is detected.
  Suggested commit: `docs(analysis): define vocabulary data flow`.
- [ ] **R0-023 — Analyze learner and editorial workflows.** Add state diagrams or
  tables for learner browse/solve/continue and author draft/review/publish/revise
  flows, including failures, retries, concurrency, autosave recovery, and
  idempotency expectations. Suggested commit:
  `docs(analysis): map learner and editorial workflows`.
- [ ] **R0-024 — Analyze data access and public isolation.** Identify public and
  author query paths, revision consistency rules, transaction boundaries,
  permanent-slug behavior, local-progress ownership, feedback data, and ways a
  draft could accidentally leak. Suggested commit:
  `docs(analysis): assess data access and draft isolation`.
- [ ] **R0-025 — Analyze quality risks and test strategy.** Build a risk-based
  test matrix covering domain rules, migrations, PostgreSQL repositories, API
  contracts, generated clients, component behavior, critical browser flows,
  accessibility, and Docker Compose startup. Include security risks created by
  operating without authentication. Suggested commit:
  `docs(analysis): define risk based test strategy`.
- [ ] **R0-026 — Baseline the analysis.** Review analysis against every accepted
  user story, record assumptions and open decisions, and update traceability.
  Suggested commit: `docs(analysis): baseline release 0 analysis`.

## Phase 3 — Design

Deliverable: `design_release_0.md`. Reference `ui_release_0.md`; do not duplicate
its detailed visual specification unnecessarily.

- [ ] **R0-030 — Design the system architecture.** Define the monorepo boundaries,
  learner and Studio applications, FastAPI entrypoint, application use cases,
  domain modules, ports/adapters, PostgreSQL access, generated OpenAPI client,
  and dependency direction. Include a context and container diagram. Suggested
  commit: `docs(design): define release 0 architecture`.
- [ ] **R0-031 — Design application functions and use cases.** Specify inputs,
  outputs, authorization assumptions, transactions, domain errors, and ports for
  vocabulary import, problem drafting, validation, editorial transitions,
  publication, public listing/detail, submission/scoring, feedback, and next-
  problem recommendation. Suggested commit:
  `docs(design): specify application use cases`.
- [ ] **R0-032 — Design the API contract.** Define `/api/v1` public resources and
  `/api/v1/author` commands, request/response schemas, pagination, filtering,
  sorting, stable error codes, idempotency, draft-safe public projections, and
  OpenAPI-to-TypeScript generation. Suggested commit:
  `docs(design): specify release 0 api contract`.
- [ ] **R0-033 — Design the PostgreSQL model.** Provide an ER diagram, tables,
  keys, composite vocabulary identity, topic relationships, revision/snapshot
  model, editorial history, scoring weights, feedback, indexes, constraints,
  transaction rules, migration strategy, and seed strategy. Suggested commit:
  `docs(design): define release 0 database model`.
- [ ] **R0-034 — Consolidate the UI implementation design.** Map learner and
  author routes, pages, server/client component boundaries, state ownership,
  local progress, URL filters, form architecture, autosave, preview, responsive
  behavior, accessibility, and generated API types back to `ui_release_0.md`.
  Suggested commit: `docs(design): map release 0 frontend architecture`.
- [ ] **R0-035 — Design Docker Compose and local operations.** Specify services,
  health checks, networks, named volumes, environment variables, startup order,
  ports, migrations, seed commands, and development/CI profiles. The base
  Release 0 stack must include PostgreSQL, FastAPI, learner Next.js, and Studio
  Next.js. Add Redis/Celery or MinIO only behind explicit profiles if an accepted
  requirement needs them. Suggested commit:
  `docs(design): define docker compose topology`.
- [ ] **R0-036 — Design testing, observability, and failure handling.** Specify
  unit/integration/E2E boundaries, PostgreSQL test isolation, fixture ownership,
  structured logs, request IDs, health/readiness endpoints, safe error mapping,
  backup/restore rehearsal, and quality commands. Suggested commit:
  `docs(design): define verification and operations`.
- [ ] **R0-037 — Review and baseline the design.** Verify every design element
  traces to accepted requirements and analysis, remove speculative components,
  record ADRs for material trade-offs, and update the traceability index.
  Suggested commit: `docs(design): baseline release 0 design`.

## Phase 4 — Executable project foundation

All behavior-bearing implementation steps below use red–green–refactor before
their commit.

- [ ] **R0-040 — Scaffold the Python backend.** Add Python 3.12 constraints,
  `pyproject.toml`, `uv.lock`, the `backend/src/ioai` package boundaries, pytest,
  Ruff, and the selected type checker. Add a smoke test that imports the package.
  Suggested commit: `build(backend): scaffold uv python workspace`.
- [ ] **R0-041 — Scaffold the frontend workspace.** Add `pnpm-workspace.yaml`,
  root scripts, lockfile, strict shared TypeScript configuration, ESLint, Vitest,
  and empty `learn`, `studio`, `api-client`, and `ui` packages with passing smoke
  tests. Suggested commit: `build(frontend): scaffold pnpm workspace`.
- [ ] **R0-042 — Add the learner application shell.** Create the Next.js App
  Router application on port 3000 with IOAI Learn metadata, Tailwind, shadcn/ui
  foundations, accessible navigation, and a tested `/problems` route shell.
  Suggested commit: `feat(learn): add learner application shell`.
- [ ] **R0-043 — Add the Studio application shell.** Create the loopback-bound
  Next.js application on port 3001 with distinct IOAI Studio branding and a
  tested `/author/problems` route shell. Suggested commit:
  `feat(studio): add author application shell`.
- [ ] **R0-044 — Add the FastAPI application shell.** Add typed settings,
  application factory, safe error mapping, request IDs, `/health/live`, and
  `/health/ready`, with pytest coverage and deterministic OpenAPI generation.
  Suggested commit: `feat(api): add fastapi application shell`.
- [ ] **R0-045 — Add PostgreSQL persistence infrastructure.** Configure
  SQLAlchemy 2 sessions, transaction handling, Alembic, database settings, and a
  first connectivity integration test against PostgreSQL. Suggested commit:
  `feat(db): add sqlalchemy and alembic foundation`.
- [ ] **R0-046 — Add the base Docker Compose environment.** Add PostgreSQL,
  FastAPI, learner, and Studio services with health checks, persistent database
  volume, loopback Studio binding, environment examples, and documented start/
  stop/reset commands. Prove the stack reaches healthy state. Suggested commit:
  `build(dev): add release 0 docker compose stack`.
- [ ] **R0-047 — Add CI quality gates.** Run backend formatting/lint/types/tests,
  frontend lint/types/unit tests/builds, migration validation, generated-contract
  drift checks, and focused integration tests with dependency caching. Suggested
  commit: `ci: add release 0 quality pipeline`.

## Phase 5 — Canonical vocabulary vertical slice

- [ ] **R0-050 — Define vocabulary domain values and invariants.** Test first,
  then implement typed vocabulary identity, bilingual labels, aliases, status,
  and topic parent references without framework imports. Suggested commit:
  `feat(vocabulary): define canonical domain model`.
- [ ] **R0-051 — Build deterministic vocabulary extraction.** Test first, then
  implement the generator/importer from `vocab.md` to structured data. Reject
  missing explicit relationships instead of inferring them from headings.
  Suggested commit: `feat(vocabulary): generate structured vocabulary data`.
- [ ] **R0-052 — Validate vocabulary graphs and uniqueness.** Add failing cases,
  then implement checks for composite identity, missing parents, self-parenting,
  cycles, ambiguous aliases, and duplicate labels within a branch. Suggested
  commit: `feat(vocabulary): validate taxonomy invariants`.
- [ ] **R0-053 — Persist and migrate vocabulary records.** Add Alembic tables,
  PostgreSQL constraints/indexes, an idempotent synchronization use case, and
  integration tests proving updates do not repurpose canonical identities.
  Suggested commit: `feat(vocabulary): persist canonical records`.
- [ ] **R0-054 — Expose vocabulary read APIs.** Add public and author-safe
  hierarchical vocabulary queries with bilingual search, alias matching, and an
  explicit include-descendants option. Generate and consume updated client
  types. Suggested commit: `feat(vocabulary): expose taxonomy api`.
- [ ] **R0-055 — Implement Release 0 availability policy.** Test and implement a
  central policy for enabled stages, task types, compute tiers, and scoring
  methods based on approved requirements; canonical future values remain stored
  but cannot be published. Suggested commit:
  `feat(vocabulary): enforce release 0 availability`.

## Phase 6 — Problem domain and authoring

- [ ] **R0-060 — Define the problem aggregate.** Test first, then implement IDs,
  stable slug rules, bilingual titles/content, observable objectives, stage and
  difficulty, competencies, topics, prerequisites, expected time, modality,
  resources, response configuration, and decimal-safe scoring components.
  Suggested commit: `feat(problems): define problem aggregate`.
- [ ] **R0-061 — Add problem persistence and migrations.** Design migrations for
  problems, revisions, metadata associations, prerequisites, response/scoring
  configuration, and optimistic versioning; add PostgreSQL repository tests.
  Suggested commit: `feat(problems): persist drafts and revisions`.
- [ ] **R0-062 — Implement create-draft API.** Add the application use case,
  author endpoint, Pydantic contracts, error cases, OpenAPI update, generated
  client, and tests. Suggested commit: `feat(authoring): create draft problems`.
- [ ] **R0-063 — Implement edit and autosave API.** Add partial draft updates,
  optimistic concurrency, conflict responses, recoverable failures, generated
  client changes, and integration tests. Suggested commit:
  `feat(authoring): update drafts safely`.
- [ ] **R0-064 — Build the author problem list.** Implement status tabs, search,
  filters, validation summary, row actions, loading/empty/error states, and
  component tests at `/author/problems`. Suggested commit:
  `feat(studio): build author problem list`.
- [ ] **R0-065 — Build editor basics and content sections.** Implement bilingual
  basics, objectives, structured content blocks, hints, explanation, feedback
  prompt, visible validation, autosave state, and unsaved-change protection with
  component tests. Suggested commit:
  `feat(studio): build problem content editor`.
- [ ] **R0-066 — Build response and scoring sections.** Implement only approved
  Release 0 response forms, scoring weights, response-specific validation, and
  accessible repeated-field interactions with component tests. Suggested
  commit: `feat(studio): configure responses and scoring`.
- [ ] **R0-067 — Build curriculum metadata section.** Add canonical selectors,
  vocabulary-type disambiguation, hierarchical topic breadcrumbs, descendant
  control, up-to-three secondary competencies, and typed prerequisites.
  Suggested commit: `feat(studio): edit curriculum metadata`.
- [ ] **R0-068 — Build resource and release-policy validation.** Add expected
  minutes, modalities, compute/runtime limits, network policy, and clear errors
  for unavailable Release 0 values. Suggested commit:
  `feat(studio): validate problem resources`.
- [ ] **R0-069 — Add complete draft validation.** Implement a domain/application
  validation report grouped by content, curriculum, assessment, resources, and
  publication; link Studio errors to fields and prove invalid drafts cannot move
  to publication. Suggested commit:
  `feat(authoring): validate complete drafts`.

## Phase 7 — Editorial review and publication

- [ ] **R0-070 — Implement editorial transitions.** Test valid and invalid state
  changes, notes, timestamps, and concurrency; add submit-for-review, request-
  changes, and approve endpoints plus generated client updates. Suggested
  commit: `feat(editorial): add review workflow`.
- [ ] **R0-071 — Build the Studio review experience.** Add validation checklist,
  editorial notes/history, state-sensitive primary actions, confirmation and
  error behavior, and accessible tests. Suggested commit:
  `feat(studio): build editorial review controls`.
- [ ] **R0-072 — Implement learner-format draft preview.** Render unsaved editor
  state in the learner layout with desktop/mobile widths, disabled public links,
  missing-translation warnings for authors, and the persistent non-public
  banner. Suggested commit: `feat(studio): add draft learner preview`.
- [ ] **R0-073 — Implement atomic publication.** Validate and approve a revision,
  create an immutable public snapshot, preserve the permanent slug, write the
  audit transition, and prove rollback on failure. Suggested commit:
  `feat(publication): publish approved revisions`.
- [ ] **R0-074 — Implement revision and archive behavior.** Editing a published
  problem creates a new draft without changing the live snapshot; archival
  removes it from discovery according to requirements without reusing its URL.
  Suggested commit: `feat(publication): revise and archive problems`.
- [ ] **R0-075 — Prove public/draft isolation at the boundary.** Add adversarial
  repository and API integration tests showing public list/detail/search never
  reveal drafts, pending revisions, hidden answers/tests, editorial notes, or
  internal object metadata. Suggested commit:
  `test(publication): verify public data isolation`.

## Phase 8 — Learner problem library and solving loop

- [ ] **R0-080 — Implement public problem-list API.** Add published-only
  pagination, editorial-path default ordering, title/objective/topic search,
  stage/difficulty/topic/type/competency/time/compute filters, stable query
  semantics, and integration tests. Suggested commit:
  `feat(learn): expose published problem library`.
- [ ] **R0-081 — Build stage selection and recommendation card.** Implement
  enabled/coming-next stages, editorial default recommendation, local-history
  continuation, “Why this?” explanation, and component tests. Suggested commit:
  `feat(learn): add stage and recommendation controls`.
- [ ] **R0-082 — Build search and hierarchical filters.** Implement URL-backed
  search, compact filters, top-level topic-family shortcuts, searchable tree,
  aliases, active-filter tokens, include-descendants behavior, clear action, and
  tests. Suggested commit: `feat(learn): add problem discovery filters`.
- [ ] **R0-083 — Build the desktop problem table.** Implement all required
  columns, paired stage/difficulty, separate status/evidence, two-topic limit,
  sticky header, row navigation, accessible focus, sorting, and tests. Suggested
  commit: `feat(learn): build problem table`.
- [ ] **R0-084 — Build responsive problem cards and states.** Implement the
  specified breakpoints, mobile filter sheet, compact cards, loading skeleton,
  no-history/no-results/error states, and tests at 360, 768, 1024, and 1440 px.
  Suggested commit: `feat(learn): add responsive library states`.
- [ ] **R0-085 — Build the learning-path sidebar.** Add local weekly goal,
  current path, prerequisite review, recent completions, and suggested topics
  without implying mastery or unsupported personalization. Suggested commit:
  `feat(learn): add learning path sidebar`.
- [ ] **R0-086 — Implement public problem-detail API and page.** Return a safe
  published projection and render title, paired stage/difficulty, objective,
  prerequisites, statement, examples/data, response area, hints, explanation
  rules, taxonomy details, and stable metadata. Suggested commit:
  `feat(learn): build public problem page`.
- [ ] **R0-087 — Implement lightweight submission and scoring.** Add the accepted
  Release 0 submission contracts, domain scoring policies, safe feedback,
  attempt recording where required, and unit/integration/component tests. Never
  expose hidden answers or tests. Suggested commit:
  `feat(scoring): add release 0 submissions`.
- [ ] **R0-088 — Implement anonymous local progress.** Persist only approved
  device-local task status, evidence display data, timing/hint counters, and
  recent activity; degrade gracefully when storage is unavailable. Suggested
  commit: `feat(learn): persist anonymous progress`.
- [ ] **R0-089 — Implement feedback and continue-next loop.** Add the per-problem
  feedback API/UI, abuse-resistant validation appropriate to the no-auth pilot,
  success/error states, and next-problem transition measurement. Suggested
  commit: `feat(learn): complete feedback and continuation loop`.

## Phase 9 — Integration and system verification

- [ ] **R0-090 — Harden migration integration tests.** Verify a clean PostgreSQL
  database upgrades to head, seed/import is idempotent, constraints protect
  invariants, representative downgrade behavior is safe, and the application
  starts only after migrations are ready. Suggested commit:
  `test(db): verify migrations and canonical seeds`.
- [ ] **R0-091 — Add API integration coverage.** Exercise success, validation,
  conflict, idempotency, pagination, filtering, workflow, scoring, feedback, and
  safe-error contracts through FastAPI against PostgreSQL. Suggested commit:
  `test(api): cover release 0 contracts`.
- [ ] **R0-092 — Add OpenAPI/client contract verification.** Fail CI on generated
  contract drift and test representative frontend requests against the running
  API, including stable error decoding. Suggested commit:
  `test(contract): verify frontend api compatibility`.
- [ ] **R0-093 — Add learner Playwright workflow.** Test browse → filter → open
  permanent problem → submit → receive feedback → continue, including a mobile
  viewport and local-progress restoration. Suggested commit:
  `test(e2e): cover learner release 0 journey`.
- [ ] **R0-094 — Add author Playwright workflow.** Test draft → autosave →
  validate → preview → submit → request/resolve changes → approve → publish →
  verify public visibility and revision isolation. Suggested commit:
  `test(e2e): cover editorial release 0 journey`.
- [ ] **R0-095 — Verify accessibility and responsive behavior.** Add automated
  accessibility checks to critical pages, perform documented keyboard/focus
  verification, and capture acceptance evidence for all required widths.
  Suggested commit: `test(ui): verify accessibility and breakpoints`.
- [ ] **R0-096 — Verify Docker Compose from a clean state.** Build all images,
  start the stack with documented commands, pass health checks, migrate/seed a
  fresh volume, run smoke flows, restart without data loss, and document any
  platform-specific limitations. Suggested commit:
  `test(system): verify clean compose startup`.

## Phase 10 — Refactor and release readiness

- [ ] **R0-100 — Refactor backend boundaries with tests green.** Remove
  duplication and framework leakage, tighten ports and names, simplify
  transactions and error mapping, delete dead code, and keep the full backend
  suite green after each small change. Suggested commit:
  `refactor(backend): clarify release 0 boundaries`.
- [ ] **R0-101 — Refactor frontend boundaries with tests green.** Consolidate
  genuinely shared primitives, remove duplicated contract types and brittle
  state, simplify components/hooks, and keep unit/E2E tests green. Suggested
  commit: `refactor(frontend): simplify release 0 interfaces`.
- [ ] **R0-102 — Tune critical queries and page performance.** Measure before
  changing; add justified PostgreSQL indexes, eliminate avoidable query or render
  work, verify pagination and loading behavior, and record results against the
  requirements budget. Suggested commit:
  `perf(release): meet release 0 performance budget`.
- [ ] **R0-103 — Rehearse backup, restore, and failure recovery.** Verify
  PostgreSQL backup/restore for representative content, document recovery of
  failed publication/autosave scenarios, and keep secrets and user data out of
  fixtures and logs. Suggested commit:
  `docs(operations): add release 0 recovery runbook`.
- [ ] **R0-104 — Finalize developer and operator documentation.** Update README,
  environment reference, Compose commands, migrations, vocabulary sync,
  OpenAPI/client generation, test commands, seed workflow, troubleshooting, and
  pilot deployment guidance. Suggested commit:
  `docs(release): finalize release 0 runbook`.
- [ ] **R0-105 — Run the full release candidate gate.** From a clean checkout,
  install from both lockfiles, start Docker Compose, migrate and seed, run all
  format/lint/type/unit/integration/E2E/build checks, inspect migration and
  contract drift, and record exact results in a release checklist. Suggested
  commit: `chore(release): record release 0 verification`.
- [ ] **R0-106 — Complete pilot acceptance review.** Trace every accepted user
  story to passing evidence, record deferred items without silently expanding
  scope, verify 20–30 reviewed problems and feedback collection, update all
  documents, and mark Release 0 ready for the 10–20 learner/teacher pilot.
  Suggested commit: `chore(release): approve release 0 pilot`.
