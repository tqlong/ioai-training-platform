# Release 0 Phase 7 editorial publication baseline

Phase 7 implements the `R0-014` editorial review and publication slice against
`requirement_release_0.md`, analysis sections 8-10, design sections 4 and 7-13,
and the Studio behavior in `ui_release_0.md`. Learner library/detail and solving
pages remain Phase 8; Phase 7 exposes only the stable published projection and
URL needed to prove publication isolation.

## Requirement traceability

| Requirement | Implementation boundary | Primary proof |
| --- | --- | --- |
| `AC-R0-014-01`–`04`, `13`, `16` | Domain-owned transition graph, required notes, validation before review/approval, immutable audit events, optimistic versions | `test_workflow.py`, `test_editorial.py`, `test_author_problem_api.py`, `editorial-review.test.tsx` |
| `AC-R0-014-05`, `07`, `08` | One repository transaction creates the snapshot, transition, and current-public pointer; publish uses scoped idempotency and rejects stale/invalid commands | `test_publication.py`, `test_problem_repository.py`, migration constraints |
| `AC-R0-014-06`, `09`, `10` | Published edits create successor draft revisions while the current immutable snapshot remains public until replacement | `test_publication.py`, `test_problem_repository.py`, `editorial-publication.spec.ts` |
| `AC-R0-014-11`, `12` | Stable slug conflicts are safe; public readers start from current published snapshots and public DTOs omit author/revision data | `test_public_queries.py`, `test_public_isolation.py`, `public_isolation_check.sh` |
| `AC-R0-014-14`, `15` | Archive removes public eligibility without deleting history; republishing requires an explicit new review flow | workflow, publication, repository, Studio component, and Playwright tests |
| `AC-R0-013-19`–`21` | Layered validation, explicit unsaved-state learner preview, persistent non-public marker, desktop/mobile width controls | validation/preview API and component tests plus `editorial-publication.spec.ts` |

The persistence adapter uses PostgreSQL transactions, row locks, version checks,
unique current-snapshot/slug constraints, and operation records. Author and
public APIs use separate application ports and contracts. The public projector
strips answer keys and author-only fields; drafts, previews, unapproved
revisions, and archived snapshots are ineligible at the repository boundary.

## Operational verification

Run `bash scripts/phase7_quality.sh` from the repository root. The command stops
the API and frontend development services so Next.js production builds do not
share `.next` output with running development servers. It then runs all Python
format/lint/type/pytest gates, frontend frozen-install/lint/type/component/build
gates, vocabulary/OpenAPI drift and Alembic-head checks, the public leak scan,
and finally redeploys PostgreSQL, applies migrations, synchronizes vocabulary,
recreates API/Learn/Studio, checks health, and runs the focused Chromium flow.

`scripts/test_editorial_e2e.sh` may be used alone when a healthy local stack is
already running. It covers validate, unsaved preview, submit, request changes,
successor revision, resubmit, approve, publish confirmation and stable URL, and
archive. Playwright retains a trace and screenshot on failure.

The PostgreSQL integration suite performs migration downgrade/upgrade checks.
As with the earlier baseline, do not run it against a database containing the
only copy of valuable local drafts; take a backup with
`scripts/db_backup_restore.sh backup` first.

The final 2026-08-09 cold-stack baseline passed 192 pytest tests, 35 Studio
component tests, all other frontend package tests, both Next.js production
builds, and all format/lint/type/drift/head/isolation checks. Redeployment
applied migration `20260809_07002`, synchronized 343 canonical vocabulary
records, reported PostgreSQL/API/Learn/Studio healthy, and passed the focused
Chromium workflow in 51.5 seconds. No gate was skipped.
