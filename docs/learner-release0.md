# Release 0 learner library and solving loop

## Learner workflow

Open `/problems`, choose one of the enabled pilot stages, and use the URL-backed
search and taxonomy filters. Desktop and tablet layouts use the dense published
problem table; widths below 768 px use problem cards and a full-height filter
sheet. Opening a title or result keeps the filtered library URL as return
context.

The permanent `/problems/{slug}` page reads only the current published snapshot.
It presents the objective, prerequisites, ordered statement/examples/constraints,
resource limits, response form, feedback action, and—after a completed result—one
eligible continuation. Release 0 responses are single choice, multiple choice,
numeric, short answer, or Python function. Short/code answers may return a
pending human-assessment state.

Progress is anonymous and device-local. It stores only stable public slugs,
separate task status and learning evidence, bounded recent/path/timing/hint data,
and a bounded continuation measure. It never stores answers, credentials,
editorial state, draft data, or identity claims. Corrupt records are discarded;
when browser storage is disabled, browsing and solving continue with a temporary-
progress notice.

## Detail navigation performance

Problem rows and cards use prefetched Next.js navigation. The detail route
loads its problem through the generated public client and resolves display
labels from the generated canonical vocabulary artifact; it does not fan out
to runtime vocabulary endpoints. The PostgreSQL vocabulary adapter reuses one
request-scoped record snapshot for query results and breadcrumbs, preventing
the former per-item SELECT pattern.

The learner browser regression measures the interval from activating a warmed
problem link until the detail heading enters the DOM. It requires zero
vocabulary requests during navigation and a result below 500 ms in the local
Phase 8 deployment.

## Safe failure behavior

- A missing, draft-only, unapproved, or archived-only slug has the same public
  “Problem unavailable” result.
- A failed submission retains the answer and retries with the same client key.
- Pending assessment does not claim completion or learning evidence.
- Feedback retains the bounded message for retry and uses safe validation,
  conflict, rate-limit, and temporary-dependency messages.
- Public responses never contain revisions, workflow state, answers, hidden
  tests, moderation data, object keys, stack traces, or provider details.

## Verification and operations

Testing and deployment are intentionally separate:

```bash
# Static, unit, integration, migration, contract, and production-build gates.
bash scripts/phase8_test.sh

# Database/migration/backend/frontend deployment only.
bash scripts/phase8_redeploy.sh

# Browser workflow against the already deployed stack.
bash scripts/test_learner_e2e.sh
```

Set `PHASE8_E2E=1` when invoking `phase8_test.sh` only if a healthy stack was
deployed separately beforehand. Playwright artifacts remain ignored under
`test-results/` and `playwright-report/`.

The final Phase 8 baseline passed 237 backend tests, 69 frontend tests, all
format/lint/type/migration/contract/isolation/build gates, and four Chromium
workflow scenarios. The browser baseline checks 360, 768, 1024, and 1440 px.
During baseline development, the deployed browser run exposed and then verified
fixes for a server/client module-boundary error and two ambiguous accessibility
locators. A host production-build attempt while the mounted Learn development
server was running also failed from competing `.next` writers; the test-only
script now refuses that state. No final gate was skipped.
