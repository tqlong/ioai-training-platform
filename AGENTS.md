# AGENTS.md — IOAI Training Platform, Release 0

## Mission

Build Release 0 as a complete editorial pilot: authors can create, validate,
review, preview, and publish high-quality problems; learners can browse only
published problems, open a permanent problem URL, submit a lightweight answer,
receive feedback, and continue to a recommended next problem.

Optimize for a trustworthy content loop, not for an advanced judge, broad
course platform, or competition system.

## Governing documents

Read these files before planning or changing product behavior:

1. `master_plan.md` — product goals, release boundaries, and curriculum policy.
2. `ui_release_0.md` — Release 0 routes, interaction design, responsive behavior,
   and acceptance criteria.
3. `vocab.md` — the sole authority for all controlled vocabulary.
4. `code_standard.md` — clean-code, Python environment, testing, and definition-
   of-done requirements.

Resolve conflicts in that order only when the more specific Release 0 UI does
not contradict a product or vocabulary invariant. Never silently choose between
conflicting requirements: document the conflict and ask for direction.

This file governs Release 0. Do not implement features assigned to later
releases merely because their canonical values already exist in `vocab.md`.

## Release 0 scope

Implement the smallest vertical product that supports:

- canonical vocabulary stored as validated structured data;
- public browsing of published problems at `/problems`;
- public problem pages with stable, permanent URLs;
- search, stage and taxonomy filters, and a dense scannable problem list;
- anonymous, device-local learner progress where required by the UI design;
- a feedback mechanism on every public problem;
- author problem management under `/author/problems`;
- structured drafting, validation, learner preview, editorial review, revision,
  and publication;
- manual or lightweight automated scoring;
- strict separation between drafts and published snapshots.

Do not add authentication, leaderboards, contests, teams, social features,
advanced personalization, GPU workloads, hosted notebooks, complex job-based
judging, semantic retrieval, or a general-purpose content-management system.

Prefer 20–30 carefully reviewed AI Foundations problems and a reliable workflow
over broad feature coverage. Support Competition Foundations where the approved
Release 0 content requires it. Later stages may appear as disabled “Coming next”
options but must not become publishable accidentally.

## Required technology

### Backend

- Python 3.12 or newer.
- `uv` for Python installation, `.venv`, dependencies, commands, and locking.
- Root `pyproject.toml` and committed `uv.lock`.
- FastAPI for HTTP APIs and the OpenAPI contract.
- Pydantic for request/response contracts, configuration, and structured
  external-output validation.
- SQLAlchemy 2 for persistence and Alembic for migrations.
- PostgreSQL as the system of record.
- `pytest` for backend tests.
- Ruff for formatting and linting; Pyright or mypy for static type checking.

### Background processing and extraction

- Use Celery with Redis when a real asynchronous parsing or generation workflow
  is introduced.
- Use Docling as the first adapter for PDF, PPTX, DOCX, and image extraction.
- Put official model-provider SDKs behind application-owned LLM and embedding
  ports. Domain and application code must not import provider SDKs.
- Do not add Celery, Redis, Docling, an LLM provider, or embeddings merely to
  prepare for hypothetical future work. Release 0 authoring does not itself
  justify document ingestion or AI generation.

### Data and files

- PostgreSQL owns vocabulary records, tasks, revisions, publication snapshots,
  editorial state, answer/scoring records, feedback, and provenance.
- Use S3-compatible storage for uploads and derived binary artifacts; use MinIO
  locally. PostgreSQL stores object keys and metadata, not binary payloads.
- Add pgvector only after an accepted semantic-retrieval use case exists. Do not
  introduce a separate vector database by default.
- Release 0 should not require object storage if it has no accepted upload or
  binary-artifact use case.

### Frontend

- Next.js App Router, React, and strict TypeScript.
- Tailwind CSS and shadcn/ui.
- `pnpm` for packages and scripts; commit `pnpm-lock.yaml`.
- ESLint for static analysis.
- Vitest and Testing Library for unit and component tests.
- Playwright for critical learner and author workflows.
- Consume the FastAPI OpenAPI contract. Generate or derive client types; do not
  manually duplicate backend request and response schemas.

## Repository shape

Use a monorepo with explicit boundaries. Start with this shape unless an
existing implementation already provides equivalent separation:

```text
backend/
  src/ioai/
    domain/
    application/
    adapters/
    entrypoints/api/
    workers/
  tests/
    unit/
    integration/
  alembic/
frontend/
  apps/
    learn/
    studio/
  packages/
    api-client/
    ui/
    vocabulary/
  tests/e2e/
pyproject.toml
uv.lock
package.json
pnpm-workspace.yaml
pnpm-lock.yaml
```

Keep the learner and author frontends as separate applications during Release
0, but make their routes merge-safe:

- learner: `http://localhost:3000/problems` and public problem routes;
- author: `http://localhost:3001/author/problems` and descendants;
- bind the Studio development server to `127.0.0.1` by default;
- never treat a separate port as authentication or production security.

Share only stable primitives, generated API types, and genuinely common UI.
Do not couple the apps through imports from each other's application folders.

## Architecture rules

Use domain-centered, dependency-inverted boundaries:

```text
HTTP / Celery / CLI
        ↓
application use cases
        ↓
domain model and policies
        ↑
ports implemented by PostgreSQL, object storage, Docling, and providers
```

- Domain code contains entities, value objects, invariants, policies, and
  domain errors. It must not import FastAPI, Celery, SQLAlchemy, Docling, Redis,
  storage SDKs, or model-provider SDKs.
- Application use cases coordinate domain behavior through narrow typed ports.
- FastAPI endpoints translate HTTP contracts and invoke one use case. They do
  not contain publication, vocabulary, scoring, or workflow rules.
- Celery tasks deserialize a job, call an application use case, and report the
  outcome. They do not implement parsing or generation policy.
- SQLAlchemy models and repositories map persistence data; they do not become
  the domain model.
- Adapters own framework and provider-specific behavior.
- Inject clocks, IDs, randomness, storage, and external services where behavior
  depends on them. Avoid import-time work and mutable global state.

Prefer straightforward modules and functions over speculative frameworks,
generic repositories, service locators, or deep inheritance trees.

## Domain invariants

### Controlled vocabulary

- `vocab.md` is the sole authority. Runtime code must consume a validated
  structured representation derived from it, not maintain parallel hand-coded
  enums or label lists.
- Add a deterministic generator or import step and a test that fails when the
  structured representation is out of sync with `vocab.md`.
- Identity is the composite `(vocabulary_type, code)`. Never assume `code` is
  globally unique.
- Store canonical codes; translate only at presentation boundaries.
- Every record has nested `labels.en` and `labels.vi` data as defined by the
  vocabulary.
- Topic parentage comes from explicit `parent_code` values, never Markdown
  heading position.
- Validate missing parents, self-parenting, cycles, and duplicate canonical
  labels or aliases within a parent branch.
- Preserve canonical future-facing values. A central Release 0 availability
  policy decides which values authors may publish.
- Unapproved or release-ineligible proposals may be recorded for review but
  must not appear on published problems.

### Learning concepts

- A stage answers where the learner is in the pathway.
- A competency describes an observable assessable ability.
- A topic identifies a concept, method, tool, or technique.
- A prerequisite is a typed reference, never a free-form tag.
- Difficulty is relative to stage; always present stage and difficulty together.
- Task status is only `NOT_STARTED`, `ATTEMPTED`, or `COMPLETED` in initial
  releases.
- Learning evidence is `INTRODUCED`, `PRACTICED`, `APPLIED`, or `PROFICIENT`.
- Task status and learning evidence are different dimensions. Never add or infer
  `MASTERED`.

### Problem metadata and publication

- A problem has exactly one pathway stage, primary competency, difficulty, and
  task type; zero to three secondary competencies; and valid topic references.
- Show at most two topics on a learner row/card and collapse the remainder.
- Searchable topic selection is hierarchical and may include descendants only
  through an explicit option.
- English/Vietnamese labels and approved aliases are searchable, but persisted
  selections remain canonical codes.
- `expected_minutes` is a positive integer; resource limits are exact numeric
  fields. Display categories are derived.
- `NONE` data modality is mutually exclusive with actual modalities.
- Scoring component weights total exactly `1.0` according to a decimal-safe
  domain rule.
- Learning objectives use observable verbs and describe assessable behavior.
- Editorial status is separate from learner task status. Use the Release 0 flow
  `DRAFT → IN_REVIEW → CHANGES_REQUESTED → APPROVED → PUBLISHED → ARCHIVED`.
- Every editorial transition records time and an author-entered note.
- Publishing requires validation and approval.
- Editing a published problem creates a draft revision. The public snapshot
  remains unchanged until the revision is approved and published.
- Public queries and builds can return only published snapshots. Enforce this
  in repository/API boundaries and prove it with tests.
- Permanent public URLs must remain stable after publication.

## API rules

- Version APIs under `/api/v1`.
- Separate public reads/submissions from author commands in routing and use
  cases. Author HTTP routes should live under `/api/v1/author/...`.
- Do not expose draft fields through public response schemas.
- Use explicit pagination, sorting, filtering, and error contracts.
- Use stable machine-readable error codes plus safe human-readable messages.
- Generate the OpenAPI document deterministically and update the frontend client
  when the contract changes.
- Add contract tests for generated types or client compatibility.
- Avoid leaking SQLAlchemy objects, stack traces, provider errors, object keys,
  or unpublished content through API responses.

## Frontend product rules

Follow `ui_release_0.md` exactly for page hierarchy, visual direction,
responsive behavior, states, and accessibility.

- Build the learner list at `/problems` and the Studio list/editor under
  `/author/problems`.
- Keep “IOAI Learn” and “IOAI Studio” visually unmistakable.
- The learner first viewport contains stage selection, one recommendation, and
  the beginning of the problem list; do not add a large marketing hero.
- Use the compact filter bar and searchable hierarchical topic picker.
- Preserve filters in the URL query string and preserve list position on return.
- Use cards below 768 px as specified; do not squeeze the desktop table onto
  mobile.
- Use visible labels, keyboard-safe dialogs, deterministic focus behavior, and
  WCAG 2.2 AA contrast and interactions.
- Never use color as the only status cue.
- Preview unsaved author state in learner format with a persistent “Draft
  preview — not public” banner.
- Save, approval, and publication must remain distinct actions.
- Do not invent generic dashboard content, vanity metrics, or competitive
  mechanics.

## Test-driven development

Use red–green–refactor for every behavior change:

1. Write the smallest behavior-focused test.
2. Run it and confirm it fails for the expected reason.
3. Implement only enough behavior to pass.
4. Refactor while keeping the suite green.

Do not claim TDD without observing the red step. Every bug fix begins with a
failing regression test.

### Backend tests

- Use `pytest`.
- Put pure domain and use-case tests in `backend/tests/unit`.
- Put PostgreSQL, Alembic, FastAPI, and adapter tests in
  `backend/tests/integration`.
- Test migrations both up and down when safe, schema constraints, transaction
  boundaries, public/draft isolation, vocabulary invariants, workflow
  transitions, scoring totals, and stable slugs.
- Use real domain objects and fakes at ports. Mock only when the interaction is
  itself the contract.
- Tests must not depend on developer state, live networks, wall-clock time, or
  uncontrolled randomness.

### Frontend tests

- Use Vitest and Testing Library for components, hooks, and page behavior.
- Query the UI by accessible role/name where possible; avoid implementation-
  detail selectors.
- Cover filtering, hierarchical topic selection, table/card responsive
  behavior, status/evidence separation, form validation, autosave failure, and
  preview warnings.
- Use Playwright for critical flows: learner browse → open problem → submit →
  continue; and author draft → validate → preview → review → publish → verify
  public visibility.
- Keep the Playwright suite focused on critical integration paths, not every
  component permutation.

## Database and migration discipline

- Model PostgreSQL constraints that protect real invariants; duplicate critical
  validation in the domain for actionable errors.
- Use explicit SQLAlchemy 2 mappings and transaction boundaries.
- All schema changes use Alembic. Never mutate a shared database manually.
- Give migrations descriptive revision messages and make data migrations
  deterministic and reviewable.
- Do not rewrite an already-shared migration; add a new migration.
- Test repository behavior against PostgreSQL rather than relying on SQLite
  compatibility.
- Keep seeds/fixtures deterministic and based on canonical codes.

## Clean-code expectations

- Keep modules, classes, functions, and components focused on one responsibility.
- Use domain language consistently in Python, TypeScript, database names, tests,
  and UI copy.
- Prefer explicit data flow and typed values over hidden mutable state.
- Validate at boundaries and keep internal invariants obvious.
- Raise specific, actionable errors; never silently swallow failures.
- Comments explain intent or constraints, not syntax.
- Remove dead code. Do not leave commented-out implementations.
- Do not add an abstraction until at least one current requirement needs it.
- Do not mix unrelated refactors with a feature or bug fix.

## Commands and quality gates

Use project scripts when they exist. The expected baseline is:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest

pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
pnpm build
```

During TDD, run the smallest relevant test first. Before declaring work done,
run all relevant formatting, lint, type, test, migration, OpenAPI/client-
generation, and production-build checks.

## Working rules for agents

- Inspect the repository and relevant governing documents before editing.
- Preserve user changes and unrelated work; never rewrite or delete it to make a
  task easier.
- State important assumptions when a requirement is ambiguous, but prefer the
  smallest Release 0 interpretation.
- Keep changes vertical and reviewable: schema/domain → use case → adapter/API →
  generated client → UI → tests.
- Update tests and documentation with behavior or workflow changes.
- Keep secrets in ignored local environment files and document required keys in
  `.env.example` using non-secret placeholders.
- Commit lockfiles. Do not commit `.venv`, `node_modules`, caches, generated
  coverage, local databases, uploaded objects, or secrets.
- Do not report completion if tests were skipped, failing, or not run. State the
  exact limitation.

## Definition of done

A Release 0 change is done only when:

- its acceptance behavior is clear and remains within Release 0 scope;
- a relevant test was observed failing before implementation;
- backend domain rules remain outside frameworks and adapters;
- vocabulary references use canonical structured data and pass invariants;
- public endpoints cannot expose drafts or unapproved revisions;
- FastAPI OpenAPI and generated frontend types agree;
- backend and frontend unit/integration tests pass;
- critical affected Playwright workflows pass;
- formatting, linting, static typing, migrations, and production builds pass;
- accessibility and the responsive widths specified in `ui_release_0.md` are
  verified for affected UI;
- lockfiles and migrations are intentional;
- documentation is updated;
- no secrets, local artifacts, dead code, or unrelated changes are included.
