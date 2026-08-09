# Release 0 Phase 8 learner implementation baseline

## Scope and evidence reviewed

This baseline records the repository state before Phase 8 behavior changes. It
maps every learner acceptance criterion to an owning Phase 8 step so work builds
on the Phase 7 publication boundary instead of introducing a second public data
path.

Evidence inspected:

- `ioai.application.problems.public_queries` already projects current published
  snapshots and strips workflow/internal fields, but supports only offset/limit
  reads and a slug lookup.
- `SqlAlchemyPublishedProblemReader` starts from
  `problem.current_published_snapshot_id`; this is the reusable repository
  isolation boundary for list, detail, recommendation, and submission work.
- the public problem routes and typed public problem DTOs are not yet registered;
  the existing problem router is author/editorial only.
- the generated OpenAPI client has author/public-vocabulary foundations but no
  learner list, detail, recommendation, submission, or feedback operations.
- PostgreSQL has immutable `published_snapshot` records and publication
  idempotency, but no learner-attempt or problem-feedback tables.
- `/problems` is a fixture-backed empty shell. There is no permanent detail
  route, discovery state, response form, progress adapter, recommendation UI,
  or problem-feedback UI.
- Phase 7 isolation tests already prove that current public projections do not
  serialize drafts, workflow state, answer keys, hidden tests, object keys, or
  internal revision identifiers. Phase 8 must extend, not bypass, those tests.

## Acceptance-criterion ownership

| Acceptance criterion | Baseline status | Owning implementation step | Required proof |
| --- | --- | --- | --- |
| `AC-R0-011-01` | Partial: published-only reader exists; required list fields and progress overlay do not | `R0-08003`, `R0-08004`, `R0-08008` | repository/API isolation and table component tests |
| `AC-R0-011-02` | Missing | `R0-08004`, `R0-08008` | DTO and accessible disclosure tests |
| `AC-R0-011-03` | Missing | `R0-08004`, `R0-08009` | safe API error and retry/feedback UI tests |
| `AC-R0-011-04` | Vocabulary exists; selector missing | `R0-08006` | canonical ordered bilingual stage component test |
| `AC-R0-011-05` | Availability policy exists; learner control missing | `R0-08004`, `R0-08006` | API rejection and disabled-control tests |
| `AC-R0-011-06` | Missing | `R0-08005`, `R0-08006` | stage-scoped API and shareable URL tests |
| `AC-R0-011-07` | Vocabulary search exists separately; problem search missing | `R0-08003`, `R0-08006` | bilingual/alias repository and UI tests |
| `AC-R0-011-08` | Vocabulary hierarchy exists; problem filtering UI/query missing | `R0-08003`, `R0-08006` | explicit descendant repository and picker tests |
| `AC-R0-011-09` | Missing; status/evidence remain client-owned | `R0-08003`, `R0-08004`, `R0-08006`, `R0-08015` | query validation, URL token, and overlay tests |
| `AC-R0-011-10` | Missing | `R0-08003`, `R0-08004`, `R0-08006` | deterministic sort/pagination/count tests |
| `AC-R0-011-11` | Missing | `R0-08006`, `R0-08009` | active-filter empty-state test |
| `AC-R0-011-12` | Missing | `R0-08008`, `R0-08009` | table breakpoint tests |
| `AC-R0-011-13` | Missing | `R0-08009` | mobile-card breakpoint tests |
| `AC-R0-011-14` | Shell semantics only | `R0-08006`, `R0-08008`, `R0-08009`, `R0-08018` | keyboard/focus/accessible-name/component and browser tests |
| `AC-R0-011-15` | Partial: stable slug reader exists; route/page missing | `R0-08010`, `R0-08011` | direct URL API/component tests |
| `AC-R0-011-16` | Phase 7 snapshot pointer proves isolation; learner route missing | `R0-08010`, `R0-08011`, `R0-08018` | replacement-revision API and browser tests |
| `AC-R0-012-01` | Published payload exists; complete DTO/page missing | `R0-08010`, `R0-08011` | detail projection and reading-order tests |
| `AC-R0-012-02` | Author preview warnings are isolated; public language policy missing | `R0-08010`, `R0-08011` | projection and UI tests with partial translations |
| `AC-R0-012-03` | Five task types are domain-valid; learner forms missing | `R0-08011`, `R0-08012` | accessible discriminated-form tests |
| `AC-R0-012-04` | Implemented by central availability/publication validation | Reused Phase 5-7; regression in `R0-08014` and `R0-08018` | policy, publication, public-isolation tests |
| `AC-R0-012-05` | Domain configuration validation exists; submission validation missing | `R0-08012`, `R0-08013`, `R0-08014` | malformed response domain/API/UI tests |
| `AC-R0-012-06` | Missing attempt persistence/use case/API/UI | `R0-08002`, `R0-08013`, `R0-08014` | transaction, application, API, and component tests |
| `AC-R0-012-07` | Decimal weight invariant exists; assessment/result safety missing | `R0-08013`, `R0-08014` | decimal scoring and leak-regression tests |
| `AC-R0-012-08` | Human-rubric configuration exists; pending flow missing | `R0-08013`, `R0-08014` | pending assessment application/API/UI tests |
| `AC-R0-012-09` | Missing | `R0-08015` | versioned bounded local adapter tests |
| `AC-R0-012-10` | Missing | `R0-08007`, `R0-08015` | refresh/restoration and overlay tests |
| `AC-R0-012-11` | Missing | `R0-08009`, `R0-08015`, `R0-08018` | corrupt/disabled storage component/browser tests |
| `AC-R0-012-12` | Missing persistence/API/UI | `R0-08002`, `R0-08016`, `R0-08017` | bounded record, contract, and dialog tests |
| `AC-R0-012-13` | Missing | `R0-08016`, `R0-08017` | no-partial-write validation tests |
| `AC-R0-012-14` | Missing | `R0-08016`, `R0-08017`, `R0-08018` | abuse-limit repository/API/browser tests |
| `AC-R0-012-15` | Missing | `R0-08005`, `R0-08007` | editorial-start policy/API/card tests |
| `AC-R0-012-16` | Missing | `R0-08005`, `R0-08007`, `R0-08015` | eligible-candidate/history policy tests |
| `AC-R0-012-17` | Missing | `R0-08005`, `R0-08017`, `R0-08018` | permanent next URL and isolation browser tests |

## Boundary decisions for implementation

1. All server learner reads start from `PublishedProblemReader` backed by the
   current snapshot pointer. Public routes never accept revision, preview, or
   draft identifiers.
2. The learner application replaces its fixture with generated API types. It
   does not import Studio application code or duplicate backend schemas.
3. The URL owns discovery state, PostgreSQL owns snapshots/attempts/feedback,
   and the browser owns anonymous progress. Task status/evidence filters are
   applied to validated local overlays; they are not invented as account data.
4. Submission, feedback, and recommendation extend the Phase 7 leak-path suite
   before their public routes are considered complete.
5. Deployment scripts and test scripts remain separate. Phase 8 receives a
   focused quality script and an independent redeployment path before its final
   baseline is checked.

