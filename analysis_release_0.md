# Release 0 Analysis

Status: In progress. This document analyzes the accepted requirements in
`requirement_release_0.md`; it is not a replacement for the requirements or
the governing product, UI, vocabulary, and code-standard documents.

## Analysis rules

- Every conclusion cites one or more requirement IDs. Behavioral conclusions
  cite the relevant `AC-R0-*` criterion where available.
- Release 0 scope is limited to the five approved task types and
  `NONE`/`BROWSER`/`CPU_LIGHT` compute tiers defined in requirements section
  15.2.
- Exclusions and deferred decisions in requirements section 15.3 are not
  treated as hidden capabilities.
- Terms such as stage, competency, topic, prerequisite, task status, learning
  evidence, editorial status, revision, and published snapshot retain the
  meanings defined by the requirements and `vocab.md`.

## 1. Actors and responsibilities

### 1.1 Actor table

| Actor | Goal | Responsibilities in Release 0 | Trigger / output | Failure expectation |
| --- | --- | --- | --- | --- |
| Learner | Find, solve, and continue through reviewed problems | Select a stage; search and filter published problems; open permanent URLs; submit supported responses; read feedback; provide problem feedback; maintain best-effort local progress | Opens `/problems` or a permanent problem URL; receives public content, submission feedback, and one next recommendation | Can continue browsing when local storage, scoring, or public data is unavailable; receives safe actionable errors without draft or infrastructure details (`R0-011`, `R0-012`, `AC-R0-011-03`, `AC-R0-012-11`) |
| Author | Produce valid, reviewable learning content | Create and revise structured drafts; select canonical metadata; configure prerequisites, response, scoring, and resources; autosave; validate; preview; submit for review | Uses `/author/problems`; produces a draft revision or review request | Keeps recoverable local work on save failure; cannot submit invalid or unavailable content (`R0-013`, `AC-R0-013-16`, `AC-R0-013-19`) |
| Reviewer | Decide whether a revision is ready for publication | Inspect submitted content; request changes or approve; enter required notes; publish approved revisions; archive public problems | Performs an editorial transition and leaves an auditable history entry | Invalid transitions, missing notes, stale revisions, and failed publication change no state and expose safe errors (`R0-014`, `AC-R0-014-03`, `AC-R0-014-16`) |
| Curriculum owner | Keep curriculum vocabulary and availability trustworthy | Govern canonical vocabulary; review missing-value proposals; maintain Release 0 availability policy | Approves or rejects canonical value proposals outside the problem editor | Proposed or future values cannot become publishable metadata without canonical approval (`R0-010`, `R0-013`, `AC-R0-013-10`) |
| Local operator | Run the local pilot safely | Start the learner, Studio, API, and database services; follow documented migration, backup, restore, and health procedures | Starts or diagnoses the development stack | Studio defaults to loopback; health and readiness distinguish process and dependency failures; no-auth exposure is not treated as authorization (`R0-015`, `AC-R0-015-11`, `AC-R0-015-16`) |

### 1.2 Responsibility boundaries

The learner owns only interaction with public projections and best-effort
browser-local progress. The learner does not select or mutate editorial state,
canonical vocabulary, revisions, or publication snapshots (`R0-011`, `R0-012`,
`AC-R0-012-09`, `AC-R0-012-10`).

The author owns draft content and revision intent but cannot bypass validation,
canonical metadata rules, review, or approval. Preview is an author-facing view
of unsaved or unpublished state and is not a public projection (`R0-013`,
`AC-R0-013-19` through `AC-R0-013-21`).

The reviewer owns editorial decisions, not vocabulary semantics. The curriculum
owner governs canonical values, while the reviewer decides whether a particular
problem revision satisfies the approved content and publication rules (`R0-013`,
`R0-014`).

The local operator can run services but is not an identity provider. A separate
Studio port or loopback binding organizes the pilot and reduces accidental
exposure; it does not establish production authorization (`R0-010`,
`R0-015`, `AC-R0-015-10`, `AC-R0-015-11`).

### 1.3 Actor interaction summary

```text
Curriculum owner
        | approves canonical values and Release 0 availability
        v
Author ---> Draft / revision ---> Reviewer ---> Approved ---> Publisher
  |              |                    |                         |
  |              +-- learner preview  +-- notes/history          |
  |                                                            v
  +---------------------------------------------------- Published snapshot
                                                               |
Local operator ---> services and operations          Learner ---> public loop
                                                               |
                                        local progress <--------+
```

The diagram represents responsibility and data flow, not authentication. The
exact service and persistence boundaries are analyzed in R0-021 and R0-027
before design work begins (`R0-015`, `AC-R0-015-10`).

## 2. Traceability status

The remaining sections are added by the subsequent Phase 2 commits in
`plan_release_0.md`. R0-020 establishes the actor vocabulary used by those
sections.

## 3. Context and trust boundaries

### 3.1 Release 0 context

```text
 Anonymous learner browser                         Local author browser
         |                                                   |
         | public reads, submissions, feedback               | Studio commands,
         |                                                   | preview, review
         v                                                   v
  Learner Next.js :3000                            Studio Next.js :3001
         |                                                   |
         +---------------------- HTTP -----------------------+
                                |
                         FastAPI :8000
                         /     |       \
                        /      |        \
                 public API  author API  health/ops
                        \      |        /
                         \     |       /
                          PostgreSQL
                    system of record

  Learner browser local storage
  (anonymous progress only; not authoritative)
```

The learner app, Studio, and FastAPI are separate runtime surfaces with
merge-safe routes. PostgreSQL is authoritative for vocabulary, revisions,
snapshots, workflow history, attempts, and feedback. Browser-local storage is
authoritative only for the learner's best-effort local progress view and must
not be treated as an account, publication record, or server-side identity
(`R0-010`, `R0-012`, `R0-015`, `AC-R0-012-09`, `AC-R0-012-10`).

Release 0 has no accepted upload, extraction, model-provider, embedding, or
asynchronous judging context. Redis, Celery, Docling, MinIO, GPU services, and
external identity providers remain outside the context until a new accepted
requirement creates a concrete use case (`R0-010`, section 15.3 of
`requirement_release_0.md`).

### 3.2 Trust-boundary table

| Boundary | What crosses it | Trust assumption | Required control |
| --- | --- | --- | --- |
| Learner browser -> public learner app/API | Search, filters, public reads, submissions, feedback | Input is untrusted and anonymous; client state can be modified | Validate all input at the API/domain boundary; return only public projections and safe error contracts (`R0-011`, `R0-012`, `R0-015`) |
| Author browser -> Studio/API | Draft commands, preview requests, review/publication commands | Local pilot operator is trusted by deployment context, but request data is still untrusted | Validate commands, enforce workflow and policy rules server-side, use bounded fields and optimistic version checks; port separation is not authorization (`AC-R0-013-18`, `AC-R0-015-10`, `AC-R0-015-11`) |
| Public API -> PostgreSQL | Published reads and learner records | Database is authoritative but query paths may be accidentally over-broad | Separate public projections from author queries; enforce published-only eligibility at repository/API boundaries; use transaction boundaries and constraints (`R0-014`, `AC-R0-014-12`, `AC-R0-015-07`) |
| Studio/API -> PostgreSQL | Drafts, revisions, metadata, workflow history, publication | Persistence must not infer authorization from a port or route | Validate state transitions and notes; atomically publish snapshots; prevent stale writes and partial transitions (`R0-013`, `R0-014`, `AC-R0-013-18`, `AC-R0-014-05`, `AC-R0-014-16`) |
| Browser local storage -> learner UI | Status, evidence display data, history, recovery context | Storage may be absent, corrupted, stale, or intentionally modified | Treat it as untrusted cache-like state; validate schema, handle failure, never use it to authorize or expose private records (`R0-012`, `AC-R0-012-11`) |
| Local operator -> development stack | Process startup, migrations, backups, health checks | Operator has filesystem/process access to the pilot environment | Document loopback Studio binding, secrets handling, deterministic commands, readiness, backup/restore, and the limit of no-auth operation (`R0-015`) |

### 3.3 No-auth threat analysis

The absence of authentication changes the threat model but does not remove the
need for authorization-shaped boundaries. The highest risks are an external
client invoking author commands, a learner query returning drafts, a malformed
submission causing unsafe scoring behavior, anonymous feedback abuse, and
leakage through error messages. The requirements therefore imply these
separations even before an identity system exists:

1. Public read and submission contracts must be distinct from author commands.
2. Author routes must not rely on the Studio port as a security check.
3. Publication eligibility and published-only projections must be enforced below
   HTTP routing so alternate query paths cannot bypass them.
4. Feedback, progress, and submission inputs must be bounded and safe to log.
5. Errors must expose stable codes and actionable messages, not stack traces,
   SQL, provider errors, object keys, answers, or unpublished content.

These are analysis conclusions, not an authorization implementation. Their
concrete ports, API contracts, and persistence mechanisms belong to Phase 3
design (`R0-015`, `AC-R0-015-10` through `AC-R0-015-13`).

## 4. Domain model

### 4.1 Concept table

| Concept | Meaning and ownership | Key relationships | Requirement evidence |
| --- | --- | --- | --- |
| Problem | Stable curriculum identity and permanent slug shared by revisions | Has one or more revisions; may have one current published snapshot | `R0-011`, `R0-013`, `R0-014`, `AC-R0-011-15`, `AC-R0-014-09` |
| Problem revision | Editable version of problem content, metadata, response, resources, and scoring | Belongs to one problem; has editorial status and transition history; can produce one snapshot | `R0-013`, `R0-014`, `AC-R0-013-03`, `AC-R0-014-10` |
| Published snapshot | Immutable public projection of an approved revision | Belongs to a problem and publication event; is the only public problem source | `R0-011`, `R0-014`, `AC-R0-014-05`, `AC-R0-014-12` |
| Vocabulary record | Canonical typed value with `(vocabulary_type, code)`, bilingual labels, aliases, and policy status | Topic records may have an explicit parent; problem metadata references canonical records | `R0-010`, `R0-013`, `R0-015`, `AC-R0-013-07` through `AC-R0-013-10` |
| Prerequisite | Typed relationship to competency, topic, task, or learning unit | May carry relationship and minimum evidence; is not a free-form tag | `R0-013`, `AC-R0-013-11` |
| Response configuration | Type-specific contract for the learner answer | Belongs to one revision; selects one of the five Release 0 task types | `R0-012`, `R0-013`, `AC-R0-012-03`, `AC-R0-013-12` |
| Scoring component | Weighted assessment rule, automated or human | Belongs to response configuration; decimal-safe weights total `1.0` | `R0-012`, `R0-013`, `AC-R0-012-07`, `AC-R0-013-13` |
| Editorial transition | Immutable record of a status change, timestamp, and required note | Belongs to a revision; only valid source/target transitions are allowed | `R0-014`, `AC-R0-014-01` through `AC-R0-014-04`, `AC-R0-014-13` |
| Learner attempt | Server-side bounded record of a submission and assessment outcome | References a published problem/snapshot and response result; does not identify an account | `R0-012`, `R0-015`, `AC-R0-012-06`, `AC-R0-015-12` |
| Local progress | Device-local learner view of status, evidence display data, recent history, and timing/hint context | References stable public problem identity; never grants access or changes publication | `R0-012`, `AC-R0-012-09` through `AC-R0-012-11` |
| Recommendation | One editorially eligible next problem and plain-language reason | Depends on selected stage, published availability, prerequisites, and local history | `R0-011`, `R0-012`, `AC-R0-012-15` through `AC-R0-012-17` |
| Feedback | Bounded anonymous report attached to a published problem | Has category, message, safe problem reference, and abuse-control metadata | `R0-012`, `R0-015`, `AC-R0-012-12` through `AC-R0-012-14` |
| Audit note | Required human-entered explanation on editorial action | Stored with transition or publication action; not exposed in public projections | `R0-014`, `AC-R0-014-05`, `AC-R0-014-13` |

### 4.2 Problem and revision aggregate

The problem identity is stable across revisions. Content, canonical metadata,
prerequisites, response configuration, scoring, and resources belong to a
revision because a change to any of them must be reviewable and must not alter
the current public snapshot before publication. The stable slug belongs to the
problem identity and is unique among public identities; a later revision cannot
silently change the URL (`R0-011`, `R0-013`, `R0-014`).

The aggregate must enforce these cardinalities and invariants before persistence:

- exactly one stage, primary competency, difficulty, and task type;
- zero through three secondary competencies;
- valid canonical topic references and typed prerequisites;
- positive `expected_minutes` and exact numeric resource limits;
- `NONE` data modality alone, or one or more actual modalities;
- one accepted Release 0 response configuration;
- one or more scoring components whose decimal-safe weights total exactly `1.0`;
- observable learning objective and required structured learner content;
- task type and compute tier permitted by Release 0 availability policy.

The aggregate does not decide whether a revision is public merely because its
fields are valid. Editorial status and publication state remain separate so a
valid draft can stay private, a reviewed revision can await publication, and a
published snapshot can remain immutable while a new draft revision is edited
(`R0-013`, `R0-014`, `AC-R0-013-19`, `AC-R0-014-06`).

### 4.3 State dimensions

| Dimension | Values | Meaning | Must not be conflated with |
| --- | --- | --- | --- |
| Learner task status | `NOT_STARTED`, `ATTEMPTED`, `COMPLETED` | Device-local interaction progress, optionally supported by a server attempt | Learning evidence or editorial status |
| Learning evidence | `INTRODUCED`, `PRACTICED`, `APPLIED`, `PROFICIENT` | Accumulated evidence shown separately from completion | `MASTERED`, task status, or publication |
| Editorial status | `DRAFT`, `IN_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`, `PUBLISHED`, `ARCHIVED` | Revision workflow state | Learner status or validation result |
| Publication state | No snapshot, current published snapshot, archived/no public snapshot | Whether a public projection is eligible | Draft validity or approval alone |

The separate dimensions prevent a completed learner task from being interpreted
as mastery, an approved revision from being interpreted as public, or an
attempt from being interpreted as editorial evidence (`R0-010`, `R0-012`,
`R0-014`, `AC-R0-012-09`, `AC-R0-014-05`).

### 4.4 Lifecycle and ownership conclusions

1. A draft revision is created under a stable problem identity and remains
   private until the valid editorial workflow publishes it.
2. Publishing creates an immutable snapshot in the same logical transaction as
   the successful publication transition, or neither is visible.
3. Editing a published problem creates a new revision. The old snapshot remains
   the public source until the new revision is approved and published.
4. Attempts and feedback reference public problem identity or snapshot context,
   not draft revision IDs. This avoids exposing author internals through learner
   records.
5. Local progress may point to a stable problem identity but is never a source
   of authorization, curriculum metadata, or publication state.

These are domain ownership conclusions; database keys, ORM mappings, and
transaction implementation are deferred to Phase 3 design (`R0-014`,
`R0-015`, `AC-R0-014-09` through `AC-R0-014-12`).

## 5. Vocabulary ingestion and governance

### 5.1 Deterministic data flow

`vocab.md` is the sole human-maintained canonical source. The analysis implies
this repeatable pipeline:

```text
vocab.md
   |
   v  parse declared sections and table rows
raw vocabulary records
   |
   v  normalize codes, labels, aliases, parents, and statuses
validated structured representation
   |
   +--> checked-in/generated artifact used by runtime and fixtures
   |
   +--> deterministic drift check against vocab.md
   |
   +--> synchronization input for PostgreSQL vocabulary records
```

The parser may recognize the documented table structure, but Markdown heading
position is presentation and cannot establish parentage. Every non-root topic
must carry an explicit `parent_code`; a missing explicit relationship is an
error rather than an inferred relationship (`R0-010`, `R0-013`, `R0-015`,
`AC-R0-013-07`, `AC-R0-013-09`).

The structured representation must retain vocabulary type, code, nested
English/Vietnamese labels, approved aliases, explicit parent code, canonical
status, and any fields needed by the availability policy. Runtime code consumes
this validated representation rather than maintaining parallel hand-coded enum
or label lists (`R0-010`, `R0-011`, `R0-013`, `AC-R0-011-07`,
`AC-R0-013-08`).

### 5.2 Identity and graph validation

Canonical identity is the composite `(vocabulary_type, code)`. A competency and
topic may share a code or label without being the same record. Therefore:

- uniqueness is checked within composite identity, not code globally;
- references carry vocabulary type as well as code;
- duplicate canonical labels and aliases are rejected within a parent branch
  when they would make selection ambiguous;
- every non-root topic resolves to an existing parent of the topic vocabulary;
- self-parenting is rejected;
- cycles are rejected by graph traversal;
- orphaned records and unresolved references fail validation before publication;
- parent and descendant selection remains explicit rather than implicitly
  including all descendants.

These checks protect both author metadata selection and learner hierarchical
search. They must produce actionable validation errors while preserving future
canonical values that are valid but unavailable to Release 0 (`R0-011`,
`R0-013`, `AC-R0-011-08`, `AC-R0-013-07` through `AC-R0-013-10`).

### 5.3 Bilingual search and canonical selection

Search indexes or in-memory lookup structures may include English labels,
Vietnamese labels, and approved aliases. They are presentation/search inputs,
not persisted task selections. A selected competency, topic, stage, task type,
compute tier, scoring method, modality, or prerequisite target persists its
canonical code with vocabulary type (`R0-011`, `R0-013`, `AC-R0-011-07`,
`AC-R0-013-08`, `AC-R0-013-11`).

If a record is missing or ambiguous, the author can submit a proposal note. The
proposal is a separate review object and cannot be substituted into a problem
revision as if it were canonical. This preserves the curriculum-owner boundary
and prevents an unapproved value from entering a published snapshot
(`R0-010`, `R0-013`, `AC-R0-013-10`).

### 5.4 Release 0 availability policy

Canonical completeness and release availability are separate decisions. The
canonical representation retains future-facing values, while a central policy
determines whether an author may publish them in Release 0.

The approved Release 0 set is:

| Policy dimension | Enabled values |
| --- | --- |
| Task type | `QUIZ_SINGLE`, `QUIZ_MULTIPLE`, `NUMERIC_ANSWER`, `SHORT_ANSWER`, `CODE_FUNCTION` |
| Compute tier | `NONE`, `BROWSER`, `CPU_LIGHT` |
| Scoring method | `EXACT_MATCH`, `UNIT_TESTS`, `PARTIAL_TESTS`, `RUBRIC_HUMAN` when appropriate to the response |
| Data modality | `NONE`, or an actual modality when the task has an approved dataset; `NONE` is mutually exclusive with actual modalities |

GPU, distributed, higher CPU, ranking-based, hidden-label, and otherwise
unsupported capabilities remain canonical-but-unavailable and must be blocked
at validation and publication, not deleted from vocabulary data (`R0-012`,
`R0-013`, `R0-016`, `AC-R0-012-04`, `AC-R0-013-14`).

### 5.5 Drift detection and synchronization

Drift is any difference between the canonical source and the structured
representation that changes identity, labels, aliases, parentage, status, or
policy-relevant values. The deterministic drift check should:

1. Parse `vocab.md` using the same normalization rules as generation.
2. Generate the structured representation in a stable ordering.
3. Compare it with the committed artifact or expected generated output.
4. Fail with a field-level diff when records are missing, added, or changed.
5. Run graph, uniqueness, bilingual-label, and availability validations before
   synchronization to PostgreSQL.

Database synchronization must be idempotent and must not repurpose an existing
composite identity. A changed label or alias is a content update; a changed
vocabulary type or code is a new identity requiring explicit migration or
review, not an in-place reinterpretation (`R0-015`, `AC-R0-015-07`,
`AC-R0-015-19`).
