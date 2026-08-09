# Release 0 Phase 6 problem-authoring baseline

Phase 6 implements the R0-013 authoring slice against `requirement_release_0.md`,
`analysis_release_0.md`, `design_release_0.md`, and the Studio behavior in
`ui_release_0.md`. It does not add Phase 7 editorial transitions or public
publication behavior.

## Delivered boundaries

- Framework-free problem identity, bilingual content, curriculum, prerequisite,
  response, scoring, resource, revision, and layered-validation rules.
- Alembic-managed draft tables plus transactional JSON aggregate and normalized
  competency, topic, prerequisite, response, and scoring persistence.
- Versioned author create/list/read/save/validate/preview commands under
  `/api/v1/author`, with stable conflicts and no public draft reader.
- Deterministic OpenAPI-derived TypeScript types and an IOAI Studio list/editor
  covering structured bilingual content, canonical metadata, assessment,
  resources, autosave recovery, validation focus, and proposal capture.
- Draft saving preserves incomplete author work: observable-objective and code
  configuration completeness are reported by layered validation rather than
  failing a save. Structural corruption remains a domain error.
- Studio reads mutable author drafts without HTTP/framework caching, uses the
  Compose-internal API for server rendering, and proxies same-origin browser
  commands so a loopback-only Studio remains usable through one SSH tunnel.
- English titles generate editable URL-safe slugs until the author takes manual
  control. Field help uses keyboard-accessible U+2753 controls, and validation
  separates signed, color-coded errors from non-blocking warnings.
- An author-only learner-shaped preview projection that strips answer keys,
  hidden tests, revision identifiers, and translation workflow state.

The Vietnamese input spike is recorded in
`docs/decisions/06013-vietnamese-input.md`. No browser Telex dependency met the
documented stability gate, so Studio preserves native composition events and
uses system input methods instead of shipping an application-owned converter.

## Verification baseline

`scripts/foundation_quality.sh` is the authoritative aggregate gate. It runs
backend formatting/lint/type checks and all pytest tests, frontend frozen-lockfile
installation/lint/type checks/unit and component tests/production builds,
vocabulary and OpenAPI drift checks, and the Alembic-head check.

PostgreSQL integration tests explicitly downgrade the isolated `ioai_test`
database to `base`, upgrade to `head`, exercise constraints and normalized
repository transactions, then downgrade that test database to `base` during
teardown. `scripts/dev_redeploy.sh` subsequently recreates and
waits for PostgreSQL, upgrades migrations, synchronizes vocabulary, recreates
API/Learn/Studio, waits for health, and checks both frontend routes and API
reads.

Playwright author review/publication and responsive learner-preview rendering
are not Phase 6 gates: R0-06019 explicitly assigns that browser workflow to
R0-072, and editorial review/publication belongs to Phase 7. No Phase 6 quality
gate is otherwise skipped.

The final 2026-08-09 baseline passed 150 pytest tests, 25 Studio component
tests, all other frontend package tests, both Next.js production builds, and all
format/lint/type/drift/head checks. Redeployment finished with migration
`20260809_06006`, 343 unchanged canonical vocabulary records on the idempotency
run, and healthy PostgreSQL, API, Learn, and Studio services.

Post-baseline manual verification also covered server/browser API routing,
uncached refresh of a versioned draft, freely saved incomplete code tests,
objective validation, explicit translation-pending warnings, automatic/manual
slug ownership, and accessible severity presentation. Regression coverage lives
in `test_foundation_stack_smoke.py`, the problem domain tests, API-client tests,
and Studio content/editor/validation component tests.

Migration integration coverage is isolated in the profile-scoped
`postgres-test` service and `ioai_test` database on port `5433`. A central
safety guard rejects missing test configuration and any database name that does
not end in `_test`, preventing the suite from downgrading the development
database containing local drafts.
