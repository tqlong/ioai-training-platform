# Release 0 Phase 8 manual verification

This checklist verifies **Phase 8 — Learner problem library and solving loop**
(`R0-08001` through `R0-08018`). It covers published-only discovery, URL-owned
filters, responsive results, permanent problem pages, all five Release 0
response families, safe assessment feedback, device-local progress, anonymous
problem feedback, and continuation to one recommended next problem.

Use this checklist to find and record bugs. Do not mark an item passed merely
because the automated suite covers it. For each failure, record the exact URL,
viewport, input, expected result, actual result, screenshot, console error, and
request/response details without copying secrets.

Phase 8 does not add accounts, authentication, server-saved learner progress,
advanced code execution, GPU workloads, hosted notebooks, leaderboards, or
personalized mastery. Do not report their absence as a Phase 8 defect.

## 1. Test record and prerequisites

```text
Tester: Nguyen Hoang Cong
Date/time: 2026-09-08 22:49 (GMT +7)
Commit: b8e43cfd8474b7fe0ab8d8f9da2d0666e1085b3a
Host/OS: Windows 11
Browser/version: Chrome
Primary viewport: 1920x1200
Database/data set:
```

Prerequisites:

- Docker and Docker Compose are installed.
- Ports `5432`, `8000`, `3000`, and `3001` are available.
- Commands run from the repository root.
- Use a current Chromium, Firefox, or Safari browser with developer tools.
- Use disposable pilot content or back up valuable local data first.
- Keep the browser console and Network panel open while reproducing failures.

## 2. Redeploy and verify the stack

Redeploy without deleting the PostgreSQL volume:

```bash
bash scripts/phase8_redeploy.sh
docker compose ps
```

Expected:

- [x] `postgres`, `api`, `learn`, and `studio` are healthy.
- [x] Migrations and canonical vocabulary synchronization complete.
- [x] <http://127.0.0.1:8000/health/live> and
      <http://127.0.0.1:8000/health/ready> return healthy responses. The local
      runtime does not expose interactive Swagger at `/docs`; use the committed
      `backend/generated/openapi.json` and browser Network panel to inspect the
      public `/api/v1` contracts.
- [x] <http://127.0.0.1:3000/problems> opens as **IOAI Learn**.
- [x] <http://127.0.0.1:3001/author/problems> opens as **IOAI Studio**.
- [x] Learn does not show stack traces, draft identifiers, object keys, or
      infrastructure details in the page or browser console.

## 3. Prepare representative published content

The strongest manual pass uses at least six published AI Foundations problems:

1. Single-choice quiz (`QUIZ_SINGLE`) with at least three topics.
2. Multiple-choice quiz (`QUIZ_MULTIPLE`).
3. Numeric answer (`NUMERIC_ANSWER`) with tolerance and optional unit.
4. Short answer (`SHORT_ANSWER`) using human-rubric assessment.
5. Python function (`CODE_FUNCTION`) using human-rubric assessment.
6. A second eligible next problem in the same stage and learning path.

Also retain one draft-only problem and, if practical, one archived problem.
Give the published problems distinct titles, expected times, difficulties, and
topics so sorting and filtering are observable. Include searchable English and
Vietnamese text or an approved alias in at least one item.

Create, validate, review, approve, and publish these in Studio using the Phase 7
workflow. Record the public slugs:

```text
Single-choice slug:
Multiple-choice slug:
Numeric slug:
Short-answer slug:
Code-function slug:
Continuation slug:
Draft-only slug:
Archived slug:
```

Optional setup shortcut: the focused browser suite creates uniquely named
published fixtures for all five response families. It also executes tests and
anonymous feedback requests, so use it only against disposable local data:

```bash
bash scripts/test_learner_e2e.sh
```

- [x] Every published slug appears in the public library.
- [x] Draft-only, unapproved, and archived-only slugs do not appear.
- [x] Refreshing the library does not change publication eligibility.

## 4. First viewport, product identity, and stage selector

Open <http://127.0.0.1:3000/problems> in a fresh browser profile.

- [x] The header says **IOAI Learn**, not IOAI Studio.
- [x] The first desktop viewport includes stage selection, one recommendation,
      and the beginning of the problem list without a large marketing hero.
- [x] Stages appear in canonical curriculum order: AI Foundations, Competition
      Foundations, High-school Competition, Collegiate Competition, and Open.
- [x] AI Foundations and Competition Foundations are selectable.
- [x] Later stages are disabled and visibly explained as **Coming next**.
- [x] Disabled stages cannot be selected with mouse, keyboard, touch, or a
      hand-edited query string.
- [x] Choosing an enabled stage changes both results and recommendation.
- [x] The selected stage remains visibly selected and appears canonically in
      the URL query string.
      __SUGGESTION__: Use better visual effect for selected stage.
- [x] Browser Back and Forward restore the previous stage and results.
- [x] Statuses and disabled states use visible text, not color alone.

## 5. Search, filters, hierarchy, and shareable URL state

Exercise each filter separately, then combine several filters.

- [x] Search matches a published English title or objective.
- [x] Search matches supported Vietnamese text.
- [x] Search matches an approved alias where fixture content permits it.
- [x] Search does not return draft, unapproved, superseded, or archived-only
      content.
- [x] The compact desktop filter row includes Search, Stage, Topic, Difficulty,
      Type, More filters, and Clear.
- [x] Exactly the eight top-level topic families are shown as shortcuts; the
      full topic vocabulary is not rendered as a flat chip cloud.
- [x] The topic picker is searchable and shows family, intermediate, and leaf
      hierarchy rather than relying on Markdown heading position.
- [x] Selecting a parent topic without **Include subtopics** does not silently
      include descendants.
- [x] Enabling **Include subtopics** includes matching descendants explicitly.
- [x] Stage, competency, topic, difficulty, task type, task status, learning
      evidence, time, and compute filters produce appropriately scoped results.
- [x] Active filters appear as individually removable tokens.
- [x] Removing one token preserves the other active filters.
- [x] **Clear filters** removes active filter state and restores results.
- [x] Search/filter selections use canonical codes in the URL where applicable,
      not translated labels or unpublished identifiers.
- [x] Copying the URL into a fresh tab reproduces the same discovery state.
- [x] Back/Forward changes the visible controls and result list consistently.
- [x] Unknown, malformed, duplicated, or unavailable query values are rejected
      or normalized safely; they never broaden access to private content.

Create a combination that returns no matches.

- [x] The empty state says active filters caused no matching results.
- [x] It offers a working **Clear filters** action.
- [x] Clearing restores published results without a full broken-page state.

## 6. Sorting, count, and pagination

- [x] The default order follows editorial learning-path order, then difficulty.
- [x] **Newest** sort is deterministic across refreshes.
- [x] **Expected time** sort orders by exact minutes.
- [x] **Title** sort is deterministic and understandable.
- [x] The selected sort is stored in the URL.
- [x] The result count agrees with the visible filtered data.
- [ ] Pagination controls are explicit when enough content exists.
TODO: Add page manager to show all problems.
- [x] Moving between pages updates the URL and does not duplicate or omit rows.
- [x] Changing a filter from a later page returns to a valid page.
- [x] Refresh, Back, and Forward preserve the expected sort/page state.

## 7. Desktop and tablet problem results

At `1440` px wide, inspect the dense table.

- [x] The table has an accessible name and a sticky header on a long list.
- [x] Every row shows task status and learning evidence as separate fields.
- [x] A new problem shows `NOT_STARTED`/Not started and `—` when no evidence
      exists; it never shows `MASTERED`.
- [x] Every row shows title, permanent short ID, one-line objective, stage and
      difficulty together, primary competency, task type, exact minutes, and
      compute tier.
- [x] No more than two topic chips are visible.
- [x] A problem with additional topics shows an accessible `+N` disclosure with
      the correct remaining labels.
- [x] Clicking the title opens the permanent problem URL.
- [x] Clicking a non-interactive part of the row opens the same URL.
- [x] Using a disclosure or nested control does not accidentally navigate.
- [ ] Hover, keyboard focus, and selected states remain distinguishable.
TODO: Add effect for mouse hover state.

At `1024` and `1279` px wide:

- [x] Results remain a table, not mobile cards.
- [x] Competency/evidence hidden from the main row remain available through row
      details rather than disappearing.
- [x] The learning-path sidebar moves below the recommendation as specified.
- [x] Meaningful metadata remains readable before decorative content.

At exactly `768` px wide:

- [x] Results still use the table breakpoint.
- [x] No required action is clipped or unreachable.

## 8. Mobile cards and filter sheet

At `360` px wide and again at `767` px:

- [x] The desktop table is replaced by a list of compact problem cards.
- [x] Each card retains title, task status, stage and difficulty together,
      primary topic, task type, and expected minutes.
- [x] Cards do not horizontally overflow the viewport.
- [x] **Open filters** opens a full-height sheet.
- [ ] The sheet has an accessible name and visible field labels.
TODO: Add accessible name for this sheet.
- [ ] Keyboard focus enters the sheet and remains inside it while open.
TODO: Trap keyboard focus inside this sheet.
- [ ] Escape closes the sheet when safe and returns focus to **Open filters**.
TODO: Add escape button handler.

- [x] Touch targets are usable without accidental adjacent activation.
- [x] The primary action says **Show N problems** with the current result count.
- [x] Applying filters closes the sheet and updates cards and URL.
- [x] Reopening the sheet restores the active selections.

__CRITICAL__: Fix "More filter" panel can't be closed on sheet close and add
collapse button for this panel.

## 9. Recommendation and learning-path guidance

First clear site data and select an enabled stage.

- [x] Exactly one feature card is labeled **Recommended start**.
- [x] It uses the editorially first eligible published problem for the selected
      stage and does not claim personalization or mastery.
- [x] **Why this?** exposes a plain-language reason and is keyboard operable.
- [x] The recommendation never points to the current, draft-only, archived,
      unavailable-stage, or unsupported-task problem.
- [x] Weekly goal does not present zero history as failure.
- [x] Current path, prerequisites to review, recently completed, and suggested
      topics remain supportive and bounded.
- [x] Recently completed contains no more than three problems.
- [x] Suggested next topics contains no more than two topics.

After attempting/completing problems in the same stage:

- [x] Changing stage scopes the recommendation to the selected stage.
- [x] Reload restores the recommendation context without an account.

## 10. Permanent problem URL and published content

Open each recorded slug directly in a fresh tab, without visiting the list.

- [x] `/problems/{slug}` loads the same published problem directly.
- [x] The title, stage and difficulty together, observable objective,
      prerequisites, statement, provided information/examples, constraints,
      response area, and available hints/explanation follow learner reading
      order.
- [x] Taxonomy metadata does not dominate the main task content.
- [x] Resource and response instructions match the published task.
- [x] Hint and explanation disclosures are keyboard operable and expose only
      content allowed by the published snapshot.
- [x] No **Draft preview — not public** banner or author translation warning is
      present on a public page.
- [x] No revision ID, editorial status/history, validation result, answer key,
      hidden test, scoring configuration, object key, or draft content appears
      in the page source or public API response.
- [x] A valid `return_to` link returns to the prior filtered library URL.
- [x] An absent or unsafe `return_to` value falls back safely to `/problems`.
- [x] A guessed missing, draft-only, unapproved, or archived-only slug shows the
      same safe **Problem unavailable** behavior.

If practical, create and save a successor draft for a published problem.

- [x] The permanent URL continues to show the old published snapshot.
- [x] After the successor passes review and is published, the same URL shows the
      new snapshot; the URL itself does not change.

## 11. Response validation for all five task families

For every form, first submit an empty or malformed response.

- [x] The invalid response remains editable.
- [x] A visible, field-addressable message explains how to correct it.
- [ ] Focus moves predictably to the error or invalid input.
TODO: Add focus function to the first error field.
- [x] No result claims completion, and no unsafe implementation detail appears.

### Single-choice quiz

- [x] Choices are one keyboard-operable radio group with visible labels.
- [x] Only one choice can be selected.
- [x] Selecting and changing a choice works before submission.

### Multiple-choice quiz

- [x] Choices are keyboard-operable checkboxes with visible labels.
- [x] One or more choices can be selected and deselected.
- [x] Empty selection is rejected with actionable guidance.

### Numeric answer

- [x] The numeric input has a visible label and tolerance/unit guidance.
- [x] Non-finite or malformed input is rejected while remaining editable.
- [x] A valid decimal near a configured tolerance boundary is assessed
      consistently.

### Short answer

- [ ] The bounded text input has a visible label and limit guidance.
TODO: Add limit guidance (e.g.: Up to 20000 characters).
- [x] Oversized input is blocked or rejected safely.
- [x] The human-rubric path reports pending assessment rather than completion.

### Python function

- [ ] Language, signature, starter code, public examples, and allowed limits are
      visible without exposing hidden tests.
TODO: Add limit guidance (e.g.: Up to 20000 characters).
- [x] The code field has an accessible name and retains multiline input.
- [x] Oversized/empty code is rejected safely and remains editable.
- [x] The human-rubric path reports pending assessment rather than pretending
      to execute an advanced judge.
- [x] The form never requests GPU, distributed, or hosted-notebook resources.

## 12. Submission results, retry safety, and privacy

Submit a correct and an incorrect automated answer where fixture data allows.

- [x] The submit button prevents accidental duplicate requests while pending.
- [x] An accepted assessment shows outcome, score/rubric summary, and actionable
      component feedback.
- [x] Decimal scores are stable and understandable (for example, exact correct
      work scores `1.0`).
- [x] Incorrect feedback does not reveal the answer key, hidden tests, or
      unpublished explanation.
- [x] A pending human assessment does not grant `COMPLETED` or learning evidence.
- [x] The answer remains visible/editable after a safe validation or dependency
      failure.
- [x] Retrying a failed request uses the same logical submission and does not
      create duplicated visible outcomes.
- [x] Refreshing during/after submission does not expose an internal error.

In developer tools, temporarily block the submission request and submit again.

- [x] A safe message says the answer could not be assessed and offers retry.
- [x] The learner's entered response is retained.
- [x] The error contains no provider, database, stack, snapshot, or revision
      details.

## 13. Device-local anonymous progress

Clear site data, open a published problem, then return to the library.

- [x] Opening a problem records approved local context without an account.
- [x] A valid submission changes task status monotonically to `ATTEMPTED` or
      `COMPLETED` according to its outcome.
- [x] Task status and learning evidence remain separate; neither is presented
      as `MASTERED`.
- [x] Refresh and browser restart restore status, available evidence, recent
      history, and recommendation context on the same device.
- [x] The library overlay agrees with the detail page.
- [x] Inspecting local storage shows no answer/response text, credentials,
      identity claim, draft content, editorial status, hidden test, or author
      data.
- [x] Local records are bounded rather than growing without limit.
- [x] Clearing site data resets progress without affecting published content or
      server availability.

Corrupt `ioai.learn.progress.v1` in developer tools, then reload.

- [x] Corrupt progress is discarded safely; the library and solving loop work.
- [x] No corrupt payload is rendered into the page or error message.

Disable/block local storage and reload a problem.

- [x] Browsing and submission remain usable.
- [x] A clear notice explains that progress is temporary on this device.
- [x] The notice does not expose stored content or imply an account failure.
      __SUGGESTION__: Add warning when opening a problem.

## 14. Problem feedback dialog and abuse behavior

On every public problem family, confirm **Report a problem** is available. Open
the dialog with the keyboard.

- [x] Focus enters the named feedback dialog and lands predictably.
- [x] Category and Message have visible labels.
- [x] Only approved feedback categories are offered.
- [x] No account, name, email, or identity is required.
- [x] Empty and oversized messages produce safe actionable validation.
      __SUGGESTION__: Add disabled style for "Send feedback" button.
- [x] Invalid input remains editable and is not reported as success.
- [x] Escape closes safely and returns focus to **Report a problem**.
- [x] Focus remains trapped inside the dialog while it is open.
- [x] A valid bounded report shows a clear success receipt.
- [x] Retrying the same failed logical report does not create multiple success
      confirmations.
      __SUGGESTION__: Close form immediately or disable form once submitted.

Submit valid reports repeatedly from disposable local data until the anonymous
limit is reached.

- [x] Excess requests receive a bounded rate-limit message.
- [x] The message reveals no moderation state, stored feedback, snapshot ID,
      internal counter, or infrastructure detail.
- [x] Rate limiting feedback does not break browsing or solving.

## 15. Complete and continue

Complete an automatically assessed problem with another eligible published
problem available in the selected stage.

- [x] Exactly one **Continue to …** recommendation appears after completion.
- [x] It does not appear as a completed recommendation for pending assessment.
- [x] The next item is not the current problem when an alternative exists.
- [x] Its link is a permanent `/problems/{slug}` URL.
- [ ] Opening it preserves the selected-stage/list return context.
TODO: Preserve filter parameters when opening recommended problem.
- [x] It never points to a draft, archived-only revision, unavailable stage, or
      unsupported Release 0 task.
- [ ] Returning to the library restores filters and the prior list position as
      closely as browser navigation permits.
TODO: Preserve filter parameters when opening recommended problem.
- [x] The local continuation measure is bounded and stores no identity.

## 16. Loading, dependency failure, and safe errors

Use developer-tool throttling to observe loading states, then block the public
problem-list request.

- [x] Loading retains the page/table or card dimensions without a large layout
      shift.
- [x] A list failure shows a safe retry action and feedback path.
- [x] Retry succeeds after unblocking the request.
- [x] The failure view exposes no drafts, SQL, stack trace, provider error,
      object key, internal ID, or private network detail.

Repeat for a problem-detail request.

- [x] Detail loading and unavailable states are distinct and understandable.
- [x] Retrying a temporary failure does not turn a private slug into public
      content or leak whether an unpublished revision exists.

__CRITICAL__: Fix frozen "Try again" button.

## 17. Keyboard, screen-reader, zoom, and responsive pass

Repeat the core browse -> filter -> open -> answer -> feedback -> continue flow
at `360`, `768`, `1024`, and `1440` px and at 200% browser zoom.

- [ ] A visible skip link or equivalent structure supports efficient navigation. 
TODO: Add 'skip to content' link when user press 'tab' button.
- [x] Headings and landmarks describe page hierarchy in a sensible order.
- [ ] All controls have accessible names and visible focus indicators.
TODO: Add focus indicator for "Open filter" button.
- [x] Filters, topic disclosures, row details, hints, explanations, response
      forms, feedback dialog, and continuation work using keyboard only.
- [ ] Dialog/sheet focus is trapped, Escape behavior is safe, and focus returns
      to the trigger.
TODO: Add Escape button handler and trap focus in filter dialog.
- [x] Status, evidence, errors, success, pending state, and disabled state never
      rely on color alone.
- [x] Text and controls remain readable at 200% zoom.
- [x] No required content, feedback action, submit action, or navigation becomes
      clipped, overlapped, or unreachable.
- [x] Touch interactions at mobile width do not trigger unintended row/card
      navigation.

## 18. Public/draft isolation spot check

Keep Studio and Learn open side by side while editing a published problem's
successor draft.

- [x] Unsaved and saved draft changes appear only in Studio Preview.
- [x] Learn list, detail, recommendation, submission, and feedback continue to
      use the current published snapshot.
- [x] Guessing problem IDs, revision IDs, preview identifiers, or query flags on
      public routes does not expose unpublished content.
- [ ] Public API responses never include editorial notes/history, answer keys,
      hidden tests, validation state, internal revision identity, or object
      metadata.
- [x] Archiving removes current public eligibility consistently from list,
      detail, recommendation, submission, and feedback.

Run the static cross-layer check:

```bash
bash scripts/public_isolation_check.sh
```

- [x] The learner production build completes.
- [x] No known author-only marker is found in the learner bundle.

## 19. Automated corroboration

Manual verification does not replace automated gates. Testing and deployment
are intentionally separate. Stop Learn and Studio before the production-build
gate to avoid competing `.next` writers.

```bash
docker compose stop learn studio
bash scripts/phase8_test.sh
bash scripts/phase8_redeploy.sh
bash scripts/test_learner_e2e.sh
```

Expected:

- [x] Ruff formatting/linting and Pyright pass.
- [x] Backend unit and isolated PostgreSQL integration tests pass.
- [x] Alembic migration and canonical vocabulary drift checks pass.
- [x] OpenAPI/generated-client agreement and public-isolation checks pass.
- [x] ESLint, strict TypeScript, Vitest/Testing Library, and both Next.js
      production builds pass.
- [x] The focused Chromium learner workflow passes after redeployment.
- [x] Browser coverage includes `360`, `768`, `1024`, and `1440` px.
- [x] Every skipped or failing gate is recorded; Phase 8 is not accepted while
      a required result is unknown.

## 20. Defect record template

Copy this block for every failure:

```text
Defect ID: P8-
Title:
Severity: blocker / high / medium / low
Checklist section/item:
Commit:
Browser and viewport:
Preconditions/data slug:
Exact URL:
Steps to reproduce:
Expected:
Actual:
Reproducibility: always / intermittent / once
Console error:
Network request/status/request ID:
Evidence path or screenshot:
Public/draft isolation risk: yes / no / unknown
Accessibility impact: yes / no / unknown
Notes:
```

Suggested severity:

- **Blocker:** draft/private data exposure, publication-boundary bypass, data
  corruption, or the primary learner loop cannot run.
- **High:** submission/scoring is wrong, permanent URL breaks, progress blocks
  solving, or a keyboard/screen-reader user cannot complete the loop.
- **Medium:** filtering, responsive behavior, retry, feedback, recommendation,
  or state restoration is materially incorrect but has a workaround.
- **Low:** visual/copy inconsistency that does not mislead or block the loop.

### Recorded Defects

```text
Defect ID: P8-001
Title: "Try again" button in error boundary does not re-fetch failed Server Component
Severity: medium
Checklist section/item: 16. Loading and safe failure behavior - "Retry succeeds after unblocking the request"
Commit: b8e43cf
Browser and viewport: Chrome, Desktop 1440x900
Preconditions/data slug: Backend FastAPI service temporarily stopped/blocked
Exact URL: http://localhost:3000/problems
Steps to reproduce:
1. Stop or block backend requests to trigger the error boundary.
2. Reload http://localhost:3000/problems to display the safe failure view.
3. Unblock or restart the backend service.
4. Click the "Try again" button in the failure view.
Expected: The page re-fetches the problem library from the server and restores the problem list.
Actual: The "Try again" button does not re-trigger SSR data fetching because reset() alone only re-renders the client tree in Next.js App Router.
Reproducibility: always
Console error: None
Network request/status/request ID: No outgoing RSC request triggered on click
Evidence path or screenshot: frontend/apps/learn/app/error.tsx:15
Public/draft isolation risk: no
Accessibility impact: yes
Notes: Fix using startTransition(() => { router.refresh(); reset(); }) in app/error.tsx.
```

```text
Defect ID: P8-002
Title: Missing pagination controls to browse problem library beyond default limit
Severity: medium
Checklist section/item: 6. Sorting, count, and pagination - "Pagination controls are explicit when enough content exists"
Commit: b8e43cf
Browser and viewport: Chrome, Desktop 1440x900
Preconditions/data slug: More problems published than the default page limit
Exact URL: http://localhost:3000/problems
Steps to reproduce:
1. Navigate to http://localhost:3000/problems.
2. Scroll to the bottom of the problem list table/cards.
Expected: Explicit pagination controls (Previous / Next / Page numbers) exist to navigate through all pages of problems.
Actual: No pagination controls are rendered at the bottom of the list.
Reproducibility: always
Console error: None
Network request/status/request ID: GET /api/v1/problems
Evidence path or screenshot: frontend/apps/learn/src/components/problem-discovery.tsx
Public/draft isolation risk: no
Accessibility impact: no
Notes: Requires adding page navigation controls (page / page_size query parameters).
```

```text
Defect ID: P8-003
Title: Table rows lack mouse hover state indicator
Severity: low
Checklist section/item: 7. Desktop and tablet problem results - "Hover, keyboard focus, and selected states remain distinguishable"
Commit: b8e43cf
Browser and viewport: Chrome, Desktop 1440x900
Preconditions/data slug: Any published problem list
Exact URL: http://localhost:3000/problems
Steps to reproduce:
1. Hover mouse over a problem row in the desktop table.
Expected: Row background or border changes to provide distinct visual feedback for hover state.
Actual: No hover effect is applied to the row.
Reproducibility: always
Console error: None
Network request/status/request ID: N/A
Evidence path or screenshot: frontend/apps/learn/app/globals.css
Public/draft isolation risk: no
Accessibility impact: no
Notes: Add .problem-table tbody tr:hover styling in globals.css.
```

```text
Defect ID: P8-004
Title: Mobile filter sheet lacks accessible name, focus trap, Escape key handling, and auto-collapsing "More filters"
Severity: medium
Checklist section/item: 8. Mobile cards and filter sheet & 17. Keyboard, screen-reader, zoom
Commit: b8e43cf
Browser and viewport: Chrome, Mobile 360x800 and 767px
Preconditions/data slug: Any published problems
Exact URL: http://localhost:3000/problems
Steps to reproduce:
1. Open http://localhost:3000/problems at viewport 360px.
2. Click "Open filters" to open the sheet.
3. Open the "More filters" details panel inside the sheet.
4. Press the "Escape" key, or Tab past the last control.
5. Close the sheet via the "Close" button and reopen it.
Expected: Sheet has aria-label/aria-labelledby; pressing Escape closes the sheet; keyboard Tab stays trapped inside the sheet; "More filters" collapses when sheet closes.
Actual: Escape does nothing; Tab focus leaks out into background elements; sheet lacks accessible dialog semantics; "More filters" remains open on close/reopen.
Reproducibility: always
Console error: None
Network request/status/request ID: N/A
Evidence path or screenshot: frontend/apps/learn/src/components/problem-discovery.tsx:128
Public/draft isolation risk: no
Accessibility impact: yes
Notes: Add role="dialog", aria-modal="true", onKeyDown Escape + trapFocus, and reset details on sheet close.
```

```text
Defect ID: P8-005
Title: Response validation does not automatically focus the invalid/error field
Severity: low
Checklist section/item: 11. Response validation for all five task families - "Focus moves predictably to the error or invalid input"
Commit: b8e43cf
Browser and viewport: Chrome, Desktop 1440x900
Preconditions/data slug: Any published problem
Exact URL: http://localhost:3000/problems/[slug]
Steps to reproduce:
1. Open a problem with a response form.
2. Submit an empty or invalid response.
Expected: Focus shifts automatically to the first invalid input or the error announcement message.
Actual: Error message appears, but focus remains on the Submit button.
Reproducibility: always
Console error: None
Network request/status/request ID: N/A
Evidence path or screenshot: frontend/apps/learn/src/components/response-form.tsx
Public/draft isolation risk: no
Accessibility impact: yes
Notes: Add ref to first error field / alert message and call focus() on failed validation.
```

```text
Defect ID: P8-006
Title: Short answer and Python function response forms lack visible character limit guidance
Severity: low
Checklist section/item: 11. Response validation for all five task families - Short answer & Python function
Commit: b8e43cf
Browser and viewport: Chrome, Desktop 1440x900
Preconditions/data slug: SHORT_ANSWER and CODE_FUNCTION problems
Exact URL: http://localhost:3000/problems/[slug]
Steps to reproduce:
1. Open a Short Answer or Python Function problem.
2. Inspect the textarea / code entry field.
Expected: A visible hint or label guidance indicating allowed character/size limits (e.g. "Up to 20,000 characters").
Actual: No character limit guidance is displayed to the learner before submission.
Reproducibility: always
Console error: None
Network request/status/request ID: N/A
Evidence path or screenshot: frontend/apps/learn/src/components/response-form.tsx
Public/draft isolation risk: no
Accessibility impact: no
Notes: Render schema.max_length limit guidance next to the label/textarea.
```

```text
Defect ID: P8-007
Title: "Continue to..." next recommendation link loses search/filter query parameters
Severity: medium
Checklist section/item: 15. Complete and continue - "Opening it preserves the selected-stage/list return context"
Commit: b8e43cf
Browser and viewport: Chrome, Desktop 1440x900
Preconditions/data slug: Completed problem with an eligible recommendation
Exact URL: http://localhost:3000/problems/[slug]
Steps to reproduce:
1. Navigate to /problems with filters (e.g., /problems?stage=AI_1_FOUNDATIONS&q=metrics&difficulty=EASY).
2. Open and complete a problem.
3. Observe the "Continue to [next problem]" link.
4. Click the continuation link and then click "Back to problem library".
Expected: The return_to parameter on the continuation link preserves all active search/filter query parameters.
Actual: The continuation link only attaches ?stage=..., losing search queries and other applied filters.
Reproducibility: always
Console error: None
Network request/status/request ID: N/A
Evidence path or screenshot: frontend/apps/learn/src/components/learner-actions.tsx:58
Public/draft isolation risk: no
Accessibility impact: no
Notes: Update recommendation href to propagate returnUrl instead of just /problems?stage=${stage}.
```

```text
Defect ID: P8-008
Title: Missing visible skip link for keyboard navigation and visible focus indicator on "Open filters" button
Severity: low
Checklist section/item: 17. Keyboard, screen-reader, zoom, and responsive pass - Skip link & focus indicators
Commit: b8e43cf
Browser and viewport: Chrome, Desktop and Mobile
Preconditions/data slug: http://localhost:3000/problems
Exact URL: http://localhost:3000/problems
Steps to reproduce:
1. Navigate to http://localhost:3000/problems.
2. Press "Tab" immediately upon page load.
3. On mobile viewport, Tab into "Open filters" button.
Expected: A visible "Skip to main content" link appears on first Tab; "Open filters" button has a prominent focus ring.
Actual: No skip link exists in RootLayout; "Open filters" button lacks distinctive focus indicator compared to other buttons.
Reproducibility: always
Console error: None
Network request/status/request ID: N/A
Evidence path or screenshot: frontend/apps/learn/app/layout.tsx:10
Public/draft isolation risk: no
Accessibility impact: yes
Notes: Add <a href="#main-content" className="skip-link">Skip to main content</a> in layout.tsx and add :focus-visible style for .open-filters.
```

## 21. Final result record

```text
Stack, migration, and health:                 PASS
Representative published content:             PASS
Stage selection and first viewport:           PASS
Search/filter/hierarchy/URL state:            PASS
Sort/count/pagination:                        FAIL (P8-002: missing pagination controls)
Desktop/tablet results:                       PASS
Mobile cards/filter sheet:                    FAIL (P8-004: sheet a11y & Escape/trapFocus)
Recommendation/path guidance:                 PASS
Permanent detail and snapshot stability:      PASS
Five response families and validation:        PASS
Assessment feedback/retry/privacy:            PASS
Anonymous local progress:                     PASS
Problem feedback/abuse controls:              PASS
Complete and continue:                        FAIL (P8-007: continuation loses filter context)
Loading and safe failure behavior:            FAIL (P8-001: Try again button frozen)
Accessibility/responsive/zoom:                FAIL (P8-004, P8-008: skip link & focus trap)
Public/draft isolation:                       PASS
Automated corroboration:                      PASS

Defects found: P8-001, P8-002, P8-003, P8-004, P8-005, P8-006, P8-007, P8-008

Evidence (screenshots, request IDs, logs, traces): bash scripts/test_learner_e2e.sh passed

Overall Phase 8 result:                       FAIL (Pending resolution of P8-001, P8-004, P8-007)
```
