# Release 0 Design

Status: In progress. This document turns the accepted requirements and Phase 2
analysis into implementation-ready design decisions. It does not authorize
features excluded or deferred by `requirement_release_0.md`.

## Design rules

- Every design decision cites `requirement_release_0.md` requirement groups and
  the relevant `analysis_release_0.md` sections. Behavioral contracts also cite
  acceptance-criteria ranges where useful.
- Domain rules remain independent of FastAPI, Next.js, SQLAlchemy, Celery,
  Redis, storage SDKs, and model-provider SDKs.
- Public projections are published-only by construction. Author and preview
  projections are separate contracts.
- Release 0 enables only `QUIZ_SINGLE`, `QUIZ_MULTIPLE`, `NUMERIC_ANSWER`,
  `SHORT_ANSWER`, and `CODE_FUNCTION`, with `NONE`, `BROWSER`, or `CPU_LIGHT`
  compute. Future canonical values remain data, not publishable capability.
- A separate port and loopback binding organize the no-auth local pilot; they do
  not provide authorization.
- Open choices from analysis section 11 must be resolved here or recorded as an
  ADR before implementation depends on them.

## 1. System context and boundaries

### 1.1 Context diagram

```text
                 public reads/submissions/feedback
 Anonymous learner browser ------------------------------+
        |                                                |
        v                                                v
  Learner Next.js :3000  --------------------------> FastAPI :8000
        ^                                                ^
        | public learner routes                         |
        |                                                | public + author APIs
        |                                                |
        |                                                +------------------+
        |                                                                   |
 Local author/reviewer browser                                             v
        |                                      PostgreSQL :5432
        v                                      authoritative records
  Studio Next.js :3001 ------------------------------^
  (127.0.0.1 by default)                              |
                                                       +--> health/readiness

 Learner browser local storage
 (anonymous progress only; never an authorization or publication source)
```

The two frontend applications share stable primitives and generated contracts,
not application-folder imports. The learner app is public-facing; Studio is a
distinct local editorial surface. FastAPI is the only application boundary that
coordinates domain use cases with persistence. PostgreSQL is the system of
record for vocabulary, problems, revisions, snapshots, workflow history,
attempts, and feedback (`R0-010`, `R0-014`, analysis sections 1-3 and 9).

### 1.2 Context boundaries

| Boundary | In scope | Explicitly not in scope | Design consequence |
| --- | --- | --- | --- |
| Learner browser -> Learn/API | Public published reads, filters, permanent detail, accepted submissions, feedback, device-local progress | Draft reads, author commands, accounts, cross-device progress | Public response schemas and routes contain no draft fields; local state cannot authorize or publish (`R0-011`, `R0-012`, `AC-R0-015-10`) |
| Author/reviewer browser -> Studio/API | Draft editing, preview, validation, editorial commands, local review/publication workflow | Identity provider, public deployment of unauthenticated Studio | Server validates every command; loopback is a deployment default, not an authorization check (`R0-013`, `R0-014`, `AC-R0-015-11`) |
| FastAPI -> domain/application | Typed use-case invocation, safe errors, transaction intent, ports | Business rules in HTTP handlers | Endpoints translate contracts and invoke one use case; domain owns invariants (`R0-015`, analysis sections 4 and 11) |
| Application -> PostgreSQL | Authoritative persistence and transactions | Binary payload storage, unrestricted ORM leakage | Repositories expose narrow public/author ports and published-only projections (`R0-014`, analysis section 9) |
| Local operations -> services | Process startup, migrations, health, backup/restore | Production security boundary or external orchestration | Compose is reproducible and explicit; required base services only (`R0-015`, analysis sections 2 and 10) |

### 1.3 Actors and component ownership

| Actor | Primary component/use-case surface | Cannot do through design |
| --- | --- | --- |
| Learner | Learn routes, public API, local-progress adapter, submission/feedback use cases | Read drafts, select editorial states, mutate vocabulary or snapshots |
| Author | Studio routes, author API, draft and validation use cases | Publish invalid/unapproved/unavailable revisions or change canonical vocabulary inline |
| Reviewer | Studio editorial commands and audit history | Bypass required notes, status transitions, approval/publication separation |
| Curriculum owner | Vocabulary synchronization and policy governance | Turn a proposal or future canonical value into publishable metadata without approval |
| Local operator | Compose, migration, health, backup/restore commands | Treat port separation as authentication or add excluded services speculatively |

### 1.4 Resolved and deferred context choices

Resolved for Release 0:

- Four base services are planned: PostgreSQL, FastAPI, learner Next.js, and
  Studio Next.js (`R0-015`, analysis section 3).
- Learner defaults to port 3000; Studio defaults to `127.0.0.1:3001`; FastAPI
  uses a documented local API port.
- PostgreSQL is authoritative; browser-local progress is best-effort convenience
  state (`R0-010`, `R0-012`, `AC-R0-012-09` through `AC-R0-012-11`).

Deferred to later design sections or ADRs:

- Exact PostgreSQL isolation/locking, backup retention/provider, observability
  sink, browser matrix, API generation command, and local-progress schema
  versioning. These are listed in analysis section 11.2 and cannot expand scope.
- Redis, Celery, Docling, MinIO, embeddings, model providers, GPU execution,
  authentication, and cross-device identity are excluded unless an accepted
  requirement changes (`R0-010`, requirement section 15.3).

## 2. Monorepo architecture and dependency direction

### 2.1 Repository boundaries

```text
backend/
  src/ioai/
    domain/              framework-free entities, policies, value objects
    application/         typed use cases and port protocols
    adapters/            SQLAlchemy, settings, clocks, IDs, external adapters
    entrypoints/api/     FastAPI factories, HTTP contracts, route translation
    workers/             reserved boundary; no worker added without a use case
  tests/
    unit/                domain and application tests
    integration/         PostgreSQL, Alembic, FastAPI, adapter tests
  alembic/               migration environment and revisions

frontend/
  apps/
    learn/               public learner application, port 3000
    studio/              local editorial application, port 3001
  packages/
    api-client/          generated OpenAPI-derived TypeScript client
    ui/                  stable shared primitives only
    vocabulary/          generated/validated vocabulary data and types
  tests/e2e/             focused cross-application workflows
```

Root `pyproject.toml`/`uv.lock` own Python tooling and root
`package.json`/`pnpm-workspace.yaml`/`pnpm-lock.yaml` own frontend tooling.
The learner and Studio apps may depend on shared `ui`, `api-client`, and
`vocabulary` packages, but neither app imports from the other app's application
folder (`R0-010`, `R0-015`, analysis sections 1-4).

### 2.2 Dependency direction

```text
FastAPI / CLI / future worker entrypoints
                  |
                  v
        application use cases
                  |
                  v
        domain entities/policies
                  ^
                  |
       typed ports and protocols
                  ^
                  |
 SQLAlchemy/PostgreSQL, clocks, IDs, storage/provider adapters
```

The dependency rule is one-way:

- Domain imports only standard-library and domain-owned types. It does not
  import FastAPI, SQLAlchemy, Pydantic, Celery, Redis, or provider SDKs.
- Application code coordinates domain behavior through narrow typed ports. It
  does not know HTTP status codes, ORM sessions, or frontend state.
- API entrypoints translate validated HTTP contracts into one use-case call and
  map typed errors to safe response contracts. They do not implement publication,
  vocabulary, scoring, or isolation policy.
- Adapters implement ports and map persistence/external formats to domain data.
  SQLAlchemy models are persistence mappings, not domain entities.
- Frontend apps consume generated contracts and stable shared primitives. They
  do not duplicate backend schemas or import backend implementation modules.

This keeps the high-risk invariants identified in analysis sections 4, 8, and 9
testable without frameworks and prevents public routing choices from becoming
the only draft-isolation control (`R0-015`, `AC-R0-015-07`, `AC-R0-014-12`).

### 2.3 Cross-cutting dependency injection

Use-case constructors receive clocks, ID generators, repositories, policy
providers, and assessment ports where behavior depends on them. FastAPI binds
request-scoped dependencies; tests provide deterministic fakes. No import-time
database connection, mutable singleton, random seed, or wall-clock decision is
allowed. This supports deterministic tests, migration safety, idempotency, and
reproducible recommendations (`R0-015`, `AC-R0-015-18`).

### 2.4 Architecture decisions and exclusions

The architecture intentionally does not create generic repositories, service
locators, deep inheritance trees, or a worker system without an accepted
asynchronous use case. A `workers/` boundary may exist as a documented future
location, but Release 0 authoring, lightweight scoring, and vocabulary import
remain synchronous unless requirements and analysis change (`R0-010`, analysis
sections 3 and 11.4).
