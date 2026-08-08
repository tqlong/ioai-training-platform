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

## 3. Domain modules and aggregate boundaries

### 3.1 Domain module map

| Domain module | Owns | Does not own |
| --- | --- | --- |
| `vocabulary` | Typed vocabulary identity, bilingual labels/aliases, topic parent references, graph invariants, canonical status | Markdown parsing, SQL sessions, UI labels, or HTTP responses |
| `policy` | Release 0 availability for stages, task types, compute, modalities, and scoring | Canonical vocabulary completeness or deployment authorization |
| `problems` | Stable problem identity, slug rules, revision content, metadata, response configuration, resources, and scoring components | Editorial transition orchestration or persistence mapping |
| `prerequisites` | Typed target references, relationship, and minimum evidence | Free-form tags or recommendation ranking |
| `assessment` | Response contracts, validation outcomes, decimal-safe weighted scoring, pending/manual results, safe feedback data | Hidden provider details or editorial approval |
| `editorial` | Status transition policy, required notes, approval/publication/archive rules, audit transition values | Learner task status or account identity |
| `learning` | Task status/evidence interpretation, attempt result vocabulary, recommendation eligibility inputs | Permanent publication state or claims of mastery |
| `feedback` | Bounded categories/messages and abuse-validation policy | Unbounded moderation platform or user identity |

Application use cases may coordinate multiple modules, but one module remains
the owner of each invariant. A publication use case can ask `problems` to
validate a revision, `policy` to check availability, and `editorial` to validate
a transition; it must not duplicate those rules (`R0-012`, `R0-013`, `R0-014`,
analysis sections 4 and 8).

### 3.2 Aggregate and value-object boundaries

The `Problem` aggregate owns stable identity and revision references. A
`ProblemRevision` value graph owns bilingual structured content, canonical
metadata references, typed prerequisites, response configuration, resources, and
scoring components. A `PublishedSnapshot` is immutable output of a successful
publication and is not a mutable child of the draft aggregate. This prevents an
edit from mutating public content before review and publication (`R0-014`,
`AC-R0-014-09`, `AC-R0-014-10`).

The following value objects should be explicit rather than bare strings:

- `VocabularyIdentity(vocabulary_type, code)`;
- bilingual `LocalizedText` and approved alias collection;
- `StableSlug` with normalization and uniqueness checked at the persistence
  boundary;
- `EditorialStatus`, `TaskStatus`, and `LearningEvidence` values;
- `PrerequisiteReference(relationship, target_type, target_id, minimum_evidence)`;
- exact positive resource limits and `ExpectedMinutes`;
- `ResponseConfiguration` variants for the five approved task types;
- decimal-safe `ScoringWeight` and weighted scoring component collection;
- bounded `FeedbackMessage` and submission idempotency identity.

These values make invalid states difficult to construct and keep error messages
actionable before a database write (`R0-010`, `R0-012`, `R0-013`, `R0-015`,
`AC-R0-013-07` through `AC-R0-013-14`).

### 3.3 Core invariants

The aggregate boundary must enforce:

1. Exactly one stage, primary competency, difficulty, and task type; zero through
   three secondary competencies.
2. Canonical composite vocabulary references and valid explicit topic parents.
3. Typed prerequisites only, with no free-form prerequisite tags.
4. Positive expected time, exact numeric resources, and `NONE` modality
   exclusivity.
5. One of the five Release 0 response variants and an allowed compute tier.
6. Decimal-safe scoring components totaling exactly `1.0`.
7. Observable learning objective and required bilingual structured blocks,
   allowing author-visible pending translation warnings.
8. Editorial validity independent from learner status/evidence and publication
   state.

Database constraints duplicate critical identity, uniqueness, and transaction
invariants, but domain validation runs first to provide actionable errors
(`R0-013`, `R0-014`, `R0-015`, analysis sections 4 and 9).

### 3.4 State ownership

| State | Owner | Persistence/projection rule |
| --- | --- | --- |
| Draft content and revision version | Application/revision store | Author projection only; versioned saves |
| Editorial status and transition history | Editorial domain/use case | Required note and timestamp for every accepted transition |
| Published snapshot | Publication transaction/repository | Immutable public projection; no draft fields |
| Learner task status/evidence | Browser-local learning adapter, optionally informed by attempt result | Best-effort, schema-versioned, never authorization |
| Attempt/scoring result | Assessment application/persistence | Bounded server record tied to public snapshot context |
| Recommendation candidate | Learning/recommendation use case | Select from published eligible set only |
| Feedback report | Feedback application/persistence | Bounded anonymous record tied to public problem identity |

This ownership prevents completion from becoming mastery, approval from becoming
publication, or local progress from becoming identity (`R0-010`, `R0-012`,
`R0-014`, `AC-R0-012-09`, `AC-R0-014-05`).

## 4. Application use cases and ports

### 4.1 Use-case catalog

| Use case | Input/output boundary | Ports | Transaction/idempotency rule |
| --- | --- | --- | --- |
| Synchronize vocabulary | Source revision or parsed artifact -> validation report and sync result | `VocabularySource`, `VocabularyValidator`, `VocabularyRepository`, `Clock` | Validate complete artifact before an idempotent sync; never repurpose composite identity |
| Create draft | Author draft intent -> problem/revision reference and initial status | `ProblemRepository`, `IdGenerator`, `Clock` | Allocate identity and initial revision atomically; no public snapshot |
| Save draft revision | Versioned revision patch -> saved revision or conflict | `DraftRepository`, `Clock` | Optimistic version required; stale write returns conflict and does not overwrite |
| Validate revision | Revision identity/version -> structured errors/warnings | `DraftRepository`, `VocabularyRepository`, `AvailabilityPolicy`, `Validator` | Read-consistent validation; no editorial mutation |
| Preview revision | Draft/unsaved projection request -> author-only learner-shaped preview | `DraftRepository`, `PreviewProjector` | No public repository path; unsaved content is never persisted as a snapshot |
| Submit for review | Revision/version/note -> `IN_REVIEW` transition | `DraftRepository`, `EditorialPolicy`, `TransitionRepository`, `Validator` | Validate blockers and note before atomic transition |
| Request changes/approve | Revision/version/note -> editorial transition | `DraftRepository`, `EditorialPolicy`, `TransitionRepository`, `Validator` | Current status/version and required note; no partial history |
| Publish revision | Approved revision/version/note/key -> snapshot/public result | `DraftRepository`, `SnapshotRepository`, `SlugRegistry`, `TransitionRepository`, `Clock` | One transaction; idempotency key returns prior result; unique slug and validation checked |
| Archive problem | Published identity/version/note -> archived transition/public eligibility change | `ProblemRepository`, `SnapshotRepository`, `TransitionRepository` | Atomic public removal and audit history; preserve historical records |
| List public problems | URL filters/sort/page -> public list projection | `PublishedProblemReader`, `LocalProgressReader` only at composition boundary | Query source is published-only; deterministic sort and explicit pagination |
| Read public detail | Stable slug -> public snapshot projection | `PublishedProblemReader` | Resolve current published snapshot only; no revision IDs in public contract |
| Submit answer | Public snapshot/response/idempotency key -> assessment result or pending | `PublishedProblemReader`, `AttemptRepository`, `AssessmentPolicy`, `Clock` | Bind assessment to resolved snapshot; duplicate key is safe and bounded |
| Record feedback | Public problem/category/message -> accepted/rejected report | `PublishedProblemReader`, `FeedbackRepository`, `AbusePolicy`, `Clock` | Validate size/category/rate before bounded insert |
| Recommend next problem | Stage/local history/current identity -> one public recommendation | `PublishedProblemReader`, `PrerequisiteReader`, `RecommendationPolicy` | Candidates are published and policy-eligible; no mastery inference |

Use cases return application DTOs or typed outcomes, never SQLAlchemy entities,
FastAPI responses, stack traces, or provider exceptions. Public readers and
author commands are separate ports even when they share storage adapters
(`R0-014`, analysis sections 4, 6-9).

### 4.2 Port contracts

Ports are narrow protocols owned by the application/domain boundary. Important
port families are:

- `PublishedProblemReader`: list/detail/candidate queries that cannot return a
  non-published revision by type or method contract;
- `DraftRepository`: revision reads and versioned writes for author use cases;
- `SnapshotRepository`: immutable snapshot creation and current-public lookup;
- `TransitionRepository`: append-only editorial history and current status;
- `VocabularyRepository`: typed records, explicit topic graph, and sync status;
- `AssessmentPort`: response-specific validation/scoring with safe result DTOs;
- `AttemptRepository` and `FeedbackRepository`: bounded learner records;
- `RecommendationPolicy` and `AvailabilityPolicy`: pure policy decisions;
- `Clock`, `IdGenerator`, and `IdempotencyStore`: injected nondeterminism and
  retry coordination.

No port exposes a generic `get_problem()` that requires every caller to add a
status predicate. Public and author reads must be semantically distinct to
enforce the isolation analysis (`R0-014`, `R0-015`, analysis section 9).

### 4.3 Error and outcome model

Application outcomes use stable machine-readable categories such as:

| Category | Examples | Public handling |
| --- | --- | --- |
| `VALIDATION_FAILED` | Missing objective, invalid response, bad weights | Field/section guidance; no mutation |
| `VOCABULARY_INVALID` | Unknown composite identity, missing parent, ambiguous alias | Safe canonical-selection guidance |
| `POLICY_DISALLOWED` | GPU, unsupported task type, unavailable scoring | Block publication/submission path |
| `REVISION_CONFLICT` | Stale autosave, stale approval/publication | Preserve current state and request refresh/resolve |
| `WORKFLOW_INVALID` | Missing note or invalid editorial transition | No state/history change |
| `PUBLIC_NOT_FOUND` | No current published snapshot or archived problem | Safe public not-found response |
| `IDEMPOTENCY_REPLAY` | Previously completed command key | Return original safe outcome |
| `RATE_LIMITED` | Excessive anonymous feedback/submission | Bounded retry guidance |
| `DEPENDENCY_UNAVAILABLE` | Database or assessment dependency unavailable | Retry-safe generic message, no infrastructure detail |

Adapters map framework/provider failures into these categories at the
application boundary. Public responses omit SQL, object keys, answer data,
provider messages, and unpublished content (`R0-015`, `AC-R0-015-13`).

### 4.4 Transaction ownership

The use case owns transaction intent; the persistence adapter owns session
mechanics. Publication, status transition, snapshot creation, and required
history are one transaction. Draft autosave, learner submission, and feedback
are separately bounded transactions with explicit idempotency/concurrency
rules. A use case must not perform multiple independent writes and claim they
are atomic (`R0-014`, `R0-015`, `AC-R0-014-05`, `AC-R0-015-09`).
