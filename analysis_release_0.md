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

## 6. Learner discovery and solving workflow

### 6.1 State and transition table

| State / step | Entry condition | Main behavior | Success output | Failure or retry behavior |
| --- | --- | --- | --- | --- |
| Library loading | Learner opens `/problems` or changes URL filters | Request published list with stage, search, taxonomy, sort, and pagination state | Skeleton retains layout; results contain public fields only | Retry action and safe feedback path; no infrastructure detail (`AC-R0-011-03`) |
| Library ready | Public list response succeeds | Show stage selector, recommendation, compact filters, result count, and dense table/cards | Learner can navigate or refine without losing URL state | No-result state identifies active filters and offers clear (`AC-R0-011-11`) |
| Stage/filtering | Learner changes a stage or filter | Normalize display input to canonical codes and update query string | Shareable URL reproduces the selected state; parent topics include descendants only explicitly | Invalid or unavailable values are rejected or disabled without broadening results (`AC-R0-011-06`, `AC-R0-011-08`, `AC-R0-011-09`) |
| Problem open | Learner selects a published row/card or direct slug | Resolve stable problem identity to current published snapshot | Learner sees objective, prerequisites, content blocks, response area, and recommendation context | Draft, unapproved, archived-only, or missing snapshot is not returned as public content (`AC-R0-011-15`, `AC-R0-011-16`) |
| Response entry | Published detail is ready | Render one of five accepted response forms and validate client-side hints without trusting them | Complete response can be submitted | Incomplete or malformed response remains editable and produces field guidance (`AC-R0-012-03`, `AC-R0-012-05`) |
| Submission pending | Valid response sent | Server validates published snapshot, response contract, limits, and idempotency context | Assessment result or explicit pending state | Retry is safe; duplicate request does not duplicate the logical attempt (`AC-R0-012-06`, `AC-R0-012-08`) |
| Feedback received | Assessment completes | Show safe outcome, score/rubric result, component feedback, and permitted explanation | Learner can understand next action; status may become attempted/completed according to policy | Hidden answers, test data, provider errors, and unpublished explanation remain private (`AC-R0-012-07`) |
| Local progress update | Open, attempt, completion, or evidence event occurs | Validate and persist approved device-local state if storage works | Refresh restores status, evidence display data, and recent context | Storage failure leaves product usable and explains non-persistence (`AC-R0-012-09` through `AC-R0-012-11`) |
| Feedback sent | Learner opens problem feedback | Validate category/message and apply anonymous abuse controls | Bounded feedback record associated with public problem | Safe validation or rate-limit result; no partial/unbounded record (`AC-R0-012-12` through `AC-R0-012-14`) |
| Continue | Learner completes or chooses recommendation | Select one editorially eligible next problem | Stable URL opens next published problem with stage context | Exclude current item where possible; never route to unavailable or private content (`AC-R0-012-15` through `AC-R0-012-17`) |

### 6.2 Response and scoring analysis

The public response contract is determined by the canonical task type in the
published snapshot. Release 0 supports `QUIZ_SINGLE`, `QUIZ_MULTIPLE`,
`NUMERIC_ANSWER`, `SHORT_ANSWER`, and `CODE_FUNCTION`; each must have an
explicit response schema and cannot be treated as generic free text. Resource
execution is limited to `NONE`, `BROWSER`, or `CPU_LIGHT` (`R0-012`, `R0-016`).

Assessment is a separate step from response validation. Validation answers
“can this response be assessed under the published contract?”; scoring answers
“what result follows from the configured components?”; feedback translates that
result into safe learner-facing guidance. A malformed response must not create a
completed task, and a delayed/manual assessment must not claim a result before
one exists (`AC-R0-012-05`, `AC-R0-012-08`).

Scoring components are decimal-safe and total exactly `1.0`. `EXACT_MATCH`,
`UNIT_TESTS`, and `PARTIAL_TESTS` support lightweight automated assessment;
`RUBRIC_HUMAN` supports manual review. Hidden answers, hidden test data, and
provider implementation details are assessment inputs, not public feedback
fields (`AC-R0-012-07`).

### 6.3 Recommendation analysis

Recommendation is editorially constrained rather than a claim of advanced
personalization. With no local history, the system returns the editorially
chosen first problem and labels it “Recommended start.” With local history, it
uses the selected stage, published eligibility, prerequisite relationships,
learning path order, and current problem exclusion where possible. It must not
infer mastery from task completion or expose a draft while finding a candidate
(`R0-011`, `R0-012`, `AC-R0-012-15` through `AC-R0-012-17`).

### 6.4 Client-state and failure conclusions

The URL is the shareable source of discovery filters; the server snapshot is the
source of public problem content; browser-local state is the source of
anonymous convenience progress. None may silently substitute for another.
This separation explains why a cleared local store affects recommendation
context but must not make a public URL invalid, and why a public-data failure
must not render cached draft-like content (`R0-011`, `R0-012`, `AC-R0-011-09`,
`AC-R0-012-11`).

## 7. Authoring workflow

### 7.1 Authoring state table

| State / step | Entry condition | Main behavior | Success output | Failure or recovery behavior |
| --- | --- | --- | --- | --- |
| Draft list | Author opens local Studio | List internal problem identities, revisions, editorial status, and last-save metadata | Author can resume or create a draft | Public learner routes never consume this list (`AC-R0-013-01`) |
| New draft | Author chooses create | Allocate problem and revision identities; initialize `DRAFT` | Structured editor opens without public snapshot | Initialization is atomic; no partial public identity is exposed (`AC-R0-013-02`) |
| Published revision edit | Published problem selected | Create a new draft revision under stable problem identity | Existing snapshot remains unchanged | Failed revision creation leaves current public snapshot intact (`AC-R0-013-03`) |
| Content editing | Draft exists | Edit bilingual learner blocks in reading order and observable objective | Structured content is locally editable and previewable | Missing translation is an author warning, not a public warning (`AC-R0-013-04`, `AC-R0-013-05`) |
| Metadata editing | Draft exists | Select canonical stage, difficulty, competencies, topics, prerequisites, modality, and resources | Composite vocabulary references and typed prerequisites are stored | Ambiguous, missing, invalid, or proposed values remain blocking/actionable (`AC-R0-013-07` through `AC-R0-013-11`) |
| Response/scoring editing | Task type selected | Render only fields for the selected accepted type; configure tests/tolerance/rubric and weights | Response contract is internally consistent and weights sum exactly `1.0` | Disallowed type, tier, resource, or malformed assessment blocks validation (`AC-R0-013-12` through `AC-R0-013-14`) |
| Autosave | Local draft changes become idle | Send a versioned draft save after the configured idle period | UI reports `Saving...` then `Saved` for the targeted revision | Server failure reports `Save failed` and keeps recoverable local copy (`AC-R0-013-15`, `AC-R0-013-16`) |
| Recovery | Local copy or stale version exists | Compare local/server revision and ask author to restore, discard, or resolve | Explicit author choice creates a new valid save | No silent overwrite or silent discard; stale write returns conflict (`AC-R0-013-17`, `AC-R0-013-18`) |
| Validation | Author requests validation or review | Check content, vocabulary, prerequisites, response, scoring, resources, and publication fields | Errors and warnings grouped by section and field | Blocking errors prevent review; warnings remain visible (`AC-R0-013-19`) |
| Learner preview | Draft is previewable | Render learner page with unsaved state and persistent warning | Author sees learner-format result and pending-translation warnings | Preview is not public, not indexed, and cannot be mistaken for publication (`AC-R0-013-20`, `AC-R0-013-21`) |

### 7.2 State ownership and save semantics

The editor owns transient form state. A draft revision store owns the last
server-accepted structured revision. A browser-local recovery copy owns only
unsynced author edits and must be explicitly restored or discarded. The server
revision version is the concurrency authority; a local copy cannot overwrite a
newer server revision by default (`R0-013`, `AC-R0-013-16` through
`AC-R0-013-18`).

Autosave is therefore a versioned write protocol, not a background mutation
that can be ignored. The minimum semantic sequence is:

1. Form changes mark the current revision dirty.
2. An idle timer coalesces changes and sends the revision version plus content.
3. Success advances the server version and clears the recoverable copy for the
   acknowledged fields.
4. Failure preserves the copy and exposes retry/recovery state.
5. A version conflict stops automatic overwrite and requests an explicit
   resolution.

The exact idle duration, local storage key format, and conflict merge UI are
Phase 3 design decisions. They cannot weaken recoverability, explicit choice,
or optimistic-concurrency behavior (`R0-013`, `R0-015`, `AC-R0-013-15` through
`AC-R0-013-18`).

### 7.3 Validation layering

Validation has three analytically distinct layers:

- Structural validation checks required fields, bilingual block shape, positive
  time, exact numeric resources, response-specific fields, and decimal-safe
  scoring totals.
- Canonical validation checks vocabulary identity, labels/aliases, topic
  parentage, prerequisites, modality exclusivity, and Release 0 availability.
- Publication validation checks unique stable slug, learner preview readiness,
  approval state, and absence of publication blockers.

The layers may run together in the UI, but each error must identify its source
field and stable error category. A valid structure is not sufficient for review;
an approved revision is not sufficient for publication unless the current
policy and snapshot checks also pass (`R0-013`, `R0-014`, `AC-R0-013-19`,
`AC-R0-014-05`, `AC-R0-014-07`).

### 7.4 Preview isolation conclusion

Preview needs a learner-shaped projection to reveal content and responsive
problems, but it must remain an author projection. It may include unsaved fields,
pending translation warnings, and draft-only validation context; public list,
detail, recommendation, search, build, and cache paths must never consume it.
This is a design constraint for the later public projection analysis and API
design (`R0-013`, `R0-014`, `AC-R0-013-20`, `AC-R0-013-21`).

## 8. Editorial transitions and publication

### 8.1 Transition table

| Source | Target | Allowed actor/context | Required evidence | Invalid or partial outcome |
| --- | --- | --- | --- | --- |
| `DRAFT` | `IN_REVIEW` | Author submits from local Studio | All blocking validation passes and author note is present | Keep `DRAFT`; return field-level blockers; record no transition (`AC-R0-014-01`, `AC-R0-014-02`) |
| `IN_REVIEW` | `CHANGES_REQUESTED` | Reviewer evaluates submitted revision | Reviewer note is present and identifies requested changes | Keep `IN_REVIEW`; no incomplete history entry (`AC-R0-014-03`, `AC-R0-014-16`) |
| `IN_REVIEW` | `APPROVED` | Reviewer evaluates submitted revision | Reviewer approval note and current validation result | Keep `IN_REVIEW` if invalid or note is missing (`AC-R0-014-04`, `AC-R0-014-16`) |
| `APPROVED` | `PUBLISHED` | Local Studio publication command | Current validation passes, stable slug is unique, approval exists, publication note/idempotency context is present | Publish neither snapshot nor transition if any check or transaction fails (`AC-R0-014-05`, `AC-R0-014-07`, `AC-R0-014-08`) |
| `PUBLISHED` | new draft revision | Author begins edit | Stable problem identity and new revision identity | Keep current snapshot unchanged if draft creation fails (`AC-R0-014-09`, `AC-R0-014-10`) |
| `PUBLISHED` | `ARCHIVED` | Reviewer archives with note | Required archival note and valid public-state transition | Keep public snapshot/state if validation or transaction fails (`AC-R0-014-14`) |
| `ARCHIVED` | new review/publish flow | New revision follows normal validation and approval | No silent reactivation; new publication is explicit | Preserve archived history and reject invalid shortcut (`AC-R0-014-15`) |

No other editorial states are inferred. Learner task status, learning evidence,
validation severity, and publication eligibility are separate dimensions and do
not create hidden workflow states (`R0-010`, `R0-014`, `AC-R0-014-16`).

### 8.2 Required transition record

Every accepted transition needs an immutable history record containing at least
source status, target status, revision identity, timestamp, actor context
available to the local workflow, and the required author/reviewer note. The
record is an audit explanation, not a substitute for an identity provider. A
publication record additionally identifies the resulting snapshot and stable
slug without exposing those internal records through public responses
(`R0-014`, `AC-R0-014-05`, `AC-R0-014-13`).

The transition validator must check the current persisted status, not a client's
claimed previous status. This prevents a stale Studio tab from applying a
transition against a newer revision. Missing notes, invalid source/target pairs,
stale versions, and unavailable policy values must fail before state mutation
(`AC-R0-014-07`, `AC-R0-014-16`).

### 8.3 Publication transaction and idempotency

Publication has two externally visible consequences: the revision becomes
published and a public snapshot becomes eligible. They must be committed as one
logical transaction. If snapshot creation, slug uniqueness, validation, or
history persistence fails, neither the public projection nor the successful
publication transition is visible (`R0-014`, `R0-015`, `AC-R0-014-05`,
`AC-R0-015-09`).

The same publication request may be retried because of a network timeout. An
idempotency key scoped to the revision and publication intent should return the
original result when the request already succeeded, rather than creating a
second snapshot or history event. A different revision or changed publication
intent requires a new reviewable request (`AC-R0-014-08`).

### 8.4 Stable URL and revision conclusions

The stable slug belongs to the problem identity, not an editable revision. A
published revision supplies the current snapshot contents at that slug. Editing
creates a private revision; publishing the new revision atomically replaces the
current public snapshot while preserving the URL. Archiving removes the problem
from public eligibility but preserves its internal history. A conflicting slug
must be rejected without affecting the existing problem (`R0-014`,
`AC-R0-014-09` through `AC-R0-014-15`).

These conclusions constrain repository transactions and API commands. The
specific database isolation level, locking strategy, and generated contract are
Phase 3 design decisions, not reasons to weaken public stability or auditability.

## 9. Data access and strict public isolation

### 9.1 Access-path matrix

| Access path | Consumer | Eligible source | Allowed data | Isolation requirement |
| --- | --- | --- | --- | --- |
| Public problem list/search | Learner UI and public API | Current published snapshots only | Public title, objective, stage/difficulty, approved metadata, type, time, compute, task status/evidence display context | Repository/API query must select published projection before filtering, sorting, or pagination (`AC-R0-011-01`, `AC-R0-014-12`) |
| Public problem detail | Learner UI and permanent URL | Snapshot addressed by stable problem identity/slug | Published learner content, response form, prerequisites, public recommendation context | Never resolve a draft or revision preview through the public slug (`AC-R0-011-15`, `AC-R0-011-16`) |
| Public submission | Learner UI/API | Current published response configuration | Bounded answer and safe result/feedback | Resolve against published snapshot; do not accept draft revision IDs or reveal hidden assessment data (`AC-R0-012-03`, `AC-R0-012-07`) |
| Public recommendation | Learner UI/API | Published eligible candidate set | One public problem and plain-language reason | Exclude drafts, unavailable values, and archived-only problems (`AC-R0-012-15` through `AC-R0-012-17`) |
| Public feedback | Learner UI/API | Published problem identity | Bounded category/message and moderation metadata | Do not expose author records, internal IDs, or unbounded anonymous data (`AC-R0-012-12` through `AC-R0-012-14`) |
| Author draft list/detail | Studio/API | Draft revisions and editorial history | Internal revision fields, validation state, notes, preview context | Must be routed through author-safe contracts and never reused as public projections (`AC-R0-013-01`, `AC-R0-013-20`) |
| Author preview | Studio/API | Current draft plus explicit unsaved state | Learner-shaped draft projection and author warnings | Requires explicit preview context; public build/search/cache must not consume it (`AC-R0-013-20`, `AC-R0-013-21`) |
| Author workflow command | Studio/API | Target revision with current version | Transition command, note, idempotency context | Domain validates current status, approval, policy, slug, and version before mutation (`AC-R0-014-01` through `AC-R0-014-08`) |
| Internal persistence and operations | Application/adapters | All authoritative records | Full domain state subject to operational controls | No SQL objects, provider errors, secrets, answer data, or object keys cross public error boundaries (`AC-R0-015-07`, `AC-R0-015-13`) |

### 9.2 Published-only enforcement point

Published-only eligibility must be enforced at the repository/application
projection boundary, before a caller can add a public filter, sort, search,
recommendation, or build query. An HTTP route check alone is insufficient:
another endpoint, background build, cache warmer, or future client could call a
broader repository method and leak a draft. Public response schemas must also
omit draft fields so a projection mistake cannot become an accidental contract
(`R0-011`, `R0-014`, `AC-R0-014-12`).

The author side may read richer revision and editorial records, but it should
request them through explicitly author-named use cases and response models.
Public and author query paths should not share an unconstrained “problem” read
that relies on callers to remember a status predicate (`R0-013`, `R0-015`).

### 9.3 Consistency and transaction analysis

Public detail and submission must resolve a consistent published snapshot. If a
new revision is being published concurrently, a request already resolved to a
snapshot should complete against that snapshot or return a documented conflict;
it must not mix content from two revisions. Publication, snapshot eligibility,
and transition history require one transaction boundary. Draft autosave and
editorial commands require revision-version checks. Feedback and attempts can
be separate bounded transactions, but must reference a public problem/snapshot
context and never mutate editorial state (`R0-012`, `R0-013`, `R0-014`,
`AC-R0-013-18`, `AC-R0-014-05`, `AC-R0-015-09`).

Idempotency applies to retriable commands with externally visible effects:
publication and learner submission at minimum. A duplicate submission may
return the original assessment result or an equivalent safe result, but must
not create uncontrolled attempts or alter a later published snapshot
(`AC-R0-012-06`, `AC-R0-014-08`).

### 9.4 Leak-path checklist

The following paths need explicit tests in later phases:

- list/search/filter queries that omit publication status;
- direct slug lookup that accepts revision or preview identifiers;
- recommendations built from all revisions instead of snapshots;
- learner submission errors containing answer keys, hidden tests, or draft
  explanations;
- generated OpenAPI schemas that include author-only fields;
- Next.js build-time data fetches using author repositories or draft fixtures;
- cache keys that do not distinguish public snapshot from preview;
- feedback or attempt responses that expose internal object keys or stack traces;
- archived records returned by a stale index or pagination cursor.

Each is a potential violation even if the normal learner route appears safe;
the analysis therefore treats public isolation as a cross-layer invariant rather
than a single endpoint feature (`R0-014`, `R0-015`, `AC-R0-015-13`).

## 10. Risk and verification analysis

### 10.1 Risk matrix

Risk levels reflect the harm of an undetected failure to the trustworthy
editorial loop, not implementation difficulty. High-risk items require a
behavior-focused failing test before implementation, followed by the smallest
test that proves the behavior at its owning boundary (`R0-015`,
`AC-R0-015-18`).

| Risk | Level | Failure consequence | First proof boundary | Requirement evidence |
| --- | --- | --- | --- | --- |
| Draft or unapproved revision appears in public list/detail/recommendation/build | Critical | Trust breach and incorrect learner content | Repository projection plus public API contract and E2E | `R0-014`, `AC-R0-014-12`, `AC-R0-015-13` |
| Published revision changes without a new approved snapshot | Critical | Shared permanent URL becomes untrustworthy | Domain/repository transaction test | `R0-014`, `AC-R0-014-09` through `AC-R0-014-12` |
| Invalid editorial transition, missing note, or partial publication succeeds | Critical | Unreviewed content becomes public or audit history is false | Pure workflow test plus PostgreSQL transaction test | `R0-014`, `AC-R0-014-01` through `AC-R0-014-08`, `AC-R0-015-09` |
| Vocabulary code, type, parentage, or alias is misinterpreted | High | Problems use wrong curriculum identity or ambiguous topics | Parser/graph/domain tests and deterministic drift check | `R0-010`, `R0-013`, `R0-015`, `AC-R0-013-08`, `AC-R0-015-19` |
| Release policy permits unsupported task/compute/scoring value | High | Unsupported workload or unsafe publication path | Availability policy unit test and publication integration test | `R0-012`, `R0-016`, `AC-R0-012-04`, `AC-R0-013-14` |
| Scoring weights or response validation are incorrect | High | Learner receives misleading assessment | Pure response/scoring tests and API contract test | `R0-012`, `AC-R0-012-05` through `AC-R0-012-08` |
| Autosave loses or overwrites author work | High | Content loss or silent revision corruption | State/use-case test with fake ports, then browser/component test | `R0-013`, `AC-R0-013-15` through `AC-R0-013-18` |
| Stable slug or revision consistency fails under concurrency | High | Shared links break or show mixed content | PostgreSQL repository/concurrency test | `R0-014`, `AC-R0-014-09` through `AC-R0-014-12` |
| Anonymous feedback or submission endpoint is abused | High | Noise, storage exhaustion, or unsafe responses | API boundary and rate/size-limit tests | `R0-012`, `R0-015`, `AC-R0-012-13`, `AC-R0-015-12` |
| No-auth boundary leaks author commands or sensitive errors | High | Unauthenticated users mutate or inspect private data | Public/author contract tests and security-focused E2E | `R0-015`, `AC-R0-015-10` through `AC-R0-015-13` |
| Local progress is treated as authoritative or fails silently | Medium | Misleading status/recommendation or broken anonymous loop | Browser storage adapter and component tests | `R0-012`, `AC-R0-012-09` through `AC-R0-012-11` |
| Responsive or accessibility behavior hides status or blocks a workflow | High | Learners cannot discover or solve reliably | Testing Library/accessibility checks and Playwright widths | `R0-011`, `R0-015`, `AC-R0-011-12` through `AC-R0-011-14` |
| Migration, backup, readiness, or deterministic build procedure fails | High | Data loss or unreproducible delivery | PostgreSQL/Alembic and operations smoke tests | `R0-015`, `AC-R0-015-08`, `AC-R0-015-14` through `AC-R0-015-19` |

### 10.2 Test-boundary strategy

| Boundary | Owns proof of | Required approach |
| --- | --- | --- |
| Pure domain unit | Identity, cardinality, status transitions, scoring totals, availability, stable slug rules, and typed references | Real domain objects, deterministic clocks/IDs, failing regression first; no framework imports |
| Application/use-case unit | Workflow orchestration, ports, idempotency, transaction intent, safe errors, autosave recovery, recommendations | Fakes at narrow ports; assert calls and state outcomes rather than mocking domain behavior |
| Vocabulary/import tests | Parser determinism, bilingual records, aliases, explicit parent graph, drift | Golden structured artifact plus invalid fixtures for missing parents, cycles, duplicates, and identity collisions |
| PostgreSQL/Alembic integration | Constraints, composite keys, transaction rollback, revision/snapshot isolation, concurrency, migration safety | Real PostgreSQL; deterministic fixtures; upgrade/downgrade checks where safe |
| FastAPI contract tests | Public/author route separation, schemas, pagination/filter errors, request IDs, safe error mapping, OpenAPI | Generated/derived contract checked against server; no ORM objects or draft fields in public responses |
| Frontend unit/component | URL filters, hierarchy picker, status/evidence separation, responsive table/cards, validation, autosave state, preview warning, local storage failures | Accessible role/name queries with Testing Library and Vitest |
| Playwright critical flows | Learner browse -> open -> submit -> feedback -> continue; author draft -> validate -> preview -> review -> publish -> public verify | Focused desktop/mobile workflows, with draft/public isolation assertions |
| Operations checks | Compose health, loopback Studio binding, migrations, backup/restore, deterministic build and lockfiles | Isolated CI/local profile with documented prerequisites and safe fixtures |

### 10.3 Red-green-refactor implications

For each behavior-bearing implementation step, the relevant smallest test is
written first and run to observe the expected failure. Implementation then
passes that test before refactoring and expanding integration coverage. A
documentation analysis can specify this gate but cannot claim that a runtime
behavior is implemented merely because the requirement is listed (`R0-015`,
`AC-R0-015-18`).

The highest-priority initial tests are public/draft isolation, valid editorial
transitions and atomic publication, vocabulary graph validation, scoring-total
validation, and stable slug behavior. These tests protect the core trust loop
before UI breadth or optional operational polish (`R0-014`, `R0-015`).

## 11. Analysis baseline and open decisions

### 11.1 Requirement-to-analysis matrix

| Requirement group | Analysis evidence | Proof still deferred |
| --- | --- | --- |
| R0-010 goals, personas, assumptions, terminology, scope | Sections 1-3 define actors, boundaries, and excluded context | Phase 3 context/container design may refine deployment details |
| R0-011 learner discovery | Sections 6 and 9 analyze discovery states, public projections, URLs, filters, responsive/accessibility risks, and isolation | Phase 3 API/UI design and Phase 4/7 implementation tests |
| R0-012 learner solving loop | Sections 4, 6, and 9 analyze responses, scoring, attempts, progress, feedback, and recommendations | Phase 3 contracts and Phase 7 scoring/progress/feedback tests |
| R0-013 authoring | Sections 4 and 7 analyze aggregate structure, metadata, prerequisites, response/scoring configuration, autosave, recovery, validation, and preview | Phase 3 use-case/API design and Phase 6 authoring tests |
| R0-014 editorial publication | Sections 4, 8, and 9 analyze lifecycle, audit notes, atomic publication, revisions, slugs, and public isolation | Phase 3 persistence/API design and Phase 6/7 workflow tests |
| R0-015 quality and operations | Sections 3, 9, and 10 analyze trust, integrity, privacy, test boundaries, and operational risks | Phase 3 operations design and Phase 4/7 quality gates |
| R0-016 requirements governance | This matrix plus sections 11.2-11.4 preserve scope, decisions, and downstream traceability | Future design decisions must cite this analysis and requirements IDs |

Acceptance-criteria coverage is intentionally grouped by behavior boundary. The
analysis maps `AC-R0-011-01` through `AC-R0-011-16` to sections 6 and 9;
`AC-R0-012-01` through `AC-R0-012-17` to sections 4, 6, and 9;
`AC-R0-013-01` through `AC-R0-013-21` to sections 4, 7, and 9;
`AC-R0-014-01` through `AC-R0-014-16` to sections 4, 8, and 9; and
`AC-R0-015-01` through `AC-R0-015-19` to sections 3, 9, and 10. Criteria that
require runtime proof remain explicitly deferred rather than implied to pass by
this document (`R0-016`, `AC-R0-015-18`).

### 11.2 Deferred implementation decisions

The following choices remain open for Phase 3/4 design and must be resolved by
an ADR or a design section before implementation depends on them:

- PostgreSQL isolation level, locking/version strategy, and exact transaction
  boundaries for publication, submissions, and autosave.
- Exact browser-version support window and performance measurement environment.
- Backup provider, retention period, restore target, and rehearsal schedule.
- Structured-log sink, retention, redaction policy, and request-ID propagation
  across services.
- OpenAPI-to-TypeScript generation command, artifact ownership, and drift-check
  execution point.
- Local-progress schema versioning, corruption recovery, and recommendation
  storage limits.
- Anonymous submission/feedback idempotency-key lifetime and rate/size limits.
- The concrete local operator model for author/reviewer actions while accounts
  remain out of scope.

These are not permission to add authentication, hosted execution, analytics,
semantic retrieval, or other deferred features. They are implementation choices
needed to satisfy the already accepted requirements (`R0-015`, section 15.3 of
`requirement_release_0.md`).

### 11.3 Analysis conclusions and non-conclusions

The analysis establishes that public-only projections, stable problem identity,
immutable published snapshots, explicit vocabulary identity, bounded anonymous
state, and separate workflow dimensions are cross-layer invariants. It does not
choose ORM mappings, endpoint names, UI component boundaries, database schema
names, cloud services, or authentication mechanisms. Those choices belong to
Phase 3 and must remain traceable to this analysis and the requirements baseline.

### 11.4 Baseline decision

No additional Release 0 capability is inferred. The narrower five-type response
policy from the Release 0 UI remains authoritative over the later master-plan
list; GPU/distributed work, accounts, cross-device progress, and other deferred
features remain excluded. Future analysis changes must update this matrix and
the decision index in the same commit as the changed conclusion (`R0-016`).
