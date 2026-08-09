# Decisions and Traceability Index

## Purpose

This directory records lightweight architecture decision records (ADRs) and a
traceability index for Release 0 work items.

## ADR conventions

- ADR files: `docs/decisions/adr-XXXX-<topic>.md`
- Format:
  - `Status` (`Proposed`, `Accepted`, `Superseded`, `Deprecated`)
  - `Context`
  - `Decision`
  - `Consequences`
- Keep ADRs short and practical; remove only by explicit deprecation when scope
  or evidence changes.

## Traceability index

Map each requirement/user-story ID to analysis, design, implementation, and tests.
Update this as artifacts land.

| User-story / Requirement ID | Analysis source | Design source | Implementation source | Test coverage |
| --- | --- | --- | --- | --- |
| R0-000 | Governing baseline established in `plan_release_0.md` | N/A | N/A | N/A |
| R0-001 | `AGENTS.md`, `master_plan.md`, `ui_release_0.md`, `code_standard.md` | To be added in Phase 1 | `README.md` | `README` review checklist |
| R0-002 | `plan_release_0.md` | `docs/decisions/README.md` | `docs/decisions/README.md` | Traceability index review |
| R0-010 | `requirement_release_0.md` sections 1-9 | `requirement_release_0.md` sections 1-9 | Phase 1 documentation | Requirements review |
| R0-011 | `analysis_release_0.md` sections 6, 9, and 10 | `design_release_0.md` sections 6, 8, 11, and 12; `ui_release_0.md` section 5 | Phase 7 current-snapshot reader/isolation foundation; Phase 8 criterion ownership in `docs/learner-phase8-baseline.md` | Existing `test_public_queries.py` and `test_public_isolation.py`; remaining API, component, accessibility, and E2E proof assigned to `R0-08003`–`R0-08018` |
| R0-012 | `analysis_release_0.md` sections 4, 6, 9, and 10 | `design_release_0.md` sections 3-6 and 9-12 | Existing task-type/scoring configuration and snapshot foundations; Phase 8 criterion ownership in `docs/learner-phase8-baseline.md` | Existing assessment/public-isolation tests; remaining submission, progress, feedback, recommendation, and E2E proof assigned to `R0-08002`–`R0-08018` |
| R0-013 | `ui_release_0.md`, `code_standard.md` | `requirement_release_0.md` section 12 | Phase 6 problem domain, persistence, author API, generated client, and Studio authoring; published-revision editing remains Phase 7 | Domain, PostgreSQL, API, generated-client, and Studio component tests indexed by R0-060 |
| R0-014 | `master_plan.md`, `ui_release_0.md`, `AGENTS.md` | `requirement_release_0.md` section 13 | Pending Phase 4/6/7 implementation | Workflow, isolation, and publication E2E tests |
| R0-015 | `AGENTS.md`, `code_standard.md`, `ui_release_0.md` | `requirement_release_0.md` section 14 | Pending Phase 3/4/7 implementation | Quality, security, accessibility, and operations checks |
| R0-016 | All governing documents and `plan_release_0.md` | `requirement_release_0.md` section 15 | `docs/decisions/README.md` | Traceability and baseline review |
| R0-020 | `requirement_release_0.md` R0-010 | `analysis_release_0.md` sections 1-2 | Pending Phase 3/4 | Actor/context review |
| R0-021 | `requirement_release_0.md` R0-010/R0-015 | `analysis_release_0.md` section 3 | Pending Phase 3/4 | Trust-boundary and security tests |
| R0-022 | `requirement_release_0.md` R0-012/R0-013/R0-014/R0-015 | `analysis_release_0.md` section 4 | Pending Phase 4/6 | Domain and persistence tests |
| R0-023 | `requirement_release_0.md` R0-010/R0-011/R0-012/R0-013/R0-015/R0-016 | `analysis_release_0.md` section 5 | Pending Phase 4/5 | Import, graph, drift, and policy tests |
| R0-024 | `requirement_release_0.md` R0-011/R0-012 | `analysis_release_0.md` section 6 | Pending Phase 4/7 | Learner API/UI/E2E tests |
| R0-025 | `requirement_release_0.md` R0-013 | `analysis_release_0.md` section 7 | Phase 6 authoring use cases, revision commands, recovery, validation, and preview projection | `test_author_problem_api.py`, `test_authoring.py`, `draft-editor.test.tsx`, `validation-panel.test.tsx` |
| R0-026 | `requirement_release_0.md` R0-014 | `analysis_release_0.md` section 8 | Pending Phase 3/6/7 | Workflow and publication tests |
| R0-027 | `requirement_release_0.md` R0-011/R0-012/R0-013/R0-014/R0-015 | `analysis_release_0.md` section 9 | Pending Phase 3/4/7 | Public/draft isolation tests |
| R0-028 | `requirement_release_0.md` R0-015 and all affected groups | `analysis_release_0.md` section 10 | Pending Phase 3/4/7 | Risk matrix and quality gates |
| R0-029 | `requirement_release_0.md` R0-010 through R0-016 | `analysis_release_0.md` section 11 | `docs/decisions/README.md` | Analysis baseline review |
| R0-03001 | `requirement_release_0.md` R0-010/R0-015 | `design_release_0.md` sections 1-2 | Pending Phase 4 | Architecture and boundary tests |
| R0-03002 | `requirement_release_0.md` R0-010/R0-015 | `design_release_0.md` section 2 | Pending Phase 4 | Dependency-boundary checks |
| R0-03003 | `requirement_release_0.md` R0-012/R0-013/R0-014/R0-015 | `design_release_0.md` section 3 | Pending Phase 5/6 | Domain invariant tests |
| R0-03004 | `requirement_release_0.md` R0-012/R0-013/R0-014/R0-015 | `design_release_0.md` section 4 | Pending Phase 5/6/7 | Use-case and port tests |
| R0-03005 | `requirement_release_0.md` R0-010/R0-011/R0-012/R0-013/R0-016 | `design_release_0.md` section 5 | Pending Phase 5 | Import, graph, drift, and policy tests |
| R0-03006 | `requirement_release_0.md` R0-011/R0-012/R0-015 | `design_release_0.md` section 6 | Pending Phase 4/7 | Public API and learner E2E tests |
| R0-03007 | `requirement_release_0.md` R0-013/R0-014/R0-015 | `design_release_0.md` section 7 | Phase 6 author revision API; editorial transitions remain Phase 7 | `test_author_problem_api.py`, generated OpenAPI/client drift tests |
| R0-03008 | `requirement_release_0.md` R0-011 through R0-015 | `design_release_0.md` section 8 | Pending Phase 4/7 | OpenAPI/client drift tests |
| R0-03009 | `requirement_release_0.md` R0-012 through R0-015 | `design_release_0.md` section 9 | Pending Phase 4/6 | PostgreSQL repository tests |
| R0-03010 | `requirement_release_0.md` R0-013 through R0-015 | `design_release_0.md` section 10 | Pending Phase 4/6/7 | Transaction and migration tests |
| R0-03011 | `requirement_release_0.md` R0-014/R0-015 | `design_release_0.md` section 11 | Pending Phase 4/7 | Isolation, privacy, and error tests |
| R0-03012 | `requirement_release_0.md` R0-011/R0-012/R0-015 | `design_release_0.md` section 12 | Pending Phase 4/7 | Learner component and E2E tests |
| R0-03013 | `requirement_release_0.md` R0-013/R0-014/R0-015 | `design_release_0.md` section 13 | Pending Phase 4/7 | Studio component and E2E tests |
| R0-03014 | `requirement_release_0.md` R0-015 | `design_release_0.md` section 14 | Pending Phase 4/7 | Compose and operations checks |
| R0-03015 | `requirement_release_0.md` R0-015 and affected groups | `design_release_0.md` section 15 | Pending Phase 4/7 | Verification and quality gates |
| R0-03016 | `requirement_release_0.md` R0-010 through R0-016 | `design_release_0.md` section 16 | `docs/decisions/README.md` | Design baseline review |
| R0-04001 | `analysis_release_0.md` §§2,10; `design_release_0.md` §§1,2 | `design_release_0.md` §§1,2 | `pyproject.toml`, `.python-version`, `uv.lock` | `git commit` history |
| R0-04002 | `analysis_release_0.md` §§4,10; `design_release_0.md` §2 | `design_release_0.md` §2 | `backend/src/ioai/...` package directories, `backend/tests/unit/test_smoke_imports.py` | `test_ioai_packages_import_without_side_effects` |
| R0-04003 | `analysis_release_0.md` §§2,10; `design_release_0.md` §§1,2 | `design_release_0.md` §§1,2 | `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `frontend/packages/*` | `npm` scripts smoke checks in package manifests |
| R0-04004 | `analysis_release_0.md` §§2,10; `design_release_0.md` §§2,8 | `design_release_0.md` §§2,8 | `frontend/packages/api-client`, `ui`, `vocabulary` | package smoke tests in each package |
| R0-04005 | `analysis_release_0.md` §§6 | `design_release_0.md` §12 | `frontend/apps/learn` shell | `frontend/apps/learn/tests/problems.test.tsx` |
| R0-04006 | `analysis_release_0.md` §§7 | `design_release_0.md` §13 | `frontend/apps/studio` shell | `frontend/apps/studio/tests/author-problems.test.tsx` |
| R0-04007 | `analysis_release_0.md` §§2,3,10; `design_release_0.md` §§1,2 | `design_release_0.md` §§1,2 | `backend/src/ioai/entrypoints/api/{settings,factory,main}.py` | `backend/tests/unit/test_api_factory.py` |
| R0-04008 | `analysis_release_0.md` §§9,10; `design_release_0.md` §§6-8,15 | `design_release_0.md` §§6-8,15 | `backend/src/ioai/entrypoints/api/{errors,openapi}` | `backend/tests/unit/test_health_endpoints.py`, `backend/tests/unit/test_openapi_contract_smoke.py` |
| R0-04009 | `analysis_release_0.md` §§4,9,10; `design_release_0.md` §§9,10 | `design_release_0.md` §§9,10 | `backend/src/ioai/adapters/database`, `backend/alembic`, `backend/scripts/check_alembic_head.py` | `backend/tests/integration/test_database_readiness.py` |
| R0-04010 | `analysis_release_0.md` §10; `design_release_0.md` §15 | `design_release_0.md` §15 | `backend/tests/fixtures`, `scripts/foundation_quality.sh` | `backend/tests/unit/test_fixtures.py` |
| R0-04011 | `analysis_release_0.md` §§2,3,9,10; `design_release_0.md` §14 | `design_release_0.md` §14 | `docker-compose.yml` | `backend/tests/integration/test_foundation_stack_smoke.py` |
| R0-04012 | `analysis_release_0.md` §§3,10; `design_release_0.md` §§10,14 | `design_release_0.md` §§10,14 | `docs/local-operations.md`, `scripts/dev_*`, `scripts/db_backup_restore.sh` | `backend/tests/unit/test_fixtures.py` |
| R0-04013 | `analysis_release_0.md` §§3,9,10 | `design_release_0.md` §§11-15 | `backend/tests/integration/test_foundation_stack_smoke.py` | boundary smoke suite |
| R0-04014 | `analysis_release_0.md` §10; `design_release_0.md` §§8,15 | `design_release_0.md` §§8,15 | `.github/workflows/release-0-ci.yml`, `scripts/openapi_drift_check.sh` | CI config review |
| R0-04015 | `requirement_release_0.md`, `analysis_release_0.md`, `design_release_0.md` | same as row source | `docs/decisions/README.md` | traceability review checklist |
| R0-05001 | `analysis_release_0.md` §§5.1-5.2 | `design_release_0.md` §5.1 | artifact contract and representative source fixtures | artifact contract tests |
| R0-05002 | `analysis_release_0.md` §§4,5.2 | `design_release_0.md` §§3,5.2 | `ioai.domain.vocabulary.values` | domain value tests |
| R0-05003 | `analysis_release_0.md` §5.1 | `design_release_0.md` §5.1 | Markdown source adapter and parse command | source parser tests |
| R0-05004 | `analysis_release_0.md` §5.2 | `design_release_0.md` §§5.1-5.2 | vocabulary collection validator | identity, graph, cycle, and branch tests |
| R0-05005 | `analysis_release_0.md` §§5.1,5.5 | `design_release_0.md` §5.1 | generated backend artifact, runtime loader, drift command | generation, runtime, and drift tests |
| R0-05006 | `analysis_release_0.md` §5.4 | `design_release_0.md` §5.3 | central Release 0 availability policy | allowed/disabled/modality tests |
| R0-05007 | `analysis_release_0.md` §§5.2,9 | `design_release_0.md` §§5.4,9-10 | SQLAlchemy mapping and Alembic `05007` | PostgreSQL migration/constraint tests |
| R0-05008 | `analysis_release_0.md` §5.5 | `design_release_0.md` §§4.1,5.4 | synchronization use case, repository/UoW, Alembic `05008`, seed command | idempotency, update, identity, rollback tests |
| R0-05009 | `analysis_release_0.md` §§5.2-5.3,9 | `design_release_0.md` §§5.2,6 | typed query and PostgreSQL reader | bilingual, alias, hierarchy, breadcrumb tests |
| R0-05010 | `analysis_release_0.md` §§5.3,9 | `design_release_0.md` §§5.2,6-8 | public/author FastAPI vocabulary routes and contracts | API, errors, projection, OpenAPI tests |
| R0-05011 | `analysis_release_0.md` §§5.3,5.5 | `design_release_0.md` §5.4 | proposal domain/use case/table/routes, Alembic `05011` | domain, application, persistence, API isolation tests |
| R0-05012 | `analysis_release_0.md` §§5.1,9 | `design_release_0.md` §§2,5.1,8 | generated OpenAPI TypeScript and artifact-backed vocabulary package | client, package, contract/artifact drift tests |
| R0-05013 | `analysis_release_0.md` §§5,10 | `design_release_0.md` §§5,15 | `docs/vocabulary-baseline.md`, quality and deployment scripts | complete backend/frontend/migration/build/health gates |
| R0-060 | `requirement_release_0.md` R0-013; `analysis_release_0.md` §§4,7,9 | `design_release_0.md` §§3,4,7,9,11,13; `ui_release_0.md` §§6.1–6.7,6.9 | `ioai.domain.problems`, authoring application/UoW/API, Alembic `06006`, generated API client, uncached/proxied Studio author reads, Studio list/editor components, `scripts/dev_{start,redeploy}.sh`, `manual_R0_P6.md` | `backend/tests/unit/domain/problems`, `backend/tests/unit/application/problems`, `test_author_problem_api.py`, `test_problem_{migration,repository}.py`, API-client and Studio component tests, contract drift and production builds; see `docs/problem-authoring-baseline.md` |
| R0-061 | Pending | Pending | Pending | Pending |
| R0-062 | Pending | Pending | Pending | Pending |
| R0-08001 | `requirement_release_0.md` §§10-11; `analysis_release_0.md` §§4,6,9-10 | `design_release_0.md` §§3-6,8-12,15; `ui_release_0.md` §5 | `docs/learner-phase8-baseline.md` inventories current snapshot/API/client/schema/Learn boundaries and assigns all 33 learner criteria to Phase 8 steps | Documentation review plus repository evidence cited by the baseline |
| R0-08002 | `AC-R0-012-06`–`08`, `AC-R0-012-12`–`14`; `analysis_release_0.md` §§4,9-10 | `design_release_0.md` §§3-4,6.4,9-10 | `learner_records.py`, snapshot-bound SQLAlchemy learner record repository/models, Alembic `08002` | learner-record unit/model tests and isolated PostgreSQL migration/repository tests, including rollback and duplicate constraints |
| R0-08003 | `AC-R0-011-01`–`02`, `AC-R0-011-07`–`11`; `analysis_release_0.md` §§6,9 | `design_release_0.md` §§4,6.2,9.3,12.3 | typed `PublicProblemQuery`/page contracts, central curriculum difficulty order, and current-snapshot PostgreSQL reader filtering/search/sort/pagination | `test_public_queries.py`, `test_public_problem_query_repository.py`, and current-snapshot repository regression tests |
| R0-08004 | `R0-011`; `analysis_release_0.md` §§6,9-10 | `design_release_0.md` §§6,8,11 | `GET /api/v1/problems`, explicit public list DTOs, canonical/policy query validation, propagated request IDs, deterministic OpenAPI, and `listPublicProblems` generated-client wrapper | public API unit/integration and isolation tests, API-client tests, full backend suite, and OpenAPI drift check |
| R0-08005 | `AC-R0-012-15`–`17`; `analysis_release_0.md` §§6.3,9 | `design_release_0.md` §§4.1,6.1,12.3 | bounded local recommendation context, prerequisite-aware editorial policy, current-snapshot candidate reader, `GET /api/v1/problems/{slug}/recommendation`, and generated-client method | recommendation policy/API/client tests and PostgreSQL integration proof excluding draft-only candidates |
| R0-08006 | `AC-R0-011-04`–`11`; `analysis_release_0.md` §§5.3-5.4,6 | `design_release_0.md` §§5.2-5.3,6,12.2-12.3; `ui_release_0.md` §§5.2,5.4 | dynamic `/problems` page, public vocabulary availability, bounded canonical URL parser, ordered stage selector, compact/hierarchical filters, active tokens, sorting/pagination state, and eight topic-family shortcuts | Testing Library discovery tests, backend vocabulary/API tests, generated-client drift, workspace lint/type/tests, and separate Learn/Studio production builds |
| R0-08007 | `AC-R0-012-09`–`10`, `AC-R0-012-15`–`16`; `analysis_release_0.md` §§6.3-6.4 | `design_release_0.md` §§12.3-12.4; `ui_release_0.md` §§5.3,5.6-5.7 | first-viewport editorial recommendation, client-side public continuation lookup, bounded/versioned guidance parser, weekly goal/current path/prerequisite/recent/suggested-topic sidebar, and Learn API rewrite | Testing Library no-history, bounded/corrupt context, list-limit, and recommendation-continuation tests; workspace lint/type/tests and Learn production build |
| R0-08008 | `AC-R0-011-01`–`02`, `AC-R0-011-12`, `AC-R0-011-14`; `analysis_release_0.md` §6 | `design_release_0.md` §§6.3,12.2,12.5; `ui_release_0.md` §5.5 | sticky dense results table with separate text-backed status/evidence, objective and stable ID, paired stage/difficulty, competency, two-topic disclosure, type/time/compute, preserved return URL, and guarded row/title navigation | Testing Library semantic table/accessibility/navigation test plus Learn lint/type/test and production build |
| R0-08009 | `AC-R0-011-03`, `AC-R0-011-11`–`14`; `analysis_release_0.md` §6 | `design_release_0.md` §12.5; `ui_release_0.md` §§5.7–5.8 | below-768 problem cards and full-height filter sheet, 1024–1279 competency/evidence disclosures, count-aware filter action, clearable active-filter empty state, layout-preserving skeleton, and safe retry/feedback error boundary | Testing Library card, metadata, disclosure, filter focus/action, empty/loading/error accessibility tests plus Learn lint/type/test and production build |
| R0-08010 | `AC-R0-011-15`–`16`, `AC-R0-012-01`–`02`; `analysis_release_0.md` §§6,9 | `design_release_0.md` §§6.3,8,11-12; `ui_release_0.md` §5 | `GET /api/v1/problems/{slug}` current-snapshot projection with explicit content-block, prerequisite, resource-limit, response-form, feedback, and recommendation DTOs; uniform safe not-found; generated `PublicProblemDetail` and `getPublicProblem` client | projection/API safe-field and not-found tests, published-pointer/archive repository proof, generated-client request test, Pyright/Ruff, API-client tests, and OpenAPI drift check |
| R0-08011 | `AC-R0-011-15`, `AC-R0-012-01`–`03`; `analysis_release_0.md` §6 | `design_release_0.md` §§6.3,12.1-12.2; `ui_release_0.md` §5 | permanent `/problems/[slug]` page through generated public client, ordered published blocks, paired metadata, prerequisites, guarded hint/explanation disclosures, response/feedback/continuation regions, safe return context, loading and uniform unavailable states | Testing Library semantic detail/safe-return tests plus Learn lint, strict typecheck, and production build |
| R0-08012 | `AC-R0-012-03`, `AC-R0-012-05`; `analysis_release_0.md` §6 | `design_release_0.md` §§3.3,6.3,12.1; `ui_release_0.md` §5 | discriminated client forms for exactly single choice, multiple choice, numeric, short answer, and Python function responses; stable choice IDs, finite-number validation, unit/tolerance guidance, bounded text/code, starter/signature/public examples, and editable visible errors | Testing Library coverage for all five response families and invalid/editable behavior plus Learn lint, strict typecheck, and production build |
