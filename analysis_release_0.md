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
