# Release 0 Delivery Plan

## How to use this plan

- One checklist item is one meaningful Git commit unless the item explicitly
  says it is a release checkpoint.
- Checklist item IDs use the legacy `R0-<three digits>` form for existing
  Phase 0–2 requirement/story traceability. Phase 3 uses the expandable
  `R0-03xxx` plan-step form: `R0-03001` through `R0-03999`, ordered numerically.
  Each step remains one meaningful commit. Later detailed phases use the same
  pattern with their phase prefix; Phase 7 uses `R0-07001` through
  `R0-07999`. Plan-step IDs are
  distinct from the requirement/story IDs in `requirement_release_0.md`.
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

Analysis input and traceability rule: every conclusion, model, workflow, risk,
and recommendation in `analysis_release_0.md` must cite one or more IDs from
`requirement_release_0.md`, including `AC-R0-*` where it makes a behavioral
claim. Do not add capabilities that are listed as exclusions or deferred in
requirements section 15.3. Preserve the five approved Release 0 task types,
the `NONE`/`BROWSER`/`CPU_LIGHT` compute policy, and the unresolved Phase 3/4
implementation choices recorded in requirements section 15.3.

- [x] **R0-020 — Analyze actors and responsibilities from R0-010.** Define
  learner, author, reviewer, curriculum-owner, and local-operator goals,
  responsibilities, triggers, outputs, and failure expectations. Produce an
  actor/responsibility table linked to the applicable `R0-010` requirements.
  Suggested commit: `docs(analysis): define release 0 actors`.
- [x] **R0-021 — Analyze context and trust boundaries from R0-010 and R0-015.**
  Produce a context diagram covering learner UI, local Studio, FastAPI,
  PostgreSQL, browser-local storage, and permitted external dependencies.
  Analyze anonymous operation, loopback Studio exposure, public versus author
  boundaries, and security risks created by having no authentication. Suggested
  commit: `docs(analysis): define context and trust boundaries`.
- [x] **R0-022 — Analyze the domain model from R0-012, R0-013, R0-014, and
  R0-015.** Define the problem aggregate, revision, published snapshot,
  vocabulary record, typed prerequisite, response configuration, decimal-safe
  scoring component, editorial transition, learner attempt, device-local
  progress, recommendation, feedback, and audit note. Distinguish task status,
  learning evidence, editorial status, revision state, and publication state.
  Document cardinalities, invariants, ownership, and lifecycle. Suggested
  commit: `docs(analysis): model release 0 domain concepts`.
- [x] **R0-023 — Analyze vocabulary ingestion and governance from R0-010,
  R0-011, R0-012, R0-013, R0-015, and R0-016.** Explain the deterministic path
  from `vocab.md` to structured data; composite identity; bilingual labels and
  aliases; explicit topic parentage; missing-parent, self-parent, cycle, and
  branch-uniqueness checks; proposal handling; availability policy; and drift
  detection. Include the five approved task types, `NONE`/`BROWSER`/`CPU_LIGHT`,
  approved scoring methods, and the `NONE` modality rule. Suggested commit:
  `docs(analysis): define vocabulary data flow`.
- [x] **R0-024 — Analyze the learner discovery and solving workflow from R0-011
  and R0-012.** Map stage selection, search, hierarchy filtering, sorting,
  permanent URLs, problem reading, each accepted response type, scoring
  feedback, device-local status/evidence, problem feedback, and continue-next
  recommendation. Include empty, loading, public-data failure, malformed
  submission, delayed scoring, local-storage failure, and unavailable-policy
  outcomes. Suggested commit: `docs(analysis): map learner workflows`.
- [x] **R0-025 — Analyze the authoring workflow from R0-013.** Map draft creation,
  published-problem revision, bilingual editing, metadata and prerequisite
  selection, response/scoring configuration, autosave states, local recovery,
  optimistic-concurrency conflicts, validation, and learner preview. Identify
  state ownership, retry behavior, and the point at which each validation
  blocker is surfaced. Suggested commit: `docs(analysis): map authoring workflow`.
- [x] **R0-026 — Analyze editorial transitions and publication from R0-014.**
  Model `DRAFT` -> `IN_REVIEW` -> `CHANGES_REQUESTED` -> `APPROVED` ->
  `PUBLISHED` -> `ARCHIVED`, required notes, audit history, publication
  idempotency, approval/publication separation, revision creation, stable slugs,
  and archive/republication behavior. Document invalid transitions and partial
  failure outcomes without adding states. Suggested commit:
  `docs(analysis): model editorial publication workflow`.
- [x] **R0-027 — Analyze data access and strict public isolation from R0-011,
  R0-012, R0-013, R0-014, and R0-015.** Map public reads, submissions,
  recommendations, feedback, author commands, preview reads, and persistence
  paths. Identify revision consistency, transaction boundaries, idempotency
  keys, local-progress ownership, bounded anonymous feedback, and every route or
  query shape through which drafts, unapproved revisions, answers, stack traces,
  provider errors, or object keys could leak. State the repository/API boundary
  that must enforce published-only projections. Suggested commit:
  `docs(analysis): assess data access and draft isolation`.
- [x] **R0-028 — Build the risk and verification analysis from R0-015 and all
  affected story groups.** Create a risk-ranked matrix for domain invariants,
  vocabulary drift, migrations and PostgreSQL constraints, transaction safety,
  API contracts and generated clients, scoring, autosave, progress, feedback
  abuse, responsive/accessibility behavior, performance, browser support,
  Docker health, backup/restore, observability, deterministic builds, and no-auth
  security. Map each high-risk item to the smallest test boundary and record the
  required failing-first observation for behavior changes. Suggested commit:
  `docs(analysis): define release 0 risks and verification`.
- [x] **R0-029 — Baseline the analysis against requirement_release_0.md.** Review
  `analysis_release_0.md` against every accepted story group (`R0-010` through
  `R0-016`) and every numbered acceptance-criteria range. Remove duplicate
  concepts, confirm exclusions and deferred decisions are not reintroduced,
  record assumptions and open Phase 3/4 decisions without guessing, and update
  `docs/decisions/README.md` with analysis traceability. Include a
  requirement-to-analysis matrix and list criteria whose proof is deferred to
  design or implementation. Suggested commit:
  `docs(analysis): baseline release 0 analysis`.

## Phase 3 — Design

Deliverable: `design_release_0.md`.

Design input and traceability rule: read and cite both
`requirement_release_0.md` and `analysis_release_0.md` for every design
decision. Requirements define accepted behavior and deferred scope; analysis
defines actors, domain invariants, workflow semantics, public isolation risks,
test boundaries, and open decisions. Reference `ui_release_0.md` for interface
behavior without duplicating its detailed visual specification. Every design
step must identify which choices are resolved, which are open, and which are
explicitly excluded from Release 0.

- [x] **R0-03001 — Design system context and boundaries from R0-010, R0-015,
  analysis sections 1-3, and 11.** Define actors, external dependencies,
  learner/Studio/API/PostgreSQL/browser-local boundaries, no-auth assumptions,
  loopback exposure, and the context/container diagrams. Exclude deferred
  services and features. Suggested commit: `docs(design): define system context`.
- [x] **R0-03002 — Design monorepo architecture and dependency direction from
  R0-010, R0-015, analysis sections 3-4, and 11.** Define backend/frontend
  boundaries, learner and Studio applications, FastAPI entrypoint, domain,
  application, adapter, persistence, worker, and generated-client boundaries.
  Show allowed dependency direction and actor-to-component ownership. Suggested
  commit: `docs(design): define release 0 architecture`.
- [x] **R0-03003 — Design domain modules and aggregate boundaries from R0-012,
  R0-013, R0-014, R0-015, analysis section 4, and 11.** Map problem/revision/
  snapshot, vocabulary, prerequisite, response, scoring, editorial history,
  attempt, progress, recommendation, feedback, and audit concepts to domain
  modules. Preserve cardinalities, state-dimension separation, and framework-free
  domain rules. Suggested commit: `docs(design): define domain boundaries`.
- [x] **R0-03004 — Design application use cases and ports from R0-012 through
  R0-015 and analysis sections 6-9.** Specify typed inputs, outputs, port
  dependencies, transaction intent, safe domain errors, idempotency, version/
  conflict behavior, and public versus author projections for vocabulary sync,
  drafting, validation, preview, editorial transitions, publication, listing,
  detail, submission/scoring, feedback, progress, and recommendation. Suggested
  commit: `docs(design): specify release 0 application use cases`.
- [x] **R0-03005 — Design vocabulary ingestion and availability policy from
  R0-010, R0-011, R0-012, R0-013, R0-016, analysis section 5, and 11.** Define
  parser/import boundaries, structured artifact, composite identity, explicit
  topic graph validation, bilingual/alias search, proposals, drift detection,
  synchronization, and central policy for the five task types,
  `NONE`/`BROWSER`/`CPU_LIGHT`, scoring methods, and modality rules. Suggested
  commit: `docs(design): define vocabulary and release policy integration`.
- [x] **R0-03006 — Design public read and learner command contracts from R0-011,
  R0-012, R0-015, analysis sections 6 and 9.** Define `/api/v1` list/detail,
  search/filter/sort/pagination, permanent URLs, recommendations, submissions,
  scoring feedback, local-progress interaction, and problem feedback. Include
  safe public projections, URL state, validation errors, request IDs, bounded
  inputs, and idempotency. Suggested commit: `docs(design): specify learner api`.
- [x] **R0-03007 — Design author and editorial command contracts from R0-013,
  R0-014, R0-015, analysis sections 7-9.** Define `/api/v1/author` draft,
  autosave/recovery, validation, preview, review, request-changes, approval,
  publication, revision, and archive commands. Include notes, optimistic
  versions, conflict errors, publication idempotency, preview isolation, and
  author-safe response schemas. Suggested commit: `docs(design): specify author api`.
- [x] **R0-03008 — Design OpenAPI and generated-client governance from R0-011
  through R0-015, analysis sections 9-10.** Define deterministic OpenAPI
  generation, schema ownership, TypeScript client generation, compatibility
  checks, drift detection, error-code stability, and the contract test that
  prevents draft fields or ORM objects from entering public schemas. Suggested
  commit: `docs(design): govern api contract generation`.
- [x] **R0-03009 — Design the PostgreSQL conceptual model from R0-012 through
  R0-015 and analysis sections 4, 8, and 9.** Provide ER/table designs for
  problems, revisions, snapshots, vocabulary, topic relationships,
  prerequisites, response/scoring configuration, editorial history, attempts,
  feedback, and operational metadata. Define composite keys, unique slugs,
  constraints, indexes, and deterministic seed ownership. Suggested commit:
  `docs(design): define release 0 database model`.
- [x] **R0-03010 — Design transaction, concurrency, and migration strategy from
  R0-013 through R0-015, analysis sections 7-10, and open decisions in section
  11.** Choose transaction boundaries, isolation/locking, optimistic versioning,
  atomic publication, snapshot consistency, submission/autosave idempotency,
  rollback behavior, Alembic migration discipline, and migration/seed safety.
  Suggested commit: `docs(design): define persistence consistency strategy`.
- [x] **R0-03011 — Design public isolation, privacy, and error boundaries from
  R0-014, R0-015, analysis sections 3 and 9-10.** Make published-only
  projections unavoidable below HTTP routing; separate public/author query
  paths; define preview, build, and cache boundaries; specify no-auth exposure,
  bounded anonymous data, redaction, safe errors, and leak-path checks. Suggested
  commit: `docs(design): enforce public isolation and safe boundaries`.
- [x] **R0-03012 — Design learner frontend architecture from R0-011, R0-012,
  R0-015, `ui_release_0.md`, and analysis section 6.** Map learner routes,
  page hierarchy, server/client ownership, generated API types, URL filters,
  stage/recommendation state, local progress, list/table/card behavior,
  submission/feedback/continue states, accessibility, responsive widths, and
  loading/error behavior. Suggested commit: `docs(design): map learner frontend`.
- [x] **R0-03013 — Design Studio frontend architecture from R0-013, R0-014,
  R0-015, `ui_release_0.md`, and analysis section 7.** Map author routes,
  structured form sections, canonical pickers, prerequisites, response/scoring
  forms, autosave/recovery, validation, preview banner, review controls,
  publication confirmation, focus behavior, responsive layout, and distinct
  Studio branding. Suggested commit: `docs(design): map studio frontend`.
- [x] **R0-03014 — Design Docker Compose and local operations from R0-015,
  analysis sections 2, 3, 9-10, and section 11.** Specify PostgreSQL, FastAPI,
  learner, and Studio services; health/readiness, networks, volumes, env vars,
  startup/migration/seed order, ports, loopback binding, development/CI
  profiles, backup/restore rehearsal, and safe reset. Keep Redis/Celery/MinIO
  excluded unless an accepted requirement creates a concrete need. Suggested
  commit: `docs(design): define docker compose topology`.
- [x] **R0-03015 — Design verification, observability, and failure handling from
  R0-015, analysis sections 9-10, and all affected criteria.** Define domain,
  application, vocabulary, PostgreSQL/Alembic, API contract, frontend,
  Playwright, and operations test ownership; fixtures/isolation; red-green-
  refactor evidence; structured logs, IDs, redaction, health/readiness, retries,
  safe errors, backup/restore, performance, browser, accessibility, and contract
  drift gates. Resolve open backup/observability decisions or record ADRs.
  Suggested commit: `docs(design): define verification and operations`.
- [x] **R0-03016 — Review and baseline the design against both governing
  artifacts.** Verify every design element maps to `requirement_release_0.md`
  R0-010 through R0-016, the corresponding `analysis_release_0.md` section,
  and each acceptance-criteria range. Remove speculative features and
  contradictions; confirm public/draft isolation, five-type policy, compute
  limits, stable URLs, separate state dimensions, no-auth assumptions, and
  deferred decisions. Record material trade-offs as ADRs, update
  `docs/decisions/README.md`, and include requirement-to-design and
  analysis-to-design matrices plus implementation proof deferred to Phase 4+.
  Suggested commit: `docs(design): baseline release 0 design`.

## Phase 4 — Executable project foundation

All behavior-bearing implementation steps below use red–green–refactor before
their commit. Every step must read and trace to `requirement_release_0.md`,
`analysis_release_0.md`, and `design_release_0.md`; no step may introduce
features excluded by requirements section 15.3 or design section 16. The
foundation must remain runnable with the four base services only.

- [x] **R0-04001 — Establish the Python/uv workspace from R0-010, R0-015,
  analysis sections 2 and 10, and design sections 1-2.** Add Python 3.12+
  constraints, root `pyproject.toml`, `.python-version` if selected, uv groups,
  reproducible scripts, and committed `uv.lock`. Keep secrets/local artifacts
  ignored and document the supported quality commands. Suggested commit:
  `build(backend): scaffold uv python workspace`.
- [x] **R0-04002 — Create backend package boundaries and quality smoke tests from
  R0-015, analysis sections 4 and 10, and design section 2.** Add the
  `backend/src/ioai` domain/application/adapters/entrypoints/workers package
  boundaries, unit/integration test roots, import-safe module markers, Ruff,
  Pyright or mypy configuration, and the smallest smoke test proving the package
  imports without framework side effects. Suggested commit:
  `build(backend): establish package boundaries and checks`.
- [x] **R0-04003 — Establish the pnpm frontend workspace from R0-010, R0-011,
  R0-013, R0-015, analysis sections 2 and 10, and design sections 1-2.** Add
  `pnpm-workspace.yaml`, root `package.json` scripts, committed `pnpm-lock.yaml`,
  strict shared TypeScript configuration, ESLint, Vitest, and deterministic
  workspace commands. Suggested commit: `build(frontend): scaffold pnpm workspace`.
- [x] **R0-04004 — Create shared frontend package boundaries and contract
  placeholders from R0-011, R0-013, R0-015, analysis section 9, and design
  sections 2 and 8.** Add empty-but-buildable `api-client`, `ui`, and
  `vocabulary` packages with ownership rules, smoke tests, and generated-artifact
  locations. Do not manually duplicate backend schemas or invent vocabulary
  lists. Suggested commit: `build(frontend): establish shared packages`.
- [x] **R0-04005 — Add the learner application shell from R0-011, R0-012, R0-015,
  `ui_release_0.md`, analysis section 6, and design section 12.** Create the
  Next.js App Router app on port 3000 with IOAI Learn metadata, Tailwind and
  shadcn/ui foundations, accessible header/navigation, safe loading/error
  boundaries, and a tested `/problems` route shell. Keep public data mocked only
  through typed fixtures; no drafts or author imports. Suggested commit:
  `feat(learn): add learner application shell`.
- [x] **R0-04006 — Add the Studio application shell from R0-013, R0-014, R0-015,
  `ui_release_0.md`, analysis section 7, and design section 13.** Create the
  Next.js App Router app on loopback port 3001 with distinct IOAI Studio
  metadata/branding, accessible navigation, safe error boundaries, and a tested
  `/author/problems` route shell. Keep the port organizational, not an auth
  mechanism. Suggested commit: `feat(studio): add author application shell`.
- [x] **R0-04007 — Add the FastAPI factory and settings shell from R0-015,
  analysis sections 2-3 and 10, and design sections 1-2.** Add typed settings,
  application factory, environment-safe configuration, dependency injection
  hooks, stable error mapping, request IDs, and smoke coverage without putting
  domain or publication rules in endpoints. Suggested commit:
  `feat(api): add fastapi application shell`.
- [x] **R0-04008 — Add API health/readiness and deterministic OpenAPI foundation
  from R0-015, analysis sections 9-10, and design sections 6-8 and 15.** Add
  `/health/live`, `/health/ready`, machine-readable safe responses, migration/
  dependency readiness semantics, deterministic OpenAPI generation, and the
  initial contract-drift check. Prove public schemas cannot serialize ORM or
  author-only fields even before feature resources exist. Suggested commit:
  `feat(api): add health and contract foundation`.
- [x] **R0-04009 — Add SQLAlchemy 2 and Alembic infrastructure from R0-015,
  analysis sections 4, 9, and 10, and design sections 9-10.** Configure typed
  session/unit-of-work boundaries, PostgreSQL settings, explicit transaction
  handling, migration environment, migration-head readiness check, and a
  PostgreSQL connectivity/rollback integration test. Do not add domain tables
  before their Phase 5/6 design steps. Suggested commit:
  `feat(db): add sqlalchemy and alembic foundation`.
- [x] **R0-04010 — Add deterministic test fixtures and foundation quality
  commands from R0-015, analysis section 10, and design section 15.** Establish
  fixture ownership, PostgreSQL isolation strategy, deterministic clocks/IDs,
  safe published/draft fixture shapes for later isolation tests, and scripts for
  backend/frontend unit, type, lint, format, build, and migration checks. The
  fixture layer must not silently create public content. Suggested commit:
  `test(foundation): establish deterministic fixtures and commands`.
- [x] **R0-04011 — Add the base Docker Compose topology from R0-015, analysis
  sections 2, 3, 9, and 10, and design section 14.** Add PostgreSQL, FastAPI,
  learner, and Studio services, one network, persistent database volume,
  readiness-based startup, health checks, environment examples, port bindings,
  and loopback Studio binding. Exclude Redis/Celery/Docling/MinIO/GPU/vector
  services. Suggested commit: `build(dev): add release 0 docker compose stack`.
- [x] **R0-04012 — Add local operations and migration/seed commands from R0-015,
  analysis sections 3 and 10, and design sections 10 and 14.** Document and
  script start/stop, migration, deterministic vocabulary/fixture seed, health,
  logs, backup/restore rehearsal, and explicitly confirmed destructive reset.
  Keep migration failures from making API readiness green and document that
  browser-local progress is not in PostgreSQL backups. Suggested commit:
  `build(dev): add local operations commands`.
- [x] **R0-04013 — Prove the foundation stack and critical boundary smoke flows
  from R0-011, R0-013, R0-014, R0-015, analysis sections 3, 9, and 10, and
  design sections 11-15.** Add focused tests that services start in dependency
  order, health/readiness are distinct, Studio binds to loopback, Learn and
  Studio routes are distinct, public/author schema boundaries hold, and a draft
  fixture cannot appear through a public foundation path. Suggested commit:
  `test(foundation): verify stack and boundary smoke flows`.
- [x] **R0-04014 — Add CI quality gates from R0-015, analysis section 10, and
  design sections 8 and 15.** Run uv formatting/lint/types/tests, pnpm lint,
  typecheck, unit tests, app builds, migration validation, generated OpenAPI/
  client drift, PostgreSQL integration, Compose health, and focused browser
  smoke checks with dependency caching. Fail closed on contract or public/draft
  isolation drift. Suggested commit: `ci: add release 0 quality pipeline`.
- [x] **R0-04015 — Review and baseline the executable foundation against
  `requirement_release_0.md`, `analysis_release_0.md`, and
  `design_release_0.md`.** Verify repository shape, tool/lockfile discipline,
  dependency direction, four-service topology, health/readiness, loopback
  Studio, generated contract ownership, migration safety, deterministic fixtures,
  public/draft boundaries, and quality commands. Update
  `docs/decisions/README.md`, record any ADRs, and list implementation behavior
  intentionally deferred to Phases 5+. Suggested commit:
  `build(foundation): baseline release 0 project foundation`.

## Phase 5 — Canonical vocabulary vertical slice

Deliverable: a tested path from the sole canonical source, `vocab.md`, through a
deterministic validated artifact and idempotent PostgreSQL synchronization to
typed public and author vocabulary reads. Runtime code, fixtures, APIs, and
frontend packages must consume that path rather than define parallel enums or
label lists. All behavior-bearing steps use red-green-refactor and trace to
requirements `R0-010` through `R0-016`, analysis section 5, and design section
5 unless a narrower reference is stated.

- [x] **R0-05001 — Characterize the canonical source and artifact contract from
  R0-010, R0-013, R0-015, analysis sections 5.1-5.2, and design section 5.1.**
  Add failing parser/contract tests using minimal representative source fixtures
  for every vocabulary record shape present in `vocab.md`: vocabulary type,
  code, nested English/Vietnamese labels, approved aliases, canonical status,
  and explicit topic `parent_code`. Define the stable structured-artifact schema,
  ordering, normalization rules, diagnostics, and generated-file ownership.
  Headings are presentation only and cannot establish parentage. Suggested
  commit: `test(vocabulary): define canonical source contract`.
- [x] **R0-05002 — Define framework-free vocabulary domain values from R0-010,
  R0-013, R0-015, analysis sections 4 and 5.2, and design sections 3 and 5.2.**
  Test first, then implement immutable typed composite identity, vocabulary type,
  bilingual labels, approved aliases, canonical status, and explicit topic
  parent references. Return specific actionable domain errors and keep FastAPI,
  Pydantic, SQLAlchemy, Markdown parsing, and UI concerns outside the domain.
  Suggested commit: `feat(vocabulary): define canonical domain values`.
- [x] **R0-05003 — Implement deterministic `vocab.md` extraction from R0-010,
  R0-013, R0-015, analysis section 5.1, and design section 5.1.** Test first,
  then add the adapter and project command that parse every approved source
  shape into normalized domain input. Reject malformed rows, missing bilingual
  labels, invalid statuses, and missing explicit topic relationships with
  source-oriented diagnostics; do not infer values or relationships from
  Markdown layout. Suggested commit:
  `feat(vocabulary): extract canonical source records`.
- [x] **R0-05004 — Enforce vocabulary identity, graph, and ambiguity invariants
  from R0-010, R0-011, R0-013, R0-015, `AC-R0-011-07` through
  `AC-R0-011-08`, `AC-R0-013-07` through `AC-R0-013-10`, analysis section
  5.2, and design sections 5.1-5.2.** Add failing cases before implementing
  checks for duplicate composite identities, missing or cross-type parents,
  self-parenting, cycles, orphaned records, and duplicate normalized canonical
  labels or aliases within a parent branch. Preserve identical codes or labels
  across vocabulary types when the composite identities are distinct.
  Suggested commit: `feat(vocabulary): validate canonical invariants`.
- [x] **R0-05005 — Generate the runtime artifact and enforce source drift from
  R0-010, R0-015, `AC-R0-015-18` through `AC-R0-015-19`, analysis sections
  5.1 and 5.5, and design section 5.1.** Generate the stable checked-in artifact
  only after whole-source validation, with deterministic ordering and no
  timestamps, machine paths, or environment-dependent output. Add a drift-check
  command and CI-facing test that regenerates in memory and reports field-level
  differences. Make backend runtime data and deterministic fixtures consume the
  artifact rather than hand-maintained vocabulary constants. Suggested commit:
  `build(vocabulary): generate and verify canonical artifact`.
- [x] **R0-05006 — Implement the central Release 0 availability policy from
  R0-012, R0-013, R0-016, `AC-R0-012-04`, `AC-R0-013-14`, analysis section
  5.4, and design section 5.3.** Test first, then return typed allow/deny
  decisions with stable reason codes and safe messages for the five approved
  task types, `NONE`/`BROWSER`/`CPU_LIGHT` compute tiers, approved scoring
  methods, and the mutually exclusive `NONE` modality rule. Preserve all valid
  future-facing canonical records while making unavailable values
  publication-blocking; do not silently downgrade them. Suggested commit:
  `feat(vocabulary): enforce release 0 availability`.
- [x] **R0-05007 — Add the canonical vocabulary PostgreSQL schema from R0-010,
  R0-015, `AC-R0-015-07` through `AC-R0-015-09`, analysis sections 5.2 and
  9, and design sections 5.4, 9, and 10.** Add explicit SQLAlchemy 2 mappings
  and a descriptive Alembic migration for records, labels, aliases, statuses,
  and topic parentage. Protect composite identity and enforceable parent/status
  invariants with PostgreSQL constraints; add hierarchy and normalized-search
  indexes. Integration-test upgrade, safe downgrade, constraints, and rollback
  against PostgreSQL without turning ORM rows into domain objects. Suggested
  commit: `feat(vocabulary): migrate canonical records`.
- [x] **R0-05008 — Synchronize the validated artifact idempotently from R0-010,
  R0-015, analysis section 5.5, and design sections 4.1 and 5.4.** Define the
  narrow vocabulary repository/source ports and implement one transactional
  synchronization use case. Validate the complete artifact before writing;
  report added, updated, unchanged, rejected, and policy-disabled records;
  permit approved label/alias/status updates; and never repurpose a changed
  vocabulary type or code as an existing identity. Cover repeated sync,
  rollback, update, and identity-change behavior with PostgreSQL integration
  tests, then wire the existing deterministic vocabulary seed command to this
  use case. Suggested commit: `feat(vocabulary): synchronize canonical records`.
- [x] **R0-05009 — Implement hierarchical and bilingual vocabulary queries from
  R0-011, R0-013, `AC-R0-011-07` through `AC-R0-011-08`,
  `AC-R0-013-07` through `AC-R0-013-09`, analysis sections 5.2-5.3 and 9,
  and design sections 5.2 and 6.** Test repository behavior for type-scoped
  identity lookup, stable hierarchy/breadcrumb ordering, English and Vietnamese
  label search, approved alias matching, ambiguity handling, and explicit
  descendant expansion. Return canonical composite identities and never persist
  or return a display label as identity. Suggested commit:
  `feat(vocabulary): query canonical hierarchy`.
- [x] **R0-05010 — Expose separate public and author-safe vocabulary contracts
  from R0-011, R0-013, R0-015, analysis sections 5.3 and 9, and design sections
  5.2, 6, 7, and 8.** Add versioned FastAPI read routes and Pydantic contracts
  around the query use case, including explicit type/search/root/
  include-descendants inputs, deterministic ordering, bounded results, stable
  machine-readable errors, and availability metadata only where the projection
  permits it. Prove public responses contain canonical active values and no
  proposals, persistence objects, internal diagnostics, or author-only fields.
  Suggested commit: `feat(api): expose canonical vocabulary reads`.
- [x] **R0-05011 — Record missing-value proposals without creating canonical
  metadata from R0-010, R0-013, `AC-R0-013-10`, analysis sections 5.3 and
  5.5, and design section 5.4.** Define and test a bounded author proposal
  command, persistence model, migration, and author-safe contract carrying the
  vocabulary context and note. A proposal must remain separately reviewable,
  must not enter the generated artifact or public vocabulary response, and must
  never satisfy a canonical problem reference. Do not add a broader vocabulary
  editor or curriculum-owner administration UI. Suggested commit:
  `feat(vocabulary): record canonical value proposals`.
- [x] **R0-05012 — Generate and consume vocabulary client types from R0-011,
  R0-013, R0-015, analysis sections 5.1 and 9, and design sections 2, 5.1, and
  8.** Regenerate deterministic OpenAPI and `@ioai/api-client` types, replace
  the placeholder `@ioai/vocabulary` exports with generated-artifact-backed
  typed helpers, and add contract/drift tests proving the frontend does not
  duplicate backend schemas or canonical labels. Exercise type-scoped identity,
  bilingual labels, hierarchy, aliases, and availability in package tests
  without building Phase 6 editor UI or Phase 7 learner filters. Suggested
  commit: `feat(frontend): consume canonical vocabulary contract`.
- [x] **R0-05013 — Verify and baseline the canonical vocabulary vertical slice
  against R0-010 through R0-016, analysis section 5, and design section 5.**
  Prove source-to-artifact determinism, graph and branch invariants, drift
  failure, policy-disabled value preservation, migration up/down behavior,
  transactional idempotent synchronization, bilingual hierarchy/search,
  proposal isolation, safe API projections, and OpenAPI/client compatibility.
  Run all affected backend/frontend formatting, lint, type, unit, PostgreSQL
  integration, migration, generation, and build gates; update traceability,
  developer commands, and relevant decisions. Record exact limitations instead
  of claiming completion when a gate is skipped or failing. Suggested commit:
  `feat(vocabulary): baseline canonical vertical slice`.

## Phase 6 — Problem domain and authoring

- [x] **R0-06001 — Baseline the Phase 6 authoring slice against R0-013,
  `AC-R0-013-01` through `AC-R0-013-21`, analysis sections 4 and 7, and design
  sections 3, 4, 7, 9, 11, and 13.** Replace the current problem fixture and
  Studio placeholder assumptions with a written implementation map covering
  domain ownership, author-only projections, revision/version semantics,
  validation layers, routes, and the boundary with Phase 7 editorial actions.
  Record tests to observe red for each subsequent behavior and keep public
  snapshots, transitions, and learner assessment outside this phase except for
  the interfaces the authoring slice requires. Suggested commit:
  `docs(authoring): baseline problem authoring slice`.
- [x] **R0-06002 — Define stable problem identity and structured content value
  objects from R0-013, R0-014, `AC-R0-013-02` through `AC-R0-013-06`, analysis
  sections 4.1-4.2, and design section 3.2.** Test first, then implement problem
  and revision IDs, immutable normalized slugs, editorial status as a distinct
  dimension, localized title/objective/content values, ordered statement,
  provided-information, example, constraint, hint, explanation, and feedback
  blocks, plus explicit pending-translation warnings. Validate bounded fields
  and observable assessable objectives without importing frameworks into the
  domain. Suggested commit: `feat(problems): define identity and content`.
- [x] **R0-06003 — Define response variants and decimal-safe scoring from
  `AC-R0-013-12` through `AC-R0-013-13`, analysis section 6.2, and design
  sections 3.2-3.3.** Add discriminated domain configurations for exactly
  `QUIZ_SINGLE`, `QUIZ_MULTIPLE`, `NUMERIC_ANSWER`, `SHORT_ANSWER`, and
  `CODE_FUNCTION`, including their applicable choices, tolerances, signatures,
  starter code, tests, and rubric guidance. Add scoring components using exact
  decimals, require at least one component and a total of exactly `1.0`, and
  reject fields or scoring methods that do not apply to the selected variant.
  Suggested commit: `feat(problems): model response and scoring`.
- [x] **R0-06004 — Define curriculum, prerequisite, and resource values from
  `AC-R0-013-07` through `AC-R0-013-14`, analysis sections 4.2 and 5.2-5.4,
  and design sections 3.2-3.3.** Test exact cardinalities for stage, difficulty,
  task type, primary and zero-to-three secondary competencies; typed canonical
  topics and prerequisites; positive expected minutes; exact runtime/resource
  limits; modality `NONE` exclusivity; network policy; and allowed compute
  tiers. Reuse Phase 5 composite vocabulary identities and the central Release
  0 availability policy rather than defining parallel enums or labels.
  Suggested commit: `feat(problems): model curriculum and resources`.
- [x] **R0-06005 — Assemble the problem revision aggregate and layered validation
  report from R0-013, `AC-R0-013-19`, analysis sections 4.2 and 7.3, and design
  sections 3.2-3.4 and 7.3.** Compose the content, curriculum, prerequisites,
  response, scoring, and resources under a stable problem identity while
  keeping editorial validity separate from publication. Return deterministic
  errors and warnings with stable code, section, field path, safe correction
  message, revision/version context, and `publication_eligible`; group them as
  Content, Curriculum, Assessment, Resources, and Publication. Suggested
  commit: `feat(problems): validate problem revisions`.
- [x] **R0-06006 — Add PostgreSQL problem and revision migrations from R0-013,
  R0-014, analysis sections 4 and 9, and design sections 9.1-9.5.** Create
  explicit SQLAlchemy 2 mappings and Alembic revisions for stable problems,
  versioned revisions, localized structured content, competency/topic joins,
  typed prerequisites, one response configuration, scoring components, and
  resources. Enforce critical uniqueness, cardinality, foreign-key, exact
  numeric, and optimistic-version constraints without creating published
  snapshots or transition history early; test safe upgrade and downgrade
  against PostgreSQL. Suggested commit: `feat(problems): migrate draft storage`.
- [x] **R0-06007 — Implement author-only draft repositories and transactions from
  `AC-R0-013-01` through `AC-R0-013-03` and `AC-R0-013-18`, analysis sections
  7.1-7.2 and 9, and design sections 4.2 and 9.3.** Define narrow create, list,
  read, validate-read, and compare-and-increment save ports; map persistence rows
  to domain values; allocate the problem and initial `DRAFT` revision
  atomically; and reject stale versions without overwriting newer data. Do not
  add a generic reader usable by public routes. Cover rollback, ordering,
  normalized round trips, and concurrent saves with PostgreSQL tests. Suggested
  commit: `feat(authoring): persist versioned drafts`.
- [x] **R0-06008 — Implement draft creation, listing, and reading use cases from
  `AC-R0-013-01` through `AC-R0-013-03`, analysis section 7.1, and design
  sections 4.1 and 7.1.** Coordinate injected IDs and clocks to create an
  initial structured draft with no public URL or snapshot, return author list
  rows with problem/revision identity, editorial status, version, last-save and
  validation summary, and read the current author aggregate. Define the port
  needed for Phase 7 to start a revision of a published problem, but defer that
  snapshot-preserving use case until publication storage exists. Suggested
  commit: `feat(authoring): create and query drafts`.
- [x] **R0-06009 — Expose safe author draft read/create contracts from R0-013,
  R0-015, analysis sections 3 and 9, and design sections 7.1-7.2 and 8.** Add
  `GET` and `POST /api/v1/author/problems` and
  `GET /api/v1/author/problems/{problem_id}` with bounded Pydantic contracts,
  stable errors, request IDs, and explicit author DTOs. Prove these schemas are
  not used by public routes, regenerate deterministic OpenAPI and the frontend
  client, and add compatibility/drift tests before replacing Studio fixtures.
  Suggested commit: `feat(api): expose author drafts`.
- [x] **R0-06010 — Implement versioned draft saves from `AC-R0-013-15` through
  `AC-R0-013-18`, analysis section 7.2, and design sections 7.2 and 9.3.** Add
  the save use case and `PUT /api/v1/author/revisions/{revision_id}` contract
  with `expected_version`, a structured patch or complete revision, and an
  optional bounded client save key. Return the normalized accepted revision and
  incremented version; map stale writes to `REVISION_CONFLICT` with a safe
  current-version reference; make retries non-duplicating; and prove failed
  writes leave no partial associations. Regenerate client types. Suggested
  commit: `feat(authoring): save drafts optimistically`.
- [x] **R0-06011 — Replace the Studio problem-list fixture with the author API
  from `AC-R0-013-01`, analysis section 7.1, and design section 13.1.** Build
  `/author/problems` with distinct IOAI Studio presentation, status tabs,
  search and filters supported by the author contract, revision identity,
  last-saved time, validation summary, create/resume actions, and accessible
  loading, empty, and safe retry states. Keep the list separate from public
  learner content and cover the page by accessible role/name queries.
  Suggested commit: `feat(studio): build author problem list`.
- [x] **R0-06012 — Build the draft editor route and form coordinator from
  `AC-R0-013-02`, `AC-R0-013-15`, design sections 13.1-13.3, and the current
  Studio shell.** Implement `/author/problems/new` initialization and
  `/author/problems/[id]` editing, normalized local form state, revision/version
  ownership, dirty-field tracking, section navigation, explicit Save, Validate,
  and Preview actions, and unsaved-change protection. Keep save, validation,
  preview, review, approval, and publication visibly distinct. Suggested
  commit: `feat(studio): establish draft editor state`.
- [x] **R0-06013 — Build bilingual structured content editing from
  `AC-R0-013-04` through `AC-R0-013-06` and design section 13.2.** Add visible
  English/Vietnamese fields in learner reading order for title, objective,
  statement, provided information, examples, constraints, hints, explanation,
  and feedback content. First run and document a bounded package spike, then use
  a stable, maintained Vietnamese input package for optional in-browser Telex;
  do not implement or vendor an application-owned input-method engine. Treat a
  package as eligible only when its release/maintenance history, issue response,
  production adoption, license, provenance, security posture, documented API,
  and test coverage provide evidence of stability; a recent version number or
  an unverified “stable” claim is insufficient. Also evaluate bundle cost, strict
  TypeScript/React controlled-input support, textarea and rich-editor behavior,
  caret/selection correctness, undo/redo, paste, keyboard and mobile behavior,
  browser composition events, cleanup/scoping, accessibility, and interaction
  with an operating-system Vietnamese IME. Record the selected package and
  pinned version with the evidence and rejection reasons for alternatives; do
  not add a dependency until these checks and representative Telex tests pass,
  and do not ship browser Telex if no package meets the stability gate. Provide
  an accessible `EN` / `VI` segmented toggle that changes the active editing
  language while preserving
  both translations, dirty state, validation state, and focus context. Scope an
  independently visible Telex on/off control to Vietnamese editable fields only
  so authors using a native IME can disable browser conversion and English/code
  fields are never transformed. Support accessible ordered/repeated block
  operations, mark missing translations pending, display warnings without
  treating them as learner content, and link objective validation to its field.
  Test language switching, translation preservation, Telex enable/disable and
  representative tone/diacritic sequences, native composition safety, and
  keyboard/screen-reader names before integration. Suggested commit:
  `feat(studio): edit bilingual content with optional telex`.
- [x] **R0-06014 — Build canonical curriculum and prerequisite editing from
  `AC-R0-013-07` through `AC-R0-013-11`, analysis sections 5.2-5.4 and 7.1,
  and design sections 5.2-5.4 and 13.2.** Consume the Phase 5 vocabulary client
  for type-disambiguated stage, difficulty, task type, competency, and
  searchable hierarchical topic selectors; show breadcrumbs and intermediate-
  topic specificity warnings; enforce zero-to-three secondary competencies;
  and store typed prerequisite relationship, target type/identity, and optional
  minimum evidence. Integrate the existing separately reviewable proposal
  command without allowing proposals to become metadata. Suggested commit:
  `feat(studio): edit canonical problem metadata`.
- [x] **R0-06015 — Build response and scoring editors from `AC-R0-013-12`
  through `AC-R0-013-13`, analysis section 6.2, and design section 13.2.** Render
  only the fields for the selected approved response variant, preserve no stale
  inapplicable configuration when the type changes, and add keyboard-safe
  repeated choice/test/component controls. Display the exact decimal scoring
  total and field-level errors, blocking validation until it is exactly `1.0`.
  Suggested commit: `feat(studio): configure response and scoring`.
- [x] **R0-06016 — Build resource and Release 0 policy editing from
  `AC-R0-013-14`, analysis sections 5.4 and 7.1, and design sections 3.3 and
  13.2.** Add positive expected minutes, data modalities, exact compute/runtime
  limits, and network policy fields; derive display categories rather than
  persisting them; enforce `NONE` exclusivity; and show actionable blockers for
  canonical but unavailable stages, task types, compute tiers, scoring methods,
  or resource combinations. Suggested commit:
  `feat(studio): edit problem resource policy`.
- [x] **R0-06017 — Implement Studio autosave, local recovery, and conflict
  resolution from `AC-R0-013-15` through `AC-R0-013-18`, analysis section 7.2,
  and design section 13.3.** Coalesce idle changes, show revision-bound
  `Saving...`, `Saved`, and `Save failed` states, and keep a schema-versioned
  local recovery copy on failure. On reopen or `REVISION_CONFLICT`, compare the
  server and local target and require an explicit restore, discard, retry, or
  resolve choice; never silently overwrite newer server work or discard unsaved
  fields. Test timers and storage deterministically, including unavailable or
  corrupt local storage. Suggested commit: `feat(studio): recover draft saves`.
- [x] **R0-06018 — Expose and render complete draft validation from
  `AC-R0-013-06`, `AC-R0-013-14`, and `AC-R0-013-19`, analysis section 7.3,
  and design sections 7.3 and 13.4.** Add
  `POST /api/v1/author/revisions/{revision_id}/validate`, require the current
  version, return the stable layered report, and regenerate the client. Build a
  Studio panel grouped by Content, Curriculum, Assessment, Resources, and
  Publication; link every issue to its field, move focus to the first blocker,
  keep warnings distinct, and expose `publication_eligible` without adding a
  Phase 7 transition. Suggested commit: `feat(authoring): validate complete drafts`.
- [x] **R0-06019 — Prepare the isolated learner-preview projection from
  `AC-R0-013-20` through `AC-R0-013-21`, analysis sections 7.1 and 9, and
  design sections 7.3, 11.2, and 13.4.** Define and test an author-only preview
  use case and `POST /api/v1/author/revisions/{revision_id}/preview` contract
  that accepts current saved state or explicit unsaved editor state, returns a
  learner-shaped projection plus author warnings and a mandatory
  `Draft preview - not public` marker, and cannot resolve through a public slug,
  route, search, recommendation, build, or cache. Regenerate client types; leave
  the responsive learner-page rendering and browser workflow to R0-072.
  Suggested commit: `feat(authoring): isolate draft preview data`.
- [x] **R0-06020 — Verify and baseline the problem-authoring vertical slice
  against R0-013, analysis sections 4 and 7, and design sections 3, 4, 7, 9,
  11, and 13.** Prove aggregate invariants, response variants, exact scoring,
  canonical metadata, policy blockers, migration up/down safety, transactional
  draft creation, normalized persistence, version conflicts, API/schema
  separation, generated-client agreement, Studio list/editor accessibility,
  autosave recovery, validation focus, and preview isolation. Run all affected
  backend/frontend formatting, lint, type, unit, PostgreSQL integration,
  migration, OpenAPI/client generation, component, and production-build gates;
  update traceability and document exact skipped or failing gates. Suggested
  commit: `feat(authoring): baseline problem authoring slice`.

## Phase 7 — Editorial review and publication

Phase input and traceability rule: implement `R0-014` and
`AC-R0-014-01` through `AC-R0-014-16` using analysis sections 8-10, design
sections 4, 7-11, and 13, and `ui_release_0.md` sections 6.8-6.10 and 7-9.
Build on the Phase 6 revision validation and isolated preview projection; do
not duplicate those contracts or implement the Phase 8 learner library and
solving UI early. Every accepted transition must use the persisted current
state and version, require a bounded human-entered note, use the injected
clock and available local actor context, and append immutable history in the
same transaction as its state change.

- [x] **R0-07001 — Define the editorial transition policy from
  `AC-R0-014-01` through `AC-R0-014-04`, `AC-R0-014-13`, and
  `AC-R0-014-16`, analysis sections 8.1-8.2, and design sections 3.2 and
  7.4.** Add framework-free commands and history values for exactly
  `DRAFT -> IN_REVIEW`, `IN_REVIEW -> CHANGES_REQUESTED`, and
  `IN_REVIEW -> APPROVED`; require non-blank bounded notes; distinguish actor
  context from authentication; and reject every other source/target pair
  without changing state or creating history. Cover timestamps with an
  injected clock and keep editorial status separate from validation,
  publication state, learner task status, and learning evidence. Suggested
  commit: `feat(editorial): define review transition policy`.
- [x] **R0-07002 — Add editorial, snapshot, and idempotency persistence from
  `AC-R0-014-05`, `AC-R0-014-08`, and `AC-R0-014-13`, analysis sections
  8.2-8.3, and design sections 9-10.** Add an Alembic migration and explicit
  SQLAlchemy mappings for append-only editorial transitions, immutable
  published snapshots, the problem's current-public pointer or equivalent
  single-current constraint, and operation-scoped idempotency records. Enforce
  foreign keys, unique stable slugs/current snapshots and idempotency scopes,
  useful revision/status indexes, and deterministic upgrade/downgrade tests
  against PostgreSQL. Suggested commit:
  `feat(database): persist editorial publication records`.
- [x] **R0-07003 — Implement transactional review commands from
  `AC-R0-014-01` through `AC-R0-014-04` and `AC-R0-014-16`, analysis
  sections 8.1-8.2 and 9.3, and design sections 4 and 10.1.** Add application
  use cases and narrow ports for submit-for-review, request-changes, and
  approval. Lock or compare-and-increment the persisted revision, rerun the
  required validation and Release 0 availability checks for submit and
  approval, append history atomically, and return stable errors for blockers,
  missing notes, stale versions, and invalid transitions. Prove rollback and
  concurrent/stale-command behavior with unit and PostgreSQL integration
  tests. When changes are requested, provide the defined successor-revision
  operation: copy the reviewed content into a new editable `DRAFT` rather than
  adding an unapproved `CHANGES_REQUESTED -> IN_REVIEW` shortcut or mutating
  immutable history; retrying the operation must not create duplicate
  revisions. Suggested commit: `feat(editorial): execute review commands`.
- [x] **R0-07004 — Expose editorial history and review commands from
  `AC-R0-014-01` through `AC-R0-014-04`, `AC-R0-014-13`, and
  `AC-R0-014-16`, design sections 7.1, 7.4-7.5, and 8.** Add author-only
  history reads and the submit-review, request-changes, and approve FastAPI
  commands under `/api/v1/author`; require revision ID, expected version,
  note, and bounded operation identity as designed; map workflow, validation,
  and conflict failures to safe stable contracts. Regenerate OpenAPI and the
  TypeScript client, and add compatibility tests that keep history and draft
  fields out of public schemas. Suggested commit:
  `feat(api): expose editorial review workflow`.
- [ ] **R0-07005 — Build the Studio review workspace from `AC-R0-014-01`
  through `AC-R0-014-04`, `AC-R0-014-13`, `ui_release_0.md` sections 6.8,
  7, and 9, and design sections 13.4-13.5.** Extend the Review & publish
  section with the existing grouped validation checklist, immutable note/time/
  source/target history, and status-specific Submit for review, Request
  changes, and Approve actions. Require a visible note before commands, refresh
  version/status after success, preserve author input after recoverable errors,
  link blockers back to fields, and represent status with text as well as
  color. Add accessible component tests for keyboard use, focus placement,
  loading, validation, conflict, and safe error states. Suggested commit:
  `feat(studio): build editorial review workspace`.
- [ ] **R0-07006 — Complete responsive learner-format draft preview from
  `AC-R0-013-20` through `AC-R0-013-21`, `ui_release_0.md` section 6.9,
  and design sections 7.3, 11.2, and 13.4.** Consume the Phase 6 author-only
  preview contract from the saved revision or explicit unsaved editor state and
  render the learner problem-page structure at selectable desktop and mobile
  widths. Keep the striped `Draft preview - not public` banner persistent,
  display pending-translation and other warnings only to authors, disable all
  public-problem and continue links before publication, and prove that preview
  state does not enter a public route, cache, or build. Suggested commit:
  `feat(studio): render isolated learner preview`.
- [ ] **R0-07007 — Implement atomic publication from `AC-R0-014-05` through
  `AC-R0-014-08`, analysis sections 8.3 and 9.3, and design sections 4,
  7.4, and 10.1-10.3.** Add a publish use case that locks the problem and
  approved revision, verifies expected version and approval, reruns complete
  validation and current Release 0 policy, claims the unique stable slug,
  creates an immutable learner-safe snapshot, appends the `PUBLISHED` history
  transition, and switches the current-public pointer in one transaction.
  Scope the idempotency key to revision and request digest: identical retries
  return the original result, while key reuse with different intent conflicts.
  Prove invalid-state, stale-policy, slug-conflict, retry, concurrency, and
  injected-failure rollback behavior against PostgreSQL. Suggested commit:
  `feat(publication): publish revisions atomically`.
- [ ] **R0-07008 — Expose publication confirmation and permanent URL from
  `AC-R0-014-05` through `AC-R0-014-08`, `ui_release_0.md` sections 6.8 and
  8, and design sections 7.1 and 13.5.** Add the author publish endpoint with
  expected version, required note, and idempotency key; return the stable public
  slug/URL and safe replay result; then regenerate OpenAPI and the client.
  In Studio, show Publish only for an approved, currently eligible revision and
  require a keyboard-safe confirmation dialog that clearly distinguishes the
  permanent public URL from Preview, traps focus, closes with Escape when safe,
  returns focus to its trigger, prevents duplicate submission, and renders
  blockers without implying that Save or Approve published content. Suggested
  commit: `feat(studio): confirm approved publication`.
- [ ] **R0-07009 — Create draft revisions of published problems from
  `AC-R0-014-09` through `AC-R0-014-10`, analysis sections 8.1 and 8.4, and
  design sections 7.2 and 10.2.** Complete the shared successor-revision
  command for published and changes-requested sources, copying content into a
  new independently identified `DRAFT` with the next revision number and
  optimistic version. For a published source, retain the stable problem slug
  and leave the current immutable snapshot untouched; for requested changes,
  preserve the reviewed revision and its decision history. Make retries safe,
  reject competing duplicate-current drafts according to the documented
  revision rule, expose the command through the author API/client, and update
  Edit on published or changes-requested Studio rows to enter the new draft.
  Suggested commit:
  `feat(authoring): revise published problems safely`.
- [ ] **R0-07010 — Implement explicit archive and republication behavior from
  `AC-R0-014-14` through `AC-R0-014-16`, analysis sections 8.1 and 8.4, and
  design sections 7.4 and 10.1.** Add a versioned archive command that requires
  a note, atomically appends immutable `PUBLISHED -> ARCHIVED` history and
  removes current public eligibility without deleting or reusing the slug or
  historical snapshot. Add the author API/client and a destructive-action
  confirmation in Studio. Prove that an archived problem is absent at its
  public URL and from public eligibility, and that only a new revision passing
  the normal review and publish flow can become current without mutating or
  silently reactivating archived history. Suggested commit:
  `feat(publication): archive and republish problems`.
- [ ] **R0-07011 — Establish published-only repository projections from
  `AC-R0-014-09` through `AC-R0-014-12`, analysis section 9, and design
  sections 9.3 and 11.1-11.3.** Add narrowly named current-snapshot list and
  stable-slug detail ports whose queries begin from current published
  eligibility before applying filters, sorting, or pagination. Return dedicated
  learner-safe projections that omit revision IDs, draft validation/history,
  notes, hidden answers/tests, internal scoring configuration, object metadata,
  and unavailable translations. Keep full Phase 8 search/filter/detail HTTP
  behavior out of this step; provide the safe persistence/application boundary
  it must consume. Suggested commit:
  `feat(publication): enforce published snapshot projections`.
- [ ] **R0-07012 — Prove cross-layer public/draft isolation from
  `AC-R0-014-10` through `AC-R0-014-12`, `AC-R0-015-13`, analysis sections
  9.2-9.4, and design sections 8.3 and 11.** Add adversarial repository, API,
  OpenAPI, generated-client, and Next.js build tests covering mixed published,
  draft, in-review, approved, superseded, and archived records. Demonstrate
  that list/detail/search inputs, direct slug lookup, recommendation data
  sources, preview identifiers, caches, errors, and serialized schemas cannot
  reveal unpublished content, editorial notes, answer keys, hidden tests,
  stack traces, object keys, or internal IDs. Suggested commit:
  `test(publication): prove public draft isolation`.
- [ ] **R0-07013 — Verify the editorial publication browser workflow from
  `R0-014`, `AC-R0-013-19` through `AC-R0-013-21`, and
  `ui_release_0.md` sections 6.8-6.10 and 10.** Add the critical Playwright
  path for author validate -> unsaved learner preview -> submit -> request
  changes -> revise -> resubmit -> approve -> confirm publish -> verify the
  permanent public URL, plus revision and archive coverage at the smallest
  useful browser boundary. Exercise desktop and mobile preview widths,
  deterministic focus, required notes, visible status text, validation
  blockers, and the rule that the prior public snapshot remains unchanged
  throughout unpublished edits. Suggested commit:
  `test(e2e): cover editorial publication workflow`.
- [ ] **R0-07014 — Baseline Phase 7 against R0-014, analysis sections 8-10,
  design sections 4 and 7-13, and `ui_release_0.md`.** Update requirement-to-
  implementation/test traceability and operational documentation; verify
  migration up/down safety, transaction rollback, idempotency, concurrency,
  generated OpenAPI/client agreement, Studio accessibility/responsiveness,
  public projection isolation, and the critical browser workflow. Run all
  affected backend/frontend format, lint, type, unit, PostgreSQL integration,
  migration, contract, component, Playwright, and production-build gates, and
  record every exact skipped or failing gate rather than claiming completion.
  Suggested commit: `feat(publication): baseline editorial workflow`.

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
