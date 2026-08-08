# Release 0 Requirements

Status: Working baseline. Phase 1 stories are added and reviewed in the
commit sequence defined by `plan_release_0.md`.

## 1. Purpose and goals

Release 0 is a complete editorial pilot for a small, trustworthy AI learning
problem library. It supports this loop:

1. An author creates and validates a structured problem.
2. A reviewer checks the content and requests changes or approves it.
3. An authorized local Studio workflow publishes an approved snapshot.
4. A learner discovers a published problem, submits a lightweight response,
   receives feedback, and continues to an editorially recommended next problem.

The release optimizes for reviewed content and a dependable draft-to-public
workflow. It does not optimize for competition infrastructure, advanced
judging, or broad learning-platform features.

## 2. Personas and responsibilities

### Learner

An anonymous visitor who browses only published problems, chooses a pathway
stage, opens permanent problem URLs, submits supported responses, reads
feedback, and optionally keeps progress on the current device.

### Author

A content creator who uses the local Studio to draft and revise structured
problems, select canonical metadata, validate content, autosave work, and
preview the learner experience.

### Reviewer

An editorial participant who evaluates a submitted draft, records a required
note, requests changes or approves the revision, and preserves an auditable
workflow history.

### Curriculum owner

The owner of canonical vocabulary and Release 0 availability policy. This role
governs vocabulary changes and can review proposals for values that are
canonical but not publishable in Release 0.

## 3. Assumptions

- Release 0 has no accounts or authentication. The separation between the
  public learner app and local Studio is organizational and network-scoped,
  not an authorization boundary.
- PostgreSQL is the system of record for vocabulary, problems, revisions,
  publication snapshots, workflow history, attempts, progress, and feedback.
- Public reads and builds can return published snapshots only.
- The canonical controlled vocabulary is derived from `vocab.md`; persisted
  selections use canonical composite identity `(vocabulary_type, code)`.
- English is the default content and interface language. Vietnamese labels and
  approved aliases are available where the governing UI and vocabulary require
  them.
- Anonymous learner progress is device-local and best-effort. The product
  remains usable when local storage is unavailable or cleared.
- Release 0 content is primarily AI Foundations, with Competition Foundations
  available where approved content requires it. Later stages may be visible as
  disabled options but are not publishable accidentally.

## 4. Terminology

- **Stage:** the learner's position in the pathway.
- **Competency:** an observable assessable ability; a problem has one primary
  competency and up to three secondary competencies.
- **Topic:** a concept, method, tool, or technique in the canonical hierarchy.
- **Prerequisite:** a typed reference to a competency, topic, task, or learning
  unit; it is not a free-form tag.
- **Difficulty:** challenge relative to a stage and always presented with it.
- **Task status:** `NOT_STARTED`, `ATTEMPTED`, or `COMPLETED`.
- **Learning evidence:** `INTRODUCED`, `PRACTICED`, `APPLIED`, or `PROFICIENT`.
- **Editorial status:** `DRAFT`, `IN_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`,
  `PUBLISHED`, or `ARCHIVED`.
- **Revision:** an editable version of a problem. Editing a published problem
  creates a new revision.
- **Published snapshot:** the immutable public projection of an approved
  revision, addressed by a stable permanent URL.

## 5. In-scope behavior

- Canonical vocabulary import, validation, bilingual labels, aliases, topic
  hierarchy, and Release 0 availability policy.
- Public browsing at `/problems`, search, stage and taxonomy filters, sorting,
  dense desktop results, responsive mobile cards, and permanent problem URLs.
- Anonymous device-local task status where specified by the UI design.
- Public problem detail, supported lightweight answer submission, feedback,
  and an editorially recommended next problem.
- Author problem management under `/author/problems`, structured drafting,
  autosave and recovery, validation, learner-format preview, editorial review,
  revision, publication, and archiving.
- Manual or lightweight automated scoring without complex job-based judging.
- Strict separation between drafts and published snapshots.

## 6. Explicit exclusions

- Authentication, accounts, roles enforced by an identity provider, teams, and
  organization management.
- Leaderboards, contests, streak pressure, social features, and competitive
  ranking.
- GPU workloads, hosted notebooks, dataset hosting, complex asynchronous
  judging, or advanced execution sandboxes.
- Semantic retrieval, a separate vector database, broad personalization, and
  a general-purpose CMS.
- Document ingestion, LLM generation, embeddings, Celery, Redis, or MinIO
  unless a later accepted Release 0 requirement creates a concrete use case.
- Editing canonical vocabulary inside the problem editor. Missing vocabulary
  may be proposed for curriculum-owner review.
- Publishing stages, task types, compute tiers, or scoring methods that the
  Release 0 availability policy does not enable.

## 7. Success measures

Release 0 is successful when:

- A reviewed author can move a valid problem from draft through approval to a
  public permanent URL without exposing intermediate revisions.
- A learner can discover, open, answer, receive feedback on, and continue from
  a published problem without an account.
- Public APIs and builds cannot return draft or unapproved content.
- Canonical vocabulary selections remain valid, bilingual, hierarchical, and
  traceable to `vocab.md`.
- The critical learner and author workflows are covered by automated tests,
  including responsive and accessibility behavior where applicable.
- The local development setup is deterministic and its documented quality
  commands can be run without hidden global state.

## 8. Story and acceptance-criteria convention

Each story has a stable ID in the form `R0-<three digits>`, followed by a
short title, persona, and outcome:

> As a `<persona>`, I want `<capability>` so that `<outcome>`.

Acceptance criteria use numbered Given/When/Then scenarios:

```text
AC-R0-XXX-01
Given <precondition>
When <action>
Then <observable result>
```

Criteria describe externally observable behavior and reference canonical codes
where a controlled value is involved. Cross-cutting requirements use IDs in
the same namespace and are linked to the stories they constrain.

## 9. Governing-source reconciliation

This document narrows `master_plan.md` and `ui_release_0.md` to the Release 0
editorial pilot. Where the documents differ in presentation detail, the
Release 0 UI document governs the interface. `vocab.md` remains the sole
authority for controlled values, and `code_standard.md` governs implementation
quality and verification. No unresolved contradiction is intentionally hidden;
product decisions that cannot be resolved from those sources are recorded in
the final requirements baseline.

## 10. Learner discovery stories

### R0-011-01 — Browse the published problem library

As a learner, I want to browse a dense list of available problems so that I can
choose what to practise next.

```text
AC-R0-011-01
Given published snapshots exist and drafts or unapproved revisions also exist
When I open `/problems`
Then the result contains only published snapshots and shows the problem title,
stage and difficulty together, primary competency, up to two topics, type,
expected minutes, compute tier, task status, and learning evidence.

AC-R0-011-02
Given a problem has more than two topics
When its row or card is rendered
Then no more than two topic labels are shown and the remaining count is
available through an accessible collapsed affordance.

AC-R0-011-03
Given public problem data is unavailable
When the library load fails
Then the learner sees a safe retry action and feedback path without draft data,
infrastructure details, stack traces, or provider errors.
```

### R0-011-02 — Select a pathway stage

As a learner, I want to select my pathway stage so that recommendations and
difficulty are interpreted in the right curriculum context.

```text
AC-R0-011-04
Given the stage selector is visible
When I inspect it
Then it shows the canonical stages in order: `AI_1_FOUNDATIONS`,
`AI_2_COMPETITION_FOUNDATIONS`, `AI_3_HIGHSCHOOL`, `AI_4_STUDENT`, and
`AI_OPEN`, with bilingual presentation labels where available.

AC-R0-011-05
Given the Release 0 availability policy enables only the approved pilot stages
When I inspect later-stage controls
Then unavailable stages may be visible as disabled “Coming next” options but
cannot scope a publishable or public problem selection.

AC-R0-011-06
Given I select an available stage
When the library updates
Then the selected stage scopes the recommendation and results, remains visible,
and is represented in the shareable URL state.
```

### R0-011-03 — Search and filter the library

As a learner, I want to search and filter problems by curriculum metadata so
that I can find relevant practice quickly.

```text
AC-R0-011-07
Given published problems contain English labels, Vietnamese labels, or approved
aliases in titles, objectives, competencies, and topics
When I search using any of those supported terms
Then matching published problems are returned while persisted selections remain
canonical codes.

AC-R0-011-08
Given I open the topic picker
When I search and select a parent or leaf topic
Then the hierarchy is shown as family, intermediate category, and leaf topic,
and descendants are included only after I explicitly enable “Include subtopics”.

AC-R0-011-09
Given I use stage, competency, topic, difficulty, task type, status, evidence,
time, compute, or additional filters
When the result list changes
Then active filters are visible, removable, and serialized in the URL query
string without exposing unpublished records.

AC-R0-011-10
Given the default list is ordered by editorial learning-path order and then
difficulty
When I choose an allowed alternative sort
Then the list supports newest, expected time, and title sorting with explicit
pagination and a result count.

AC-R0-011-11
Given active filters produce no matches
When the list is rendered
Then the empty state identifies that filters are active and offers a clear-
filters action.
```

### R0-011-04 — Use the library across responsive layouts

As a learner, I want the library to remain scannable on my device so that I can
discover problems without losing important metadata.

```text
AC-R0-011-12
Given a viewport at or above 768 px
When the library is rendered
Then results use the dense table structure and preserve meaningful learning
information before truncating it.

AC-R0-011-13
Given a viewport below 768 px
When the library is rendered
Then each result uses the specified card treatment rather than squeezing the
desktop table into the narrow viewport.

AC-R0-011-14
Given a learner uses keyboard navigation or assistive technology
When they operate filters, rows, disclosures, or dialogs
Then controls have visible labels, deterministic focus behavior, accessible
names, and no status is communicated by color alone.
```

### R0-011-05 — Open a permanent problem URL

As a learner, I want each published problem to have a stable URL so that I can
bookmark or share it.

```text
AC-R0-011-15
Given a problem snapshot is published with a unique stable slug
When I open its public URL directly or from a list row
Then the same published problem detail is returned without requiring prior list
navigation or learner state.

AC-R0-011-16
Given a later revision is created or published for an existing problem
When I revisit its permanent URL
Then the URL remains unchanged and shows only the current published snapshot;
draft and unapproved revisions remain private.
```

## 11. Learner solving-loop stories

### R0-012-01 — Read a problem and its learning context

As a learner, I want to understand the objective, prerequisites, and response
instructions so that I know what the problem asks me to demonstrate.

```text
AC-R0-012-01
Given I open a published permanent problem URL
When the detail page loads
Then it shows the title, stage and difficulty together, observable learning
objective, prerequisites, statement, provided information or examples,
constraints, response area, and available hints or explanation according to the
published snapshot.

AC-R0-012-02
Given a published problem has English and Vietnamese content or a translation
marked pending during authoring
When I view the public page
Then the available public content follows the published language policy and
never exposes author-only translation warnings or draft fields.
```

### R0-012-02 — Use the approved Release 0 response types

As a learner, I want a predictable response form so that I can answer without
an advanced judge or hosted execution environment.

Release 0 accepts exactly these canonical task types:

- `QUIZ_SINGLE` — one selected choice.
- `QUIZ_MULTIPLE` — one or more selected choices.
- `NUMERIC_ANSWER` — a numeric value, with an optional unit and explicit
  tolerance policy.
- `SHORT_ANSWER` — a short written response assessed by configured exact,
  keyword, or human-rubric guidance.
- `CODE_FUNCTION` — a small function response evaluated under the published
  language, signature, starter code, limits, and tests.
- `CODE_DEBUGGING` — a bounded correction to supplied code evaluated by tests.
- `CODE_COMPLETION` — a bounded completion to supplied code evaluated by tests.

These types are available only with the `NONE`, `BROWSER`, or `CPU_LIGHT`
compute tiers. All other canonical task types, scoring methods requiring hidden
labels or ranking, and all GPU or distributed tiers are unavailable for Release
0 publication. The vocabulary records remain canonical and are not deleted.

```text
AC-R0-012-03
Given a published problem uses an accepted Release 0 task type
When I open its response area
Then the form matches that task type, identifies required inputs, supports
keyboard and assistive-technology use, and does not request unavailable runtime
resources.

AC-R0-012-04
Given a problem uses a task type or compute tier outside the Release 0 policy
When an author attempts to publish it
Then publication is blocked with a stable actionable error and the problem
cannot appear in public reads or recommendations.

AC-R0-012-05
Given I submit an incomplete or malformed response
When validation runs
Then the response is rejected safely with field-level guidance, no attempt is
recorded as completed, and no implementation or provider details are exposed.
```

### R0-012-03 — Submit and receive lightweight feedback

As a learner, I want feedback after submission so that I can understand whether
my answer met the problem's assessment criteria.

```text
AC-R0-012-06
Given my response satisfies the published response contract
When I submit it
Then the system records an attempt and returns a safe result containing the
outcome, score or rubric result when configured, actionable feedback, and any
allowed next step.

AC-R0-012-07
Given a scoring configuration has weighted components
When the submission is assessed
Then the component weights are applied using decimal-safe arithmetic, their
total is exactly `1.0`, and the response never reveals hidden answers, test
data, unpublished explanations, or internal errors.

AC-R0-012-08
Given a manual or delayed assessment is required
When the learner submits
Then the UI clearly reports that assessment is pending and does not claim a
completed result or learning evidence prematurely.
```

### R0-012-04 — Keep anonymous progress on the device

As an anonymous learner, I want basic progress to survive a refresh so that I
can continue on the same device without creating an account.

```text
AC-R0-012-09
Given local storage is available
When I open, attempt, or complete a published problem
Then only the approved device-local progress data is persisted, using task
status `NOT_STARTED`, `ATTEMPTED`, or `COMPLETED` and separate learning
evidence when evidence is available.

AC-R0-012-10
Given I refresh the page or return to the library on the same device
When local progress is readable
Then the status, evidence display data, recent history, and recommendation
context are restored without an account or server identity.

AC-R0-012-11
Given local storage is unavailable, corrupted, or cleared
When I use the learner product
Then browsing and solving remain available, progress is treated as temporary,
and the UI explains the persistence limitation without exposing stored content.
```

### R0-012-05 — Send problem feedback

As a learner, I want to report an issue from every public problem page so that
content and usability problems can be reviewed.

```text
AC-R0-012-12
Given I am viewing any published problem
When I open the feedback mechanism
Then it identifies the problem safely, offers the approved feedback categories,
accepts a bounded message, and does not require an account.

AC-R0-012-13
Given feedback input is invalid or exceeds its limits
When I submit it
Then the request is rejected with a safe actionable error and no partial or
unbounded record is stored.

AC-R0-012-14
Given valid feedback is submitted repeatedly from an anonymous device
When abuse controls apply
Then the system rate-limits or rejects excessive submissions without revealing
whether private moderation data exists.
```

### R0-012-06 — Continue to the recommended problem

As a learner, I want one clear next recommendation so that completing a
problem leads naturally to another suitable problem.

```text
AC-R0-012-15
Given I have no local history for the selected stage
When the library or problem page shows a recommendation
Then it labels the item “Recommended start” and uses the editorially chosen
first published problem without claiming personalization.

AC-R0-012-16
Given I have attempted or completed problems locally
When a recommendation is calculated
Then it selects one published problem compatible with the selected stage,
prerequisites, Release 0 availability policy, and editorial learning path,
excluding the current problem when a suitable alternative exists.

AC-R0-012-17
Given I complete a problem and choose to continue
When the next recommendation is opened
Then it uses a permanent URL, preserves the selected stage context, and never
redirects to a draft, archived-only revision, or unavailable task.
```
