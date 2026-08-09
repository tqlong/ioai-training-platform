# Canonical Vocabulary Baseline (Phase 5)

## Implemented user-facing capability

- Public clients can query active canonical vocabulary by type, bilingual label,
  approved alias, hierarchy root, and explicit descendant expansion.
- Author clients can query canonical values with Release 0 availability status
  and record separately reviewable missing-value proposals.
- API selections and frontend helpers preserve composite
  `(vocabulary_type, code)` identity and bilingual labels with Vietnamese
  diacritics.

Phase 5 provides APIs and shared packages, not complete learner or Studio
screens. Author metadata controls are Phase 6 and learner filters are Phase 7.

## Canonical pipeline

```text
vocab.md
  -> deterministic parser and domain validation
  -> backend/generated/vocabulary.json
  -> idempotent PostgreSQL synchronization
  -> public/author FastAPI projections
  -> generated OpenAPI TypeScript and frontend vocabulary data
```

The checked-in source currently yields 343 validated records. Release 0 enables
AI Foundations and Competition Foundations, five task types, `NONE`/`BROWSER`/
`CPU_LIGHT` compute, and the approved scoring methods. Other canonical values
remain stored but publication-blocking.

## Operational proof

- `bash scripts/vocabulary_drift_check.sh`
- `bash scripts/openapi_drift_check.sh`
- `bash scripts/dev_migrate.sh`
- `bash scripts/dev_seed.sh`
- `bash scripts/dev_redeploy.sh`
- `bash scripts/dev_health.sh`

Backend tests cover parsing, graph invariants, policy, migrations, synchronization,
queries, API projections, and proposal isolation. Frontend tests cover generated
client behavior and artifact-backed helpers. The root `pnpm test:e2e` command
currently reports no package with a `test:e2e` script; Phase 5 introduces no
learner or Studio screen, so browser workflow coverage begins with the affected
Phase 6 and Phase 7 UI slices. No Celery, Redis, Docling, MinIO, LLM provider,
embeddings, GPU service, authentication, or vocabulary editor was introduced.
