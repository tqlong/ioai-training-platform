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

PostgreSQL integration tests explicitly downgrade to `base`, upgrade to `head`,
exercise constraints and normalized repository transactions, then downgrade to
`base` during teardown. `scripts/dev_redeploy.sh` subsequently recreates and
waits for PostgreSQL, upgrades migrations, synchronizes vocabulary, recreates
API/Learn/Studio, waits for health, and checks both frontend routes and API
reads.

Playwright author review/publication and responsive learner-preview rendering
are not Phase 6 gates: R0-06019 explicitly assigns that browser workflow to
R0-072, and editorial review/publication belongs to Phase 7. No Phase 6 quality
gate is otherwise skipped.

The final 2026-08-09 baseline passed 147 pytest tests, 24 Studio component
tests, all other frontend package tests, both Next.js production builds, and all
format/lint/type/drift/head checks. Redeployment finished with migration
`20260809_06006`, 343 unchanged canonical vocabulary records on the idempotency
run, and healthy PostgreSQL, API, Learn, and Studio services.
