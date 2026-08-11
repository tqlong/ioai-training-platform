# Release 0 Phase 8.1 manual assessment checklist

Use a fresh browser profile at 360, 768, 1024, and 1440 px. Start PostgreSQL,
the API, Learn on port 3000, and Studio on port 3001. Record failures with the
route, viewport, request ID, and console/network evidence.

## Author rubric

- [ ] Create or edit a problem and select `RUBRIC_HUMAN`.
- [ ] Confirm a structured rubric appears instead of a generic configuration.
- [ ] Add multiple criteria and verify stable IDs, English text, maximum points,
  zero/max performance levels, optional guidance, and exemplar inputs persist.
- [ ] Confirm Vietnamese rubric text may remain pending.
- [ ] Confirm invalid/missing levels, duplicate IDs/points, weight total other
  than `1.0`, and pass thresholds outside `0`–`1` block validation/publication.
- [ ] Set a non-default threshold, publish, then edit a successor revision and
  confirm the public snapshot remains unchanged.

## Learner submission

- [ ] Submit a human-scored answer and see “Pending assessment” without a pass,
  completion, or learning-evidence claim.
- [ ] Submit a mixed automated/human problem and confirm the request completes
  once without exposing hidden answers or private rubric guidance.
- [ ] Open `/submissions`; confirm the problem, pending status, time, and link
  are present only on this device.
- [ ] Open the result link; confirm the submitted answer is visible and the
  private receipt is absent from the URL, page, logs, and network response.
- [ ] Copy the result URL to a clean browser and confirm the uniform unavailable
  state does not disclose whether the attempt exists.
- [ ] Disable or corrupt local storage and confirm submission still works with a
  clear limitation and no server-side identity fallback.

## Studio assessment

- [ ] Open `/author/assessments`; confirm Pending is oldest-first and Assessed
  history is distinct from editorial review.
- [ ] Open an assessment and verify the exact submitted answer and published
  snapshot rubric are shown.
- [ ] Confirm completion is disabled until every criterion has one level.
- [ ] Complete an assessment without comments and verify it succeeds.
- [ ] Confirm the final weighted score uses stored automated results and the
  published threshold; automated evaluation must not rerun.
- [ ] Open the learner result and confirm criterion labels, selected levels,
  points, optional feedback, total score, and pass status are learner-safe.
- [ ] Confirm passed results update local task status to `COMPLETED`; failed
  results remain `ATTEMPTED`; no screen says `MASTERED`.

## Corrections, isolation, and accessibility

- [ ] Correct an assessment; require a reason and confirm the original decision
  remains in history.
- [ ] Submit two concurrent corrections and confirm the stale one is rejected
  with a recoverable conflict message.
- [ ] Publish a new problem revision after submission and confirm pending and
  completed assessments still use the original snapshot rubric and threshold.
- [ ] Verify keyboard order, visible focus, labels, radio grouping, status text,
  and 200% zoom on queue, assessment detail, history, and learner result pages.
- [ ] Confirm mobile layouts do not force desktop tables or horizontal page
  scrolling and status is never communicated by color alone.

## Quality evidence

- [x] Migration upgrades a clean database and downgrades safely.
- [x] Legacy published `RUBRIC_HUMAN` snapshots and unresolved legacy attempts
  are zero before rollout; no published snapshot was rewritten automatically.
  Run `PYTHONPATH=backend/src uv run python scripts/manual_assessment_preflight.py`
  with `IOAI_DATABASE_URL` set to the target database.
- [x] Backend tests, Ruff, Pyright, frontend lint/type/tests/build, OpenAPI drift,
  affected Playwright flows, and Compose smoke checks pass or exact limitations
  are recorded.

Automated baseline recorded on 2026-08-11: 245 backend tests passed; Ruff,
Pyright, frontend lint/type/unit tests, production builds, and OpenAPI/client
drift checks passed. The redeployment applied the migration and seed, reported
zero rollout-blocking legacy snapshots or attempts, and passed API, Learn,
Studio, submission-history, and assessment-queue health checks. The focused
Chromium workflow passed all 6 tests. The preflight also reported 20 preserved
historical snapshots whose slugs use the reserved `learner-e2e-*` fixture
prefix; they are excluded from rollout data and were not rewritten or deleted.

The interaction checks above intentionally remain unchecked until a person
verifies them at every listed viewport.
