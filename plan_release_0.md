# Release 0 Delivery Plan

## How to use this plan

- One checklist item is one meaningful Git commit unless the item explicitly
  says it is a release checkpoint.
- Checklist item IDs use the legacy `R0-<three digits>` form for existing
  Phase 0–2 requirement/story traceability. Phase 3 uses the expandable
  `R0-03xxx` plan-step form: `R0-03001` through `R0-03999`, ordered numerically.
  Each step remains one meaningful commit. Future phases may use the same
  pattern with their phase prefix, such as `R0-04xx`. Plan-step IDs are
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
- [ ] **R0-05007 — Add the canonical vocabulary PostgreSQL schema from R0-010,
  R0-015, `AC-R0-015-07` through `AC-R0-015-09`, analysis sections 5.2 and
  9, and design sections 5.4, 9, and 10.** Add explicit SQLAlchemy 2 mappings
  and a descriptive Alembic migration for records, labels, aliases, statuses,
  and topic parentage. Protect composite identity and enforceable parent/status
  invariants with PostgreSQL constraints; add hierarchy and normalized-search
  indexes. Integration-test upgrade, safe downgrade, constraints, and rollback
  against PostgreSQL without turning ORM rows into domain objects. Suggested
  commit: `feat(vocabulary): migrate canonical records`.
- [ ] **R0-05008 — Synchronize the validated artifact idempotently from R0-010,
  R0-015, analysis section 5.5, and design sections 4.1 and 5.4.** Define the
  narrow vocabulary repository/source ports and implement one transactional
  synchronization use case. Validate the complete artifact before writing;
  report added, updated, unchanged, rejected, and policy-disabled records;
  permit approved label/alias/status updates; and never repurpose a changed
  vocabulary type or code as an existing identity. Cover repeated sync,
  rollback, update, and identity-change behavior with PostgreSQL integration
  tests, then wire the existing deterministic vocabulary seed command to this
  use case. Suggested commit: `feat(vocabulary): synchronize canonical records`.
- [ ] **R0-05009 — Implement hierarchical and bilingual vocabulary queries from
  R0-011, R0-013, `AC-R0-011-07` through `AC-R0-011-08`,
  `AC-R0-013-07` through `AC-R0-013-09`, analysis sections 5.2-5.3 and 9,
  and design sections 5.2 and 6.** Test repository behavior for type-scoped
  identity lookup, stable hierarchy/breadcrumb ordering, English and Vietnamese
  label search, approved alias matching, ambiguity handling, and explicit
  descendant expansion. Return canonical composite identities and never persist
  or return a display label as identity. Suggested commit:
  `feat(vocabulary): query canonical hierarchy`.
- [ ] **R0-05010 — Expose separate public and author-safe vocabulary contracts
  from R0-011, R0-013, R0-015, analysis sections 5.3 and 9, and design sections
  5.2, 6, 7, and 8.** Add versioned FastAPI read routes and Pydantic contracts
  around the query use case, including explicit type/search/root/
  include-descendants inputs, deterministic ordering, bounded results, stable
  machine-readable errors, and availability metadata only where the projection
  permits it. Prove public responses contain canonical active values and no
  proposals, persistence objects, internal diagnostics, or author-only fields.
  Suggested commit: `feat(api): expose canonical vocabulary reads`.
- [ ] **R0-05011 — Record missing-value proposals without creating canonical
  metadata from R0-010, R0-013, `AC-R0-013-10`, analysis sections 5.3 and
  5.5, and design section 5.4.** Define and test a bounded author proposal
  command, persistence model, migration, and author-safe contract carrying the
  vocabulary context and note. A proposal must remain separately reviewable,
  must not enter the generated artifact or public vocabulary response, and must
  never satisfy a canonical problem reference. Do not add a broader vocabulary
  editor or curriculum-owner administration UI. Suggested commit:
  `feat(vocabulary): record canonical value proposals`.
- [ ] **R0-05012 — Generate and consume vocabulary client types from R0-011,
  R0-013, R0-015, analysis sections 5.1 and 9, and design sections 2, 5.1, and
  8.** Regenerate deterministic OpenAPI and `@ioai/api-client` types, replace
  the placeholder `@ioai/vocabulary` exports with generated-artifact-backed
  typed helpers, and add contract/drift tests proving the frontend does not
  duplicate backend schemas or canonical labels. Exercise type-scoped identity,
  bilingual labels, hierarchy, aliases, and availability in package tests
  without building Phase 6 editor UI or Phase 7 learner filters. Suggested
  commit: `feat(frontend): consume canonical vocabulary contract`.
- [ ] **R0-05013 — Verify and baseline the canonical vocabulary vertical slice
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
