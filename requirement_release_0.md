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

