# Release 0 Phase 7 manual verification

This checklist verifies the completed **Phase 7 — Editorial review and
publication** slice (`R0-07001` through `R0-07014`). It covers editorial
transitions, audit history, learner-format preview, approval, atomic
publication, stable URLs, successor revisions, archive behavior, and strict
separation between author revisions and published snapshots.

Phase 7 does not implement the Phase 8 learner problem-detail experience. A
successful publication returns and displays the permanent path
`/problems/{slug}`, but rendering the complete public problem page belongs to
Phase 8. Do not report a missing learner detail page as a Phase 7 failure.

## 1. Test record and prerequisites

Record these values before testing:

```text
Tester:
Date/time:
Commit:
Host/OS:
Browser/version:
```

Prerequisites:

- Docker and Docker Compose are installed.
- Ports `5432`, `8000`, `3000`, and `3001` are available.
- Commands run from the repository root.
- Use a current Chromium, Firefox, or Safari browser with developer tools.
- Use a disposable local database, or back up valuable drafts before running
  migration/integration gates.

## 2. Redeploy and verify the complete stack

Redeploy PostgreSQL, migrations, vocabulary, API, learner app, and Studio:

```bash
bash scripts/dev_redeploy.sh
docker compose ps
bash scripts/dev_health.sh
```

Expected:

- [x] `postgres`, `api`, `learn`, and `studio` are healthy.
- [x] Migration `20260809_07002` or a later repository head is applied.
- [x] Canonical vocabulary synchronization finishes without rejection.
- [x] <http://127.0.0.1:3000/problems> opens as **IOAI Learn**.
- [x] <http://127.0.0.1:3001/author/problems> opens as **IOAI Studio**.
- [x] Studio remains bound to host loopback by default; its separate port is
      not presented as authentication or production security.

## 3. Prepare one publication-eligible draft

Open <http://127.0.0.1:3001/author/problems>, select **Create problem**, and
complete a small problem. A convenient valid example is:

- Slug: a unique value such as `manual-p7-YYYYMMDD-HHMM`.
- English/Vietnamese title and summary: complete.
- Objective: use an observable verb, for example **Calculate precision from a
  confusion matrix.**
- At least one problem-statement block in both languages.
- Stage: **AI Foundations**.
- Difficulty: **Easy**.
- Primary competency: **Metrics**.
- Task type: **Single-answer Quiz**.
- Topic: a leaf topic such as **Confusion Matrix**.
- Data modality and compute tier: **None**.
- Runtime: **Instant**, network: **Denied**, numeric resource limits: `0`.
- Expected minutes: a positive integer such as `15`.
- Two quiz choices with exactly one correct answer.
- One `EXACT_MATCH` scoring component with weight `1.0`.

Save and reload the editor.

- [ ] Problem ID and revision ID are distinct and visible only in Studio.
- [ ] Editorial status is visibly **Draft**/`DRAFT`, not learner task status.
- [ ] The saved version increments and the data survives reload.
- [ ] The draft does not appear in IOAI Learn.
- [ ] Save, Validate, Preview, and editorial actions remain separate controls.

Keep the problem ID, revision ID, current version, and slug in the test record.

If the problem already has multiple revisions, verify the Studio list:

- [ ] Shows one row for the stable problem identity by default.
- [ ] The collapsed row contains the latest revision, status, validation, and
      last-saved values.
- [ ] **Show all N revisions** reports the correct total and expands exactly N
      rows for that problem.
- [ ] **Hide revision history** restores the single latest row.
- [ ] Expanded historical rows retain their own status and validation result.

## 4. Verify validation blocks review (`R0-07003`)

1. Make one saved draft invalid, such as setting scoring weights below `1.0`.
2. Select **Validate draft**.
3. Attempt to submit the revision for review.

Expected:

- [ ] Validation reports a field-addressable blocker under the correct group.
- [ ] Focus moves deterministically to the first blocker or its issue link.
- [ ] The revision stays `DRAFT`; no `IN_REVIEW` history entry is created.
- [ ] A missing editorial note disables or rejects the transition.
- [ ] Errors include text/icon cues and do not rely on color alone.

Restore valid scoring, save, and validate again.

- [ ] **Eligible for publication** is visible.
- [ ] Validation does not itself submit, approve, or publish the revision.

## 5. Verify unsaved learner preview (`R0-07005`, `R0-07006`)

1. Change the English title but do not select **Save draft**.
2. Immediately select **Preview as learner**.

Expected:

- [ ] The preview shows the unsaved title, including after a cold route load.
- [ ] A persistent **Draft preview - not public** banner is visible.
- [ ] The page uses learner-style content and labels, not raw editor fields.
- [ ] **Desktop width** is initially selected.
- [ ] **Mobile width** changes the preview frame without opening a public URL.
- [ ] **Open public problem** and continuation controls are disabled before
      publication.
- [ ] Pending translations appear only as author preview warnings.
- [ ] No answer key, hidden tests, editorial note, revision ID, validation
      internals, or object-storage metadata appears in learner content.
- [ ] Previewing does not race autosave into a stale-version error.

Return to the editor. Save or discard the temporary title change, then validate
the current saved version again before continuing.

## 6. Submit for review and inspect history (`R0-07003`, `R0-07004`)

1. Enter a meaningful editorial note such as `Ready for editorial review.`
2. Select **Submit for review**.

Expected:

- [ ] The visible status changes from **Draft** to **In review**.
- [ ] Editing and draft-save controls cannot silently change the submitted
      revision.
- [ ] Editorial history shows `DRAFT -> IN_REVIEW`, the exact note, actor
      context, and timestamp.
- [ ] History is ordered and visually separate from learner task status and
      learning evidence.
- [ ] Reloading preserves the status and immutable history record.

## 7. Request changes and create a successor draft (`R0-07003`, `R0-07009`)

1. Enter `Clarify the learner explanation.` as the review note.
2. Select **Request changes**.
3. Return to `/author/problems` and locate the same problem ID.
4. Select **Address changes**.

Expected:

- [ ] Status changes to **Changes requested**.
- [ ] History adds `IN_REVIEW -> CHANGES_REQUESTED` with the required note and
      timestamp; the earlier entry remains unchanged.
- [ ] **Address changes** creates a new revision in `DRAFT` rather than making
      the reviewed revision editable.
- [ ] The successor has a new revision ID and next revision number/version.
- [ ] Content, canonical metadata, response, scoring, resources, problem ID,
      and slug are copied accurately.
- [ ] Refreshing or retrying does not create competing duplicate-current
      drafts.

Make a small meaningful revision, save it, validate it, enter a new note, and
select **Submit for review**.

## 8. Approve without publishing (`R0-07003`, `R0-07004`)

1. On the resubmitted revision, enter `Content and scoring checked.`.
2. Select **Approve**.

Expected:

- [ ] Status changes from **In review** to **Approved**.
- [ ] Approval requires a non-empty note and current valid revision.
- [ ] History includes the approval decision with timestamp and note.
- [ ] The problem is still absent from public eligibility.
- [ ] Approval does not create a public snapshot or imply publication.
- [ ] **Publish** appears only for the approved eligible revision.

## 9. Verify the publication confirmation (`R0-07007`, `R0-07008`)

1. Activate **Publish** with the keyboard.
2. Inspect the confirmation dialog without confirming yet.

Expected:

- [ ] The dialog is named **Publish approved revision**.
- [ ] It clearly shows the permanent path `/problems/{slug}`.
- [ ] Copy distinguishes the permanent public URL from author Preview.
- [ ] A publication note is required.
- [ ] Focus enters and remains within the dialog while it is open.
- [ ] Escape closes the dialog when no submission is in progress.
- [ ] Closing returns focus to the **Publish** trigger.
- [ ] Reopen the dialog; duplicate confirmation cannot be submitted while the
      first request is pending.

Enter `Publish reviewed pilot content.` and confirm.

- [ ] Status becomes **Published**.
- [ ] The result shows a link whose `href` is exactly `/problems/{slug}`.
- [ ] History includes the publish transition and note.
- [ ] Save, approval, and publication remain visibly distinct actions.

Phase 8 owns the full learner detail page, so only the stable path and published
projection are Phase 7 acceptance targets.

## 10. Verify stable publication and retry safety (`R0-07007`, `R0-07008`)

Use browser developer tools to inspect the successful publish request and
response, or inspect the endpoint at <http://127.0.0.1:8000/docs>.

- [ ] The request includes current `expected_version`, a required note, and an
      operation/idempotency key.
- [ ] The response includes the stable slug, `/problems/{slug}`, publication
      time, and snapshot reference without leaking draft content.
- [ ] Replaying the same request and operation key returns the original logical
      publication instead of creating a second snapshot/history event.
- [ ] Reusing the key with changed publication intent returns a stable conflict.
- [ ] A stale expected version or invalid transition returns a stable 409-style
      error and changes no state.
- [ ] No response exposes SQL, stack traces, provider errors, secrets, or object
      keys.

Do not invent request fields manually; copy the canonical schema and captured
payload from OpenAPI/browser tools.

## 11. Edit a published problem without changing its snapshot (`R0-07009`)

1. Return to the Studio problem list.
2. Start an edit/revision for the published problem.
3. Change a learner-visible title or statement in the new draft and save it.
4. Preview the draft, but do not approve or publish it.

Expected:

- [ ] A new `DRAFT` revision is created with a new revision identity.
- [ ] The stable problem identity and slug are retained.
- [ ] The new content appears in author preview only.
- [ ] The current published snapshot remains unchanged and eligible.
- [ ] Draft, in-review, changes-requested, and approved revisions never replace
      the public snapshot.
- [ ] Publishing the successor only after the normal validate/review/approve
      flow replaces the current snapshot while preserving the same URL.

If you publish the successor to test replacement, verify its status/history and
that the permanent path is identical to the first publication.

## 12. Verify archive behavior (`R0-07010`)

1. Locate the currently published row and activate **Archive**.
2. Inspect the **Archive published problem** confirmation.
3. Attempt to confirm with an empty note, then enter
   `Archive after manual verification.` and confirm.

Expected:

- [ ] Empty archive notes are disabled or rejected.
- [ ] The dialog is keyboard operable, closes safely, and returns focus.
- [ ] Status becomes **Archived** with a visible text label.
- [ ] History records `PUBLISHED -> ARCHIVED`, timestamp, actor context, and
      exact note without deleting earlier history.
- [ ] The current public pointer/eligibility is removed atomically.
- [ ] The historical snapshot and slug remain internally preserved.
- [ ] Retrying archive does not create duplicate successful transitions.
- [ ] Archived content cannot be silently reactivated; republication requires
      a new revision through validation, review, approval, and publish.

## 13. Verify public/draft isolation (`R0-07011`, `R0-07012`)

Keep both Studio and IOAI Learn open while exercising the workflow.

- [ ] Draft, in-review, changes-requested, approved, superseded, and archived
      revisions never appear as public candidates.
- [ ] Guessing a problem ID, revision ID, or preview identifier on a public
      route does not return unpublished content.
- [ ] Public responses contain stable learner content only—no revision IDs,
      editorial notes/history, validation results, answer keys, hidden tests,
      internal scoring configuration, object metadata, or unavailable
      translations.
- [ ] Preview state is not reachable through a public query parameter, slug,
      cache, recommendation source, or production learner bundle.
- [ ] Archived problems are absent from current published eligibility.
- [ ] Author routes can still retrieve the complete history after archive.

Run the static cross-layer check:

```bash
bash scripts/public_isolation_check.sh
```

- [ ] The learner production build completes.
- [ ] The script reports no known author-only markers in the learner bundle.

## 14. Concurrency and rollback spot checks

### Stale editorial command

1. Open the same reviewable revision in two tabs.
2. Apply a valid transition in tab A.
3. Attempt a different transition from stale tab B.

- [ ] Tab B receives a stable conflict rather than overwriting tab A.
- [ ] Only one accepted transition/history row exists.

### Slug conflict

1. Prepare two otherwise eligible approved problems with the same desired
   slug, if the UI permits the setup safely.
2. Publish the first, then attempt to publish the second.

- [ ] The second returns `SLUG_CONFLICT` or equivalent safe UI feedback.
- [ ] No partial snapshot, public pointer, or `PUBLISHED` history entry is
      created for the rejected problem.
- [ ] The first published problem remains unchanged.

Injected transaction failures and simultaneous publish races are primarily
automated PostgreSQL checks; do not manipulate the database manually to create
them.

## 15. Accessibility and responsive checks

Inspect Studio and Preview at widths `360`, `768`, `1024`, and `1440` px, and
at 200% browser zoom.

- [ ] Editorial status always has visible text and never relies on color alone.
- [ ] Required notes have visible labels.
- [ ] Keyboard-only navigation reaches validation issues, Preview, editorial
      notes/actions, publish/archive dialogs, and history.
- [ ] Focus indicators remain visible.
- [ ] Dialog focus is deterministic, trapped while open, restored on close,
      and not lost after validation errors.
- [ ] Desktop/mobile preview width controls have accessible pressed states.
- [ ] No required content or action becomes unreachable at supported widths or
      200% zoom.
- [ ] The striped non-public preview banner remains prominent at every width.

## 16. Automated corroboration

Manual verification does not replace automated gates. The complete Phase 7
command stops API/frontend development services during production builds,
runs all backend/frontend, migration, drift, isolation, and build gates, then
redeploys and runs the Chromium editorial workflow:

> **Database safety:** `phase7_quality.sh` delegates pytest to the isolated
> `postgres-test` service and `ioai_test` database on port `5433`. Integration
> tests refuse the development `ioai` database. A backup remains prudent for
> local operational recovery but is no longer required to protect drafts from
> the test suite.

```bash
bash scripts/db_backup_restore.sh backup  # when local data must be preserved
bash scripts/phase7_quality.sh
```

Expected:

- [ ] Ruff formatting/linting and Pyright pass.
- [ ] All pytest unit and PostgreSQL integration tests pass.
- [ ] ESLint, strict TypeScript, frontend unit/component tests, and both Next.js
      production builds pass.
- [ ] Vocabulary, OpenAPI/generated-client, and Alembic-head checks pass.
- [ ] Public isolation scan passes.
- [ ] PostgreSQL, migrations, API, Learn, and Studio redeploy healthy.
- [ ] The focused Chromium workflow passes after redeployment.
- [ ] Every skipped or failing gate is recorded; Phase 7 is not accepted while
      a required result is unknown.

For only the browser workflow against an already healthy stack:

```bash
bash scripts/test_editorial_e2e.sh
```

## 17. Final result record

```text
Stack, migration, and health:             PASS / FAIL
Eligible draft and validation blocking:   PASS / FAIL
Unsaved responsive preview:               PASS / FAIL
Submit and audit history:                  PASS / FAIL
Request changes and successor revision:   PASS / FAIL
Approval remains non-public:              PASS / FAIL
Publish confirmation and stable URL:       PASS / FAIL
Idempotency and safe errors:               PASS / FAIL
Published revision isolation:              PASS / FAIL
Archive and explicit republication:        PASS / FAIL
Public/draft isolation:                    PASS / FAIL
Concurrency and rollback spot checks:      PASS / FAIL / AUTOMATED ONLY
Accessibility and responsive behavior:     PASS / FAIL
Automated corroboration:                   PASS / FAIL / NOT RUN

Defects found:

Evidence (screenshots, request IDs, logs, traces):

Overall Phase 7 result:                    PASS / FAIL
```
