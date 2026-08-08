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

## 5. Vocabulary ingestion and Release 0 policy

### 5.1 Generation pipeline

```text
vocab.md
  -> deterministic parser
  -> normalized typed records
  -> graph/uniqueness/label validation
  -> stable structured artifact
  -> drift check + runtime package
  -> idempotent PostgreSQL synchronization
```

The parser is an adapter owned outside the domain. It extracts declared values,
labels, aliases, statuses, and explicit parent codes; it never infers topic
parentage from Markdown heading position. The domain validator receives typed
records and checks composite identity, parent resolution, self-parenting, cycles,
branch ambiguity, bilingual labels, alias uniqueness, and status shape. A failed
validation produces no synchronization write (`R0-010`, `R0-013`, `R0-015`,
analysis section 5).

The generated artifact is deterministic: records use stable vocabulary-type and
code ordering, normalized field representation, and no timestamps or machine
paths. The drift command parses the source and compares the generated result;
it fails with a field-level diff when identity, labels, aliases, parentage, or
status changes. Runtime and fixtures consume the artifact instead of parallel
enums (`AC-R0-015-19`).

### 5.2 Composite identity and search design

```text
VocabularyIdentity
  vocabulary_type: canonical vocabulary family
  code: stable uppercase canonical code
```

Every repository key, API selection, fixture, and problem metadata reference
stores both fields. Search indexes may denormalize English labels, Vietnamese
labels, and approved aliases, but the selected result resolves back to the
composite identity before persistence. Competency and topic records with the
same code remain distinct (`R0-010`, `R0-011`, `R0-013`, `AC-R0-011-07`,
`AC-R0-013-08`).

Topic records store explicit `parent_code` within the topic vocabulary. A
hierarchical picker can return family, intermediate, and leaf records and can
optionally expand descendants only when the caller supplies an explicit
include-descendants option. The policy is shared by learner search and author
selection but the projections differ (`AC-R0-011-08`, `AC-R0-013-09`).

### 5.3 Availability policy

Availability is a pure central policy evaluated at author validation,
publication, public candidate selection, and any task fixture generation. It
does not remove canonical future records.

| Dimension | Release 0 enabled values | Design rule |
| --- | --- | --- |
| Task type | `QUIZ_SINGLE`, `QUIZ_MULTIPLE`, `NUMERIC_ANSWER`, `SHORT_ANSWER`, `CODE_FUNCTION` | Any other canonical task type is stored but publication-blocking |
| Compute tier | `NONE`, `BROWSER`, `CPU_LIGHT` | GPU, distributed, and higher CPU values are publication-blocking |
| Scoring | `EXACT_MATCH`, `UNIT_TESTS`, `PARTIAL_TESTS`, `RUBRIC_HUMAN` | Weights are decimal-safe and total exactly `1.0` |
| Modality | `NONE` alone, or actual modalities without `NONE` | `NONE` is mutually exclusive with actual data modalities |

The policy returns a typed decision with enabled/disabled status, reason code,
and safe display message. A disabled value can be visible as unavailable to an
author, but cannot be silently downgraded or published (`R0-012`, `R0-013`,
`R0-016`, `AC-R0-012-04`, `AC-R0-013-14`).

### 5.4 Proposals and synchronization

“Can’t find the right value?” creates a bounded proposal associated with author
context and a note. It does not create a vocabulary record and cannot satisfy a
problem revision's canonical reference. Curriculum-owner approval changes the
canonical source through the vocabulary workflow, after which regeneration and
drift checks are required (`AC-R0-013-10`).

Synchronization is idempotent by composite identity. Existing records may
receive approved label/alias/status updates, but a changed type or code is a new
identity and cannot repurpose the old record. The sync result reports added,
updated, unchanged, rejected, and policy-disabled records without leaking
provider or database details (`R0-015`, `AC-R0-015-07`).

## 6. Public learner API design

### 6.1 Resource surface

All public resources are versioned under `/api/v1` and return published-safe
DTOs. Proposed resource surface:

| Method and path | Purpose | Source/projection |
| --- | --- | --- |
| `GET /api/v1/problems` | List/search/filter/sort/paginate public problems | `PublishedProblemReader` list projection |
| `GET /api/v1/problems/{slug}` | Read a permanent problem URL | Current published snapshot projection |
| `GET /api/v1/problems/{slug}/recommendation` | Get one editorially eligible next problem | Published recommendation projection |
| `POST /api/v1/problems/{slug}/submissions` | Submit one accepted response | Snapshot-bound assessment result/pending projection |
| `POST /api/v1/problems/{slug}/feedback` | Send bounded anonymous problem feedback | Accepted feedback receipt |
| `GET /api/v1/vocabulary` | Public-safe hierarchy/search values for discovery | Canonical active vocabulary projection, no draft proposals |

The API never accepts a revision ID, draft ID, preview token, or author-only
field in a public problem read/submission path. A slug resolves to the current
published snapshot, and a missing/archived/unpublished problem returns a safe
public not-found contract (`R0-011`, `R0-012`, `R0-014`, analysis section 9).

### 6.2 List query contract

`GET /api/v1/problems` supports explicit query parameters for:

- `stage`, `competency`, `topic`, `include_subtopics`, `difficulty`, `task_type`;
- `task_status`, `learning_evidence`, `expected_minutes`, and `compute_tier`;
- bilingual `q` search across approved public titles/objectives/labels/aliases;
- `sort` limited to editorial order, newest, expected time, or title;
- `page`, `page_size`, and a stable pagination shape.

Selections use canonical composite vocabulary identity in query semantics, while
labels and aliases are accepted only as search input. The API returns active
filter state, result count, explicit page metadata, and at most two visible topic
labels plus a remainder count. Parent topics include descendants only when
`include_subtopics=true` is explicitly supplied (`R0-011`,
`AC-R0-011-07` through `AC-R0-011-11`).

Sort order is deterministic: the default is editorial learning-path order then
difficulty, and every alternative sort has a stable tie-breaker by problem
identity. Public pagination is evaluated over the published-only set before
records are serialized, preventing a draft from shifting or leaking through a
page boundary (`AC-R0-011-01`, `AC-R0-011-10`).

### 6.3 Public response projections

The list projection contains only learner-needed fields:

```text
ProblemListItem
  stable_slug / public_short_id
  title
  observable_learning_objective
  stage + difficulty
  primary_competency
  visible_topics[0:2] + remaining_topic_count
  task_type_label
  expected_minutes
  compute_tier_label
  local task_status/evidence overlay (client-composed)
```

The detail projection adds published learner blocks, prerequisites, response
schema, allowed resource summary, hints/explanation policy, feedback affordance,
and recommendation context. It omits revision IDs, editorial notes, draft
warnings, internal answer keys, hidden tests, object keys, provider metadata,
and unpublished translations (`R0-011`, `R0-012`, `R0-014`, `AC-R0-012-07`).

### 6.4 Submission and feedback contracts

Submission input is a discriminated union keyed by the published task type:

```text
SubmissionRequest
  response_type: canonical task type
  answer: type-specific bounded payload
  client_submission_key: bounded idempotency key
```

The server resolves the slug to one snapshot, validates the union and resource
limits, and returns one of `ACCEPTED_RESULT`, `PENDING_ASSESSMENT`, or a stable
validation/dependency error. The result contains outcome, safe score/rubric
summary, feedback, and task-status/evidence hints only; it never returns hidden
answers or test data (`R0-012`, `AC-R0-012-05` through `AC-R0-012-08`).

Feedback input contains a bounded canonical category and bounded message. The
server verifies the public problem exists, applies abuse/size controls, and
returns a receipt without exposing moderation internals. Duplicate or excessive
requests return safe rate/idempotency outcomes (`AC-R0-012-12` through
`AC-R0-012-14`).

### 6.5 Errors, request IDs, and URL state

Every response may include a request ID and errors use the application
categories defined in section 4.3. Public mapping is deliberately coarse for
dependency failures and never includes stack traces, SQL, filesystem paths,
provider messages, answer data, or draft content (`R0-015`,
`AC-R0-015-13`, `AC-R0-015-15`).

The frontend owns the shareable filter query string and sends it to this API;
the API does not store anonymous filter state. The permanent problem slug is
stable across revisions and is the only public identity needed to reopen a
published problem (`AC-R0-011-09`, `AC-R0-011-15`, `AC-R0-011-16`).

## 7. Author and editorial API design

### 7.1 Command surface

Author commands are versioned under `/api/v1/author` and are separate from
public resources:

| Method and path | Purpose | Required command data |
| --- | --- | --- |
| `GET /api/v1/author/problems` | List draft/revision work | Internal status, version, last-save metadata; author-safe only |
| `POST /api/v1/author/problems` | Create a draft problem | Draft initialization intent |
| `GET /api/v1/author/problems/{problem_id}` | Read current author aggregate | Revision and validation context |
| `POST /api/v1/author/problems/{problem_id}/revisions` | Start edit of published problem | Base published identity/version |
| `PUT /api/v1/author/revisions/{revision_id}` | Versioned autosave | Revision version and structured patch/full draft |
| `POST /api/v1/author/revisions/{revision_id}/validate` | Validate draft | Revision version |
| `POST /api/v1/author/revisions/{revision_id}/preview` | Create/read preview projection | Revision version and explicit preview context |
| `POST /api/v1/author/revisions/{revision_id}/submit-review` | Submit for review | Current version and required note |
| `POST /api/v1/author/revisions/{revision_id}/request-changes` | Request changes | Current version and required reviewer note |
| `POST /api/v1/author/revisions/{revision_id}/approve` | Approve revision | Current version and required reviewer note |
| `POST /api/v1/author/revisions/{revision_id}/publish` | Publish approved revision | Current version, note, idempotency key |
| `POST /api/v1/author/problems/{problem_id}/archive` | Archive public problem | Current public version and required note |

The exact path names remain subject to the final OpenAPI design, but the public
versus author separation and command semantics are fixed here. A future access
control layer can wrap these commands without changing public DTOs; Release 0
does not infer authentication from the route or port (`R0-014`, `R0-015`,
analysis sections 3 and 9).

### 7.2 Draft and revision contracts

Draft responses may include revision ID, editorial status, validation issues,
pending translation indicators, autosave version, internal notes, and preview
context. They must never be serializable by public schemas or accepted by public
routes. A draft write includes:

```text
DraftWrite
  revision_id
  expected_version
  structured_revision_patch or complete_revision
  client_save_key (optional bounded retry key)
```

The server returns the accepted version, normalized revision data, save status,
and warnings. A stale `expected_version` returns `REVISION_CONFLICT` with the
current version reference but does not merge or overwrite automatically
(`R0-013`, `AC-R0-013-15` through `AC-R0-013-18`).

### 7.3 Validation and preview contracts

Validation returns a stable report:

```text
ValidationReport
  revision_id
  revision_version
  errors[]: { code, section, field_path, message }
  warnings[]: { code, section, field_path, message }
  publication_eligible: boolean
```

Errors cover structural fields, canonical references, Release 0 policy,
resources, scoring total, stable slug, and workflow prerequisites. Warnings may
include pending translations but cannot override a publication blocker
(`R0-013`, `AC-R0-013-19`).

Preview returns a learner-shaped draft projection with a persistent
`Draft preview - not public` marker and author-only warning metadata outside the
learner content. Preview requests are never resolved by public slug and are not
eligible for list/search/recommendation/build caches (`AC-R0-013-20`,
`AC-R0-013-21`).

### 7.4 Editorial command contracts

Every transition request includes `revision_id`, `expected_version`, a bounded
human-entered `note`, and an idempotency key when the command has a public or
history side effect. The application checks current status, validation, policy,
slug uniqueness, and version before writing an immutable transition history
entry. Allowed transitions are exactly:

```text
DRAFT -> IN_REVIEW -> CHANGES_REQUESTED
                    \-> APPROVED -> PUBLISHED -> ARCHIVED
```

`CHANGES_REQUESTED` returns the revision to author editing according to the
workflow policy; published edits create a new revision rather than mutating the
current snapshot. Approval and publication remain distinct commands. Publication
creates the immutable snapshot and successful history transition atomically;
replaying the same publication idempotency key returns the original public
result (`R0-014`, `AC-R0-014-01` through `AC-R0-014-16`).

### 7.5 Author error and response safety

Author responses may explain validation and workflow errors more fully than
public responses, but they still omit stack traces, SQL, provider errors,
secrets, object storage keys, and unrelated drafts. A missing note, stale
version, invalid transition, unavailable policy value, or conflicting slug
returns a stable error and changes no state (`R0-014`, `R0-015`,
`AC-R0-014-11`, `AC-R0-014-16`).

## 8. OpenAPI and generated-client governance

### 8.1 Contract ownership

FastAPI/Pydantic response and request models are the source of the HTTP
contract. The OpenAPI document is generated from the application entrypoint in
a deterministic command that does not require a live database, wall-clock data,
random IDs, or network access. The generated document is committed or produced
as a reproducible CI artifact according to the repository policy chosen in
Phase 4 (`R0-015`, analysis sections 9-11).

The frontend `packages/api-client` is generated from that OpenAPI document. It
owns transport types and typed request functions, not domain logic. The learner
and Studio apps consume it rather than manually duplicating request/response
schemas. Vocabulary and shared UI packages may expose stable presentation types
but cannot redefine API contracts (`R0-010`, `R0-015`, analysis section 2).

### 8.2 Generation and drift pipeline

```text
Pydantic/FastAPI contracts
          |
          v
deterministic OpenAPI JSON
          |
          v
generated TypeScript api-client
          |
          +--> contract compatibility tests
          +--> committed/generated drift check
```

The pipeline must:

1. Generate a stable OpenAPI document with sorted output and no environment-
   specific server URLs or timestamps.
2. Generate TypeScript types/client functions using one pinned toolchain.
3. Fail when generated output differs from the committed artifact, if artifacts
   are committed, or when the client is generated from a different contract.
4. Run compatibility checks for public and author response projections,
   pagination/filter contracts, stable errors, idempotency headers/fields, and
   draft-safe schema separation.
5. Make the command discoverable through `uv`/`pnpm` scripts and CI.

The final generator/tool choice is an open implementation decision from analysis
section 11.2; the invariants above are not open (`AC-R0-015-19`).

### 8.3 Schema separation rules

Public schemas are named and tested separately from author schemas:

- Public list/detail/submission/feedback schemas contain published learner
  content and safe assessment results only.
- Author draft/revision/validation/preview/workflow schemas may contain internal
  revision IDs, versions, warnings, notes, and editorial status.
- Shared fields are copied through explicit projection models, not inheritance
  from an author schema into a public schema.
- SQLAlchemy models, Pydantic ORM serialization, object keys, hidden answers,
  and provider exceptions never cross the HTTP contract boundary.

The contract test should construct a representative draft containing every
author-only field and assert that each public response remains free of it. It
should also assert that a public request cannot name a revision or preview
identifier (`R0-014`, `R0-015`, `AC-R0-014-12`, `AC-R0-015-13`).

### 8.4 Compatibility and evolution

Adding an optional response field is compatible; removing or changing the
meaning/type of a public field requires an explicit versioning decision. Stable
problem URLs and canonical codes are data contracts and cannot be changed as a
shortcut for API evolution. Author-only additions must not widen public
projections. Contract changes update the generated client, affected tests,
documentation, and traceability entry in one reviewable change (`R0-011`,
`R0-014`, `R0-016`).

## 9. PostgreSQL conceptual model

### 9.1 Entity relationship view

```text
vocabulary_record (vocabulary_type, code) 1---* topic_parent_edge
                  ^                              |
                  |                              v
             problem_revision *---* vocabulary_record
                  |
                  +---* prerequisite_reference
                  +---1 response_configuration 1---* scoring_component
                  +---* editorial_transition
                  |
                  +---0..1 published_snapshot

problem 1---* problem_revision
problem 1---0..1 current_published_snapshot
published_snapshot 1---* learner_attempt
problem 1---* feedback_report
```

The diagram is conceptual. Physical table names and SQLAlchemy mappings must
preserve the same ownership and visibility boundaries (`R0-014`, analysis
sections 4, 8, and 9).

### 9.2 Table responsibilities and keys

| Table/concept | Identity and important columns | Constraints/indexes |
| --- | --- | --- |
| `vocabulary_record` | `(vocabulary_type, code)`, labels, aliases, status, explicit parent reference where applicable | Composite primary key; type-scoped code/label checks; parent foreign key; search indexes |
| `topic_parent_edge` or explicit topic parent field | Child `(vocabulary_type, code)` and parent identity | Same-vocabulary topic constraint; no self-edge; graph validation in domain; index by parent |
| `problem` | Stable problem ID, immutable public short identity, stable slug, current-public pointer | Unique slug/short ID; slug normalization; no draft-dependent slug lookup |
| `problem_revision` | Revision ID, problem ID, version, content, canonical metadata, editorial status, timestamps | Unique `(problem_id, version)`; optimistic version; status/index by problem |
| `revision_competency` | Revision ID, competency identity, primary/secondary role | One primary; max three secondary; composite uniqueness |
| `revision_topic` | Revision ID, topic identity, selection role/order | Composite uniqueness; canonical topic foreign reference |
| `prerequisite_reference` | Revision ID, relationship, target type/identity, minimum evidence | Typed target fields; no free-form target; duplicate prevention |
| `response_configuration` | Revision ID, task type, type-specific JSON/structured fields, resource limits | One per revision; policy validation; exact numeric fields |
| `scoring_component` | Response ID, method, decimal weight, order/configuration | At least one; decimal-safe total validated in domain and transaction boundary |
| `editorial_transition` | Revision ID, source/target, note, timestamp, operation ID | Append-only; valid transition checked in domain; indexes for history |
| `published_snapshot` | Snapshot ID, problem ID, revision ID, stable slug, published content, publication time | Immutable; one current eligible snapshot per problem; unique public slug |
| `learner_attempt` | Attempt ID, snapshot/problem identity, bounded request/result, idempotency key | Unique idempotency scope; no draft revision reference; retention policy deferred |
| `feedback_report` | Feedback ID, public problem identity, category/message, bounded abuse metadata | Size/category checks; rate/idempotency support; no account identity |
| `proposal` | Proposal ID, vocabulary context, bounded note, review state | Cannot satisfy canonical metadata; author-safe only |

PostgreSQL constraints protect composite identity, foreign-key existence,
uniqueness, nullability/cardinality where practical, and publication uniqueness.
Domain/application validation remains responsible for graph cycles, decimal
sum, policy, status transitions, response variants, and actionable errors
(`R0-013`, `R0-014`, `R0-015`, `AC-R0-015-07`).

### 9.3 Projection and indexing design

Public reads should use a dedicated published snapshot projection or repository
query that begins from `published_snapshot` eligibility. Author reads begin from
`problem_revision` and may join transition/validation context. No unconstrained
problem query is shared between them (`R0-014`, analysis section 9).

Expected indexes include:

- unique normalized stable slug and public short identity;
- published snapshot by stage, editorial order, publication time, and problem;
- revision by problem/status/version for Studio lists and optimistic saves;
- vocabulary by composite identity, type/parent, normalized labels, and aliases;
- revision topic/competency and prerequisite target for filtering/recommendation;
- bounded attempt/feedback lookup by public problem and idempotency scope.

The exact PostgreSQL text-search implementation is a design choice, but it must
search approved English/Vietnamese labels and aliases without exposing proposals
or unpublished content (`R0-011`, `AC-R0-011-07`).

### 9.4 Seed and migration ownership

Migrations own schema evolution; deterministic seeds own canonical vocabulary
and intentionally approved pilot fixtures. Seeds reference canonical codes and
must not fabricate parallel vocabulary values. A migration cannot rewrite an
already-shared revision; a new migration is required. Fixture snapshots must
include both published and draft cases for isolation tests, while public seed
queries return only published records (`R0-015`, `AC-R0-015-08`).

## 10. Transactions, concurrency, and migrations

### 10.1 Transaction policy

Release 0 uses PostgreSQL's default `READ COMMITTED` isolation with explicit
row locks and optimistic version checks where the workflow needs a stronger
decision. This is sufficient for the small editorial pilot while keeping
transaction behavior understandable; an ADR is required before changing the
isolation model (`R0-014`, `R0-015`, analysis sections 8-10).

| Operation | Transaction boundary | Concurrency control | Failure result |
| --- | --- | --- | --- |
| Vocabulary sync | Validate artifact before one synchronization transaction | Composite identity upsert/update; reject identity repurposing | Roll back all writes or return a structured rejected diff |
| Draft create | Problem identity and initial revision | Unique identity/slug constraints | No partial draft/public identity |
| Draft autosave | One versioned revision update | `expected_version` compare-and-increment | `REVISION_CONFLICT`; preserve newer server revision and local recovery copy |
| Submit/request changes/approve | Status check, transition insert, revision version update | Row lock on revision or compare-and-increment | No status/history mutation on invalid or stale request |
| Publish | Lock current problem/revision; validate; create immutable snapshot; append transition; update current-public pointer | Row lock plus unique slug constraint and idempotency key | Entire transaction rolls back; no partial public snapshot |
| Archive | Lock current public problem; append archive transition; remove public eligibility | Version check and unique current-public constraint | Existing public snapshot remains available if transaction fails |
| Learner submission | Resolve one published snapshot; insert bounded attempt/result | Scoped idempotency key; snapshot immutable | Replay original result or return safe dependency error |
| Feedback | Validate and insert one bounded report | Rate/idempotency policy | No partial/unbounded record |

The application use case owns the semantic transaction boundary; the adapter
opens, commits, rolls back, and closes the SQLAlchemy transaction. No endpoint
performs multiple independent repository calls and assumes atomicity
(`R0-014`, `AC-R0-014-05`, `AC-R0-015-09`).

### 10.2 Publication consistency

Publication locks the problem identity and target revision, rechecks current
status/version, validates current policy and slug uniqueness, creates the
snapshot, writes the transition note, and updates the current-public reference
before commit. Public readers either see the old complete snapshot or the new
complete snapshot; they never see an intermediate state. A public submission
resolves a snapshot identity at the start and assesses against that immutable
configuration (`R0-012`, `R0-014`, analysis sections 8-9).

Editing a published problem never updates the current snapshot. It creates a
new revision with its own version and status. A failed draft save, review
transition, or publication cannot change the prior public revision
(`AC-R0-014-09`, `AC-R0-014-10`, `AC-R0-014-16`).

### 10.3 Idempotency and retry design

Commands with externally visible effects accept a bounded idempotency key scoped
to operation and target identity. The idempotency record stores request digest,
status, and safe result reference. A matching replay returns the original result;
the same key with a different payload returns a stable conflict. Keys do not
contain answer data or secrets and their retention period is an open operations
choice that cannot allow duplicate publication or uncontrolled attempts
(`R0-012`, `R0-014`, analysis sections 6, 8, and 9).

### 10.4 Migration discipline

All schema changes use Alembic with descriptive revisions. Each migration:

1. Has deterministic upgrade behavior and a safe downgrade where supported.
2. Adds constraints/indexes in an order compatible with existing data.
3. Does not rewrite an already-shared migration.
4. Includes deterministic data changes when a data migration is unavoidable.
5. Is tested against PostgreSQL, not SQLite compatibility assumptions.
6. Keeps canonical vocabulary synchronization separate from schema migration
   unless a schema invariant requires both in a reviewed transaction.

Migration validation runs in CI and in the Compose startup procedure before the
API is marked ready. A failed migration leaves the database unavailable rather
than starting an API against a partially upgraded schema (`R0-015`,
`AC-R0-015-08`, `AC-R0-015-16`).

## 11. Public isolation, privacy, and error boundaries

### 11.1 Projection architecture

```text
Public HTTP route
      |
      v
Public application use case
      |
      v
PublishedProblemReader / public repository projection
      |
      v
published_snapshot eligibility predicate
      |
      v
safe public DTO

Author HTTP route
      |
      v
Author application use case
      |
      v
DraftRepository / EditorialRepository / PreviewProjector
      |
      v
author DTO (never passed to public path)
```

The published-only rule is encoded in the public reader port and adapter
implementation, not added as an optional caller filter. Public list, detail,
recommendation, submission, feedback, search index, build, and cache paths all
use that reader or a derived published-only projection. There is no generic
problem reader shared across public and author use cases (`R0-014`,
`AC-R0-014-12`, analysis section 9).

### 11.2 Public/author schema boundary

Public DTOs explicitly allow only learner fields: stable slug, published content,
canonical presentation labels, response schema, safe resources, public feedback
affordance, and recommendation data. Author DTOs may include revision IDs,
versions, editorial status, transition notes, validation errors/warnings,
translation-pending state, and preview context. Projection functions copy fields
explicitly; they do not serialize an ORM object or subclass an author schema
(`R0-013`, `R0-014`, `AC-R0-013-20`, `AC-R0-015-13`).

The public contract must reject or ignore attempts to provide revision IDs,
preview identifiers, author query flags, internal object keys, or unpublished
locale fields. A public not-found response does not reveal whether a draft or
archived record exists (`AC-R0-011-15`, `AC-R0-011-16`).

### 11.3 No-auth privacy controls

Release 0 has no identity or authentication layer. Design controls therefore
focus on minimizing and bounding data:

- Submission and feedback bodies have explicit size, category, and shape limits.
- Idempotency keys are bounded and do not include secrets or answer content.
- Logs contain request/operation IDs, safe event names, outcome, and duration,
  but redact answer data, notes, tokens, object keys, and direct identity claims.
- Public and author errors use stable categories and safe messages; stack traces,
  SQL, provider errors, local paths, and unpublished data stay server-side.
- Device-local progress is schema-validated and never trusted for authorization,
  publication, or canonical metadata (`R0-012`, `R0-015`,
  `AC-R0-012-11`, `AC-R0-015-12`, `AC-R0-015-13`).

Loopback Studio binding reduces accidental network exposure but is documented as
organizational only. A future access-control layer can attach to author routes
and use cases without changing the public isolation rule (`AC-R0-015-10`,
`AC-R0-015-11`).

### 11.4 Leak-path controls

| Leak path | Design control | Proof location |
| --- | --- | --- |
| Draft in public list/detail | Public reader starts from published snapshots; public DTO excludes revision fields | Repository and API contract tests |
| Draft in recommendation/search/build | Candidate/index/build interfaces accept only published projection | Recommendation, build, and E2E isolation tests |
| Preview reachable by public URL | Preview requires author command and explicit context; no public slug resolution | API and browser preview tests |
| Hidden answers/test data in feedback | Assessment result mapper exposes safe result DTO only | Assessment unit and submission contract tests |
| SQL/provider/object details in errors | Adapter exception mapper produces stable application error | FastAPI error contract tests |
| Anonymous storage abuse | Bounded payloads, rate/idempotency policy, safe rejection | API integration tests |
| Archived snapshot through stale cursor/cache | Public eligibility checked on each query/build and cache key includes public snapshot identity | PostgreSQL and E2E tests |

This matrix makes isolation a cross-layer acceptance property rather than a
single route implementation (`R0-014`, `R0-015`, analysis sections 9-10).

## 12. Learner frontend architecture

### 12.1 Routes and page responsibilities

| Route | Page responsibility | Data/state boundary |
| --- | --- | --- |
| `/problems` | Stage selector, recommendation, compact filters, topic shortcuts, results table/cards, learning-path support | Server-fetched public list; URL owns filters; browser-local adapter overlays status/evidence |
| `/problems/[slug]` | Published problem content, response area, hints/explanation, feedback, recommendation | Server-fetched current published snapshot; client owns response interaction and local progress |
| Public error/not-found states | Safe unavailable/retry/not-found presentation | No infrastructure details; no draft fallback |

The permanent slug is the public route identity. Return navigation preserves
filter query and list position through URL/history state rather than a server
session (`R0-011`, `AC-R0-011-09`, `AC-R0-011-15`, `AC-R0-011-16`).

### 12.2 Component and state ownership

```text
Learn app shell
  +- accessible header / language and feedback affordance
  +- ProblemsPage
      +- StageSelector
      +- RecommendationCard
      +- FilterBar + HierarchicalTopicPicker
      +- ActiveFilterTokens
      +- ProblemResultsTable (>= 768 px)
      +- ProblemResultCards (< 768 px)
      +- LearningPathSidebar
      +- Pagination / Empty / Loading / Error states

ProblemDetailPage
  +- ProblemContentBlocks
  +- Prerequisites
  +- ResponseForm(task-type discriminated)
  +- SubmissionFeedback
  +- ProblemFeedbackDialog
  +- ContinueRecommendation
```

Server components or route loaders own public data fetching and safe error
translation. Client components own URL filter interaction, response input,
focus, dialogs, local storage, submission pending state, and progress overlay.
No component fetches author data or imports Studio application code. Generated
API types flow through `packages/api-client`; shared UI primitives remain
presentation-only (`R0-011`, `R0-012`, `R0-015`, analysis sections 2, 6, and 9).

### 12.3 Discovery state

The URL query string is the source of truth for selected stage, search, canonical
filters, explicit descendant inclusion, sorting, pagination, and result position.
The page derives removable filter tokens from it and restores the state when a
learner returns from detail. The topic picker exposes family/intermediate/leaf
hierarchy and requires an explicit “Include subtopics” choice
(`AC-R0-011-06`, `AC-R0-011-08`, `AC-R0-011-09`).

The recommendation card is a single editorial candidate. Without local history
it says “Recommended start”; with local history it shows a safe reason based on
stage, prerequisites, and editorial path, without claiming personalization or
mastery (`AC-R0-012-15`, `AC-R0-012-16`).

### 12.4 Local progress adapter

The client-local adapter stores only approved anonymous progress fields:
schema version, stable public problem identity, task status, learning evidence
display data, recent completion context, timing/hint counters where approved,
and weekly-goal/path context if implemented. It validates and bounds reads,
handles missing/corrupt storage, and exposes an unavailable-storage state.

The adapter never stores or authorizes draft data, hidden answers, editorial
status, credentials, or an identity claim. Clearing or disabling storage leaves
public browsing and solving available and explains that progress is temporary
(`R0-012`, `AC-R0-012-09` through `AC-R0-012-11`).

### 12.5 Responsive and accessibility design

At widths below 768 px, results render as cards with all critical metadata
available without squeezing desktop columns. At desktop widths, the dense table
uses sticky headers and keeps stage/difficulty, status/evidence, competency,
topics, type, time, and compute scannable. Intermediate widths move or collapse
secondary information according to `ui_release_0.md` rather than silently
removing it (`R0-011`, `R0-015`, `AC-R0-011-12`, `AC-R0-011-13`).

Controls use visible labels, accessible names, keyboard-safe dialogs, focus
return, text/icon status cues, and non-color-only feedback. Loading preserves
layout dimensions; empty states identify active filters; public errors provide
retry and feedback paths without draft/infrastructure details
(`AC-R0-011-03`, `AC-R0-011-11`, `AC-R0-011-14`).

## 13. Studio frontend architecture

### 13.1 Routes and page responsibilities

| Route | Responsibility | State/projection |
| --- | --- | --- |
| `/author/problems` | Draft/revision list, editorial status, last save, resume/create actions | Author API only; never learner public list |
| `/author/problems/new` | Initialize a structured draft | Server draft identity plus local form state |
| `/author/problems/[id]` | Edit current revision and show autosave/validation state | Author revision contract and versioned local recovery |
| `/author/problems/[id]/preview` | Learner-shaped draft preview | Explicit author preview projection with persistent warning |
| `/author/review/[revision_id]` | Review, request changes, approve, publish, archive | Author/editorial command contracts and audit notes |

The final route composition may combine pages, but the Studio application owns
all author/reviewer navigation and uses distinct “IOAI Studio” identity. A
different port is not access control; the API and domain still validate every
command (`R0-013`, `R0-014`, `AC-R0-015-10`, `AC-R0-015-11`).

### 13.2 Editor section architecture

```text
StudioShell
  +- ProblemsList
  +- DraftEditor
      +- ContentSection: bilingual structured blocks
      +- ObjectiveEditor
      +- CurriculumMetadata: stage/difficulty/competency/topic pickers
      +- PrerequisiteEditor
      +- ResponseEditor: five task-type variants
      +- ScoringEditor: components + decimal-safe total
      +- ResourcesEditor: exact limits + policy warnings
      +- AutosaveStatus / RecoveryDialog
      +- ValidationPanel
      +- LearnerPreviewLink
  +- ReviewPanel
      +- TransitionHistory
      +- RequiredNoteField
      +- RequestChanges / Approve / Publish / Archive actions
```

Each section owns field-level presentation and accessible error linkage; the
draft form coordinator owns normalized state, dirty fields, version, autosave,
validation report, and explicit save/recovery decisions. Canonical pickers show
vocabulary type where codes/labels overlap and persist composite identities.
Response fields are discriminated by the selected task type and never expose
fields for unsupported types (`R0-013`, `AC-R0-013-07` through `AC-R0-013-14`).

### 13.3 Autosave and recovery UI

The top bar presents `Saving...`, `Saved`, or `Save failed` for the targeted
revision. The client coalesces idle edits, sends `expected_version`, and keeps a
schema-versioned local recovery copy on failure. A recovery dialog clearly
offers restore, discard, or resolve; it never silently overwrites server work or
deletes unsaved content (`AC-R0-013-15` through `AC-R0-013-18`).

Autosave is not a substitute for an explicit editorial action. Save, validate,
preview, submit for review, request changes, approve, publish, and archive use
separate buttons, confirmations, and API commands. Publication confirmation
shows the permanent URL and distinguishes it from preview (`R0-013`, `R0-014`,
`AC-R0-014-05`).

### 13.4 Validation, preview, and editorial states

Validation panel groups errors and warnings by Content, Curriculum, Assessment,
Resources, and Publication. Each item links to its field. Blocking errors
disable review/publication; warnings remain visible and explain their impact.
The preview uses learner page structure but carries a persistent
`Draft preview - not public` banner and author-visible pending-translation
warnings. Preview data cannot enter learner routes, search, recommendations,
builds, or caches (`AC-R0-013-19` through `AC-R0-013-21`).

Review controls render from the current editorial status and server version:

```text
DRAFT              -> Submit for review
IN_REVIEW          -> Request changes | Approve
CHANGES_REQUESTED  -> Edit and resubmit
APPROVED           -> Publish
PUBLISHED          -> Create revision | Archive
ARCHIVED           -> Start new valid revision flow
```

The UI disables impossible actions for orientation, but the API/domain remains
the authority. Every accepted transition requires a note and displays status
with text/icon cues rather than color alone (`R0-014`, `AC-R0-014-01` through
`AC-R0-014-16`).

### 13.5 Responsive and accessibility rules

Studio forms remain usable at the UI-specified mobile widths by grouping fields
into sections, avoiding squeezed multi-column tables, keeping error summaries
reachable, and making dialogs keyboard-safe. Focus moves to the first blocking
error after validation and returns to the invoking control after dialogs close.
Preview and learner/public surfaces remain visually distinguishable through
labels, banners, and structure, not color alone (`R0-013`, `R0-015`,
`AC-R0-011-14`, `AC-R0-013-20`).
