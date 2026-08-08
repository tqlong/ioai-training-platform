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
| R0-011 | `master_plan.md`, `ui_release_0.md`, `vocab.md` | `requirement_release_0.md` section 10 | Pending Phase 4/7 implementation | Public API, UI, accessibility, and E2E tests |
| R0-012 | `master_plan.md`, `ui_release_0.md`, `vocab.md` | `requirement_release_0.md` section 11 | Pending Phase 4/7 implementation | Submission, progress, feedback, and E2E tests |
| R0-013 | `ui_release_0.md`, `code_standard.md` | `requirement_release_0.md` section 12 | Pending Phase 4/6 implementation | Author validation, autosave, and preview tests |
| R0-014 | `master_plan.md`, `ui_release_0.md`, `AGENTS.md` | `requirement_release_0.md` section 13 | Pending Phase 4/6/7 implementation | Workflow, isolation, and publication E2E tests |
| R0-015 | `AGENTS.md`, `code_standard.md`, `ui_release_0.md` | `requirement_release_0.md` section 14 | Pending Phase 3/4/7 implementation | Quality, security, accessibility, and operations checks |
| R0-016 | All governing documents and `plan_release_0.md` | `requirement_release_0.md` section 15 | `docs/decisions/README.md` | Traceability and baseline review |
| R0-020 | `requirement_release_0.md` R0-010 | `analysis_release_0.md` sections 1-2 | Pending Phase 3/4 | Actor/context review |
| R0-021 | `requirement_release_0.md` R0-010/R0-015 | `analysis_release_0.md` section 3 | Pending Phase 3/4 | Trust-boundary and security tests |
| R0-022 | `requirement_release_0.md` R0-012/R0-013/R0-014/R0-015 | `analysis_release_0.md` section 4 | Pending Phase 4/6 | Domain and persistence tests |
| R0-023 | `requirement_release_0.md` R0-010/R0-011/R0-012/R0-013/R0-015/R0-016 | `analysis_release_0.md` section 5 | Pending Phase 4/5 | Import, graph, drift, and policy tests |
| R0-024 | `requirement_release_0.md` R0-011/R0-012 | `analysis_release_0.md` section 6 | Pending Phase 4/7 | Learner API/UI/E2E tests |
| R0-025 | `requirement_release_0.md` R0-013 | `analysis_release_0.md` section 7 | Pending Phase 3/6 | Autosave, validation, and preview tests |
| R0-026 | `requirement_release_0.md` R0-014 | `analysis_release_0.md` section 8 | Pending Phase 3/6/7 | Workflow and publication tests |
| R0-027 | `requirement_release_0.md` R0-011/R0-012/R0-013/R0-014/R0-015 | `analysis_release_0.md` section 9 | Pending Phase 3/4/7 | Public/draft isolation tests |
| R0-028 | `requirement_release_0.md` R0-015 and all affected groups | `analysis_release_0.md` section 10 | Pending Phase 3/4/7 | Risk matrix and quality gates |
| R0-029 | `requirement_release_0.md` R0-010 through R0-016 | `analysis_release_0.md` section 11 | `docs/decisions/README.md` | Analysis baseline review |
| R0-030 | Pending | Pending | Pending | Pending |
| R0-031 | Pending | Pending | Pending | Pending |
| R0-032 | Pending | Pending | Pending | Pending |
| R0-033 | Pending | Pending | Pending | Pending |
| R0-034 | Pending | Pending | Pending | Pending |
| R0-035 | Pending | Pending | Pending | Pending |
| R0-036 | Pending | Pending | Pending | Pending |
| R0-037 | Pending | Pending | Pending | Pending |
| R0-040 | Pending | Pending | Pending | Pending |
| R0-041 | Pending | Pending | Pending | Pending |
| R0-042 | Pending | Pending | Pending | Pending |
| R0-043 | Pending | Pending | Pending | Pending |
| R0-044 | Pending | Pending | Pending | Pending |
| R0-045 | Pending | Pending | Pending | Pending |
| R0-046 | Pending | Pending | Pending | Pending |
| R0-047 | Pending | Pending | Pending | Pending |
| R0-050 | Pending | Pending | Pending | Pending |
| R0-051 | Pending | Pending | Pending | Pending |
| R0-052 | Pending | Pending | Pending | Pending |
| R0-053 | Pending | Pending | Pending | Pending |
| R0-054 | Pending | Pending | Pending | Pending |
| R0-055 | Pending | Pending | Pending | Pending |
| R0-060 | Pending | Pending | Pending | Pending |
| R0-061 | Pending | Pending | Pending | Pending |
| R0-062 | Pending | Pending | Pending | Pending |
