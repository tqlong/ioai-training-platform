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
Tester:
Date/time:
Commit:
Host/OS:
Browser/version:
Primary viewport:
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

- [ ] `postgres`, `api`, `learn`, and `studio` are healthy.
- [ ] Migrations and canonical vocabulary synchronization complete.
- [ ] <http://127.0.0.1:8000/health/live> and
      <http://127.0.0.1:8000/health/ready> return healthy responses. The local
      runtime does not expose interactive Swagger at `/docs`; use the committed
      `backend/generated/openapi.json` and browser Network panel to inspect the
      public `/api/v1` contracts.
- [ ] <http://127.0.0.1:3000/problems> opens as **IOAI Learn**.
- [ ] <http://127.0.0.1:3001/author/problems> opens as **IOAI Studio**.
- [ ] Learn does not show stack traces, draft identifiers, object keys, or
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

- [ ] Every published slug appears in the public library.
- [ ] Draft-only, unapproved, and archived-only slugs do not appear.
- [ ] Refreshing the library does not change publication eligibility.

## 4. First viewport, product identity, and stage selector

Open <http://127.0.0.1:3000/problems> in a fresh browser profile.

- [ ] The header says **IOAI Learn**, not IOAI Studio.
- [ ] The first desktop viewport includes stage selection, one recommendation,
      and the beginning of the problem list without a large marketing hero.
- [ ] Stages appear in canonical curriculum order: AI Foundations, Competition
      Foundations, High-school Competition, Collegiate Competition, and Open.
- [ ] AI Foundations and Competition Foundations are selectable.
- [ ] Later stages are disabled and visibly explained as **Coming next**.
- [ ] Disabled stages cannot be selected with mouse, keyboard, touch, or a
      hand-edited query string.
- [ ] Choosing an enabled stage changes both results and recommendation.
- [ ] The selected stage remains visibly selected and appears canonically in
      the URL query string.
- [ ] Browser Back and Forward restore the previous stage and results.
- [ ] Statuses and disabled states use visible text, not color alone.

## 5. Search, filters, hierarchy, and shareable URL state

Exercise each filter separately, then combine several filters.

- [ ] Search matches a published English title or objective.
- [ ] Search matches supported Vietnamese text.
- [ ] Search matches an approved alias where fixture content permits it.
- [ ] Search does not return draft, unapproved, superseded, or archived-only
      content.
- [ ] The compact desktop filter row includes Search, Stage, Topic, Difficulty,
      Type, More filters, and Clear.
- [ ] Exactly the eight top-level topic families are shown as shortcuts; the
      full topic vocabulary is not rendered as a flat chip cloud.
- [ ] The topic picker is searchable and shows family, intermediate, and leaf
      hierarchy rather than relying on Markdown heading position.
- [ ] Selecting a parent topic without **Include subtopics** does not silently
      include descendants.
- [ ] Enabling **Include subtopics** includes matching descendants explicitly.
- [ ] Stage, competency, topic, difficulty, task type, task status, learning
      evidence, time, and compute filters produce appropriately scoped results.
- [ ] Active filters appear as individually removable tokens.
- [ ] Removing one token preserves the other active filters.
- [ ] **Clear filters** removes active filter state and restores results.
- [ ] Search/filter selections use canonical codes in the URL where applicable,
      not translated labels or unpublished identifiers.
- [ ] Copying the URL into a fresh tab reproduces the same discovery state.
- [ ] Back/Forward changes the visible controls and result list consistently.
- [ ] Unknown, malformed, duplicated, or unavailable query values are rejected
      or normalized safely; they never broaden access to private content.

Create a combination that returns no matches.

- [ ] The empty state says active filters caused no matching results.
- [ ] It offers a working **Clear filters** action.
- [ ] Clearing restores published results without a full broken-page state.

## 6. Sorting, count, and pagination

- [ ] The default order follows editorial learning-path order, then difficulty.
- [ ] **Newest** sort is deterministic across refreshes.
- [ ] **Expected time** sort orders by exact minutes.
- [ ] **Title** sort is deterministic and understandable.
- [ ] The selected sort is stored in the URL.
- [ ] The result count agrees with the visible filtered data.
- [ ] Pagination controls are explicit when enough content exists.
- [ ] Moving between pages updates the URL and does not duplicate or omit rows.
- [ ] Changing a filter from a later page returns to a valid page.
- [ ] Refresh, Back, and Forward preserve the expected sort/page state.

## 7. Desktop and tablet problem results

At `1440` px wide, inspect the dense table.

- [ ] The table has an accessible name and a sticky header on a long list.
- [ ] Every row shows task status and learning evidence as separate fields.
- [ ] A new problem shows `NOT_STARTED`/Not started and `—` when no evidence
      exists; it never shows `MASTERED`.
- [ ] Every row shows title, permanent short ID, one-line objective, stage and
      difficulty together, primary competency, task type, exact minutes, and
      compute tier.
- [ ] No more than two topic chips are visible.
- [ ] A problem with additional topics shows an accessible `+N` disclosure with
      the correct remaining labels.
- [ ] Clicking the title opens the permanent problem URL.
- [ ] Clicking a non-interactive part of the row opens the same URL.
- [ ] Using a disclosure or nested control does not accidentally navigate.
- [ ] Hover, keyboard focus, and selected states remain distinguishable.

At `1024` and `1279` px wide:

- [ ] Results remain a table, not mobile cards.
- [ ] Competency/evidence hidden from the main row remain available through row
      details rather than disappearing.
- [ ] The learning-path sidebar moves below the recommendation as specified.
- [ ] Meaningful metadata remains readable before decorative content.

At exactly `768` px wide:

- [ ] Results still use the table breakpoint.
- [ ] No required action is clipped or unreachable.

## 8. Mobile cards and filter sheet

At `360` px wide and again at `767` px:

- [ ] The desktop table is replaced by a list of compact problem cards.
- [ ] Each card retains title, task status, stage and difficulty together,
      primary topic, task type, and expected minutes.
- [ ] Cards do not horizontally overflow the viewport.
- [ ] **Open filters** opens a full-height sheet.
- [ ] The sheet has an accessible name and visible field labels.
- [ ] Keyboard focus enters the sheet and remains inside it while open.
- [ ] Escape closes the sheet when safe and returns focus to **Open filters**.
- [ ] Touch targets are usable without accidental adjacent activation.
- [ ] The primary action says **Show N problems** with the current result count.
- [ ] Applying filters closes the sheet and updates cards and URL.
- [ ] Reopening the sheet restores the active selections.

## 9. Recommendation and learning-path guidance

First clear site data and select an enabled stage.

- [ ] Exactly one feature card is labeled **Recommended start**.
- [ ] It uses the editorially first eligible published problem for the selected
      stage and does not claim personalization or mastery.
- [ ] **Why this?** exposes a plain-language reason and is keyboard operable.
- [ ] The recommendation never points to the current, draft-only, archived,
      unavailable-stage, or unsupported-task problem.
- [ ] Weekly goal does not present zero history as failure.
- [ ] Current path, prerequisites to review, recently completed, and suggested
      topics remain supportive and bounded.
- [ ] Recently completed contains no more than three problems.
- [ ] Suggested next topics contains no more than two topics.

After attempting/completing problems in the same stage:

- [ ] The recommendation uses compatible published content and local history.
- [ ] It excludes the current problem when another suitable candidate exists.
- [ ] Changing stage scopes the recommendation to the selected stage.
- [ ] Reload restores the recommendation context without an account.

## 10. Permanent problem URL and published content

Open each recorded slug directly in a fresh tab, without visiting the list.

- [ ] `/problems/{slug}` loads the same published problem directly.
- [ ] The title, stage and difficulty together, observable objective,
      prerequisites, statement, provided information/examples, constraints,
      response area, and available hints/explanation follow learner reading
      order.
- [ ] Taxonomy metadata does not dominate the main task content.
- [ ] Resource and response instructions match the published task.
- [ ] Hint and explanation disclosures are keyboard operable and expose only
      content allowed by the published snapshot.
- [ ] No **Draft preview — not public** banner or author translation warning is
      present on a public page.
- [ ] No revision ID, editorial status/history, validation result, answer key,
      hidden test, scoring configuration, object key, or draft content appears
      in the page source or public API response.
- [ ] A valid `return_to` link returns to the prior filtered library URL.
- [ ] An absent or unsafe `return_to` value falls back safely to `/problems`.
- [ ] A guessed missing, draft-only, unapproved, or archived-only slug shows the
      same safe **Problem unavailable** behavior.

If practical, create and save a successor draft for a published problem.

- [ ] The permanent URL continues to show the old published snapshot.
- [ ] After the successor passes review and is published, the same URL shows the
      new snapshot; the URL itself does not change.

## 11. Response validation for all five task families

For every form, first submit an empty or malformed response.

- [ ] The invalid response remains editable.
- [ ] A visible, field-addressable message explains how to correct it.
- [ ] Focus moves predictably to the error or invalid input.
- [ ] No result claims completion, and no unsafe implementation detail appears.

### Single-choice quiz

- [ ] Choices are one keyboard-operable radio group with visible labels.
- [ ] Only one choice can be selected.
- [ ] Selecting and changing a choice works before submission.

### Multiple-choice quiz

- [ ] Choices are keyboard-operable checkboxes with visible labels.
- [ ] One or more choices can be selected and deselected.
- [ ] Empty selection is rejected with actionable guidance.

### Numeric answer

- [ ] The numeric input has a visible label and tolerance/unit guidance.
- [ ] Non-finite or malformed input is rejected while remaining editable.
- [ ] A valid decimal near a configured tolerance boundary is assessed
      consistently.

### Short answer

- [ ] The bounded text input has a visible label and limit guidance.
- [ ] Oversized input is blocked or rejected safely.
- [ ] The human-rubric path reports pending assessment rather than completion.

### Python function

- [ ] Language, signature, starter code, public examples, and allowed limits are
      visible without exposing hidden tests.
- [ ] The code field has an accessible name and retains multiline input.
- [ ] Oversized/empty code is rejected safely and remains editable.
- [ ] The human-rubric path reports pending assessment rather than pretending
      to execute an advanced judge.
- [ ] The form never requests GPU, distributed, or hosted-notebook resources.

## 12. Submission results, retry safety, and privacy

Submit a correct and an incorrect automated answer where fixture data allows.

- [ ] The submit button prevents accidental duplicate requests while pending.
- [ ] An accepted assessment shows outcome, score/rubric summary, and actionable
      component feedback.
- [ ] Decimal scores are stable and understandable (for example, exact correct
      work scores `1.0`).
- [ ] Incorrect feedback does not reveal the answer key, hidden tests, or
      unpublished explanation.
- [ ] A pending human assessment does not grant `COMPLETED` or learning evidence.
- [ ] The answer remains visible/editable after a safe validation or dependency
      failure.
- [ ] Retrying a failed request uses the same logical submission and does not
      create duplicated visible outcomes.
- [ ] Refreshing during/after submission does not expose an internal error.

In developer tools, temporarily block the submission request and submit again.

- [ ] A safe message says the answer could not be assessed and offers retry.
- [ ] The learner's entered response is retained.
- [ ] The error contains no provider, database, stack, snapshot, or revision
      details.

## 13. Device-local anonymous progress

Clear site data, open a published problem, then return to the library.

- [ ] Opening a problem records approved local context without an account.
- [ ] A valid submission changes task status monotonically to `ATTEMPTED` or
      `COMPLETED` according to its outcome.
- [ ] Task status and learning evidence remain separate; neither is presented
      as `MASTERED`.
- [ ] Refresh and browser restart restore status, available evidence, recent
      history, and recommendation context on the same device.
- [ ] The library overlay agrees with the detail page.
- [ ] Inspecting local storage shows no answer/response text, credentials,
      identity claim, draft content, editorial status, hidden test, or author
      data.
- [ ] Local records are bounded rather than growing without limit.
- [ ] Clearing site data resets progress without affecting published content or
      server availability.

Corrupt `ioai.learn.progress.v1` in developer tools, then reload.

- [ ] Corrupt progress is discarded safely; the library and solving loop work.
- [ ] No corrupt payload is rendered into the page or error message.

Disable/block local storage and reload a problem.

- [ ] Browsing and submission remain usable.
- [ ] A clear notice explains that progress is temporary on this device.
- [ ] The notice does not expose stored content or imply an account failure.

## 14. Problem feedback dialog and abuse behavior

On every public problem family, confirm **Report a problem** is available. Open
the dialog with the keyboard.

- [ ] Focus enters the named feedback dialog and lands predictably.
- [ ] Category and Message have visible labels.
- [ ] Only approved feedback categories are offered.
- [ ] No account, name, email, or identity is required.
- [ ] Empty and oversized messages produce safe actionable validation.
- [ ] Invalid input remains editable and is not reported as success.
- [ ] Escape closes safely and returns focus to **Report a problem**.
- [ ] Focus remains trapped inside the dialog while it is open.
- [ ] A valid bounded report shows a clear success receipt.
- [ ] Retrying the same failed logical report does not create multiple success
      confirmations.

Submit valid reports repeatedly from disposable local data until the anonymous
limit is reached.

- [ ] Excess requests receive a bounded rate-limit message.
- [ ] The message reveals no moderation state, stored feedback, snapshot ID,
      internal counter, or infrastructure detail.
- [ ] Rate limiting feedback does not break browsing or solving.

## 15. Complete and continue

Complete an automatically assessed problem with another eligible published
problem available in the selected stage.

- [ ] Exactly one **Continue to …** recommendation appears after completion.
- [ ] It does not appear as a completed recommendation for pending assessment.
- [ ] The next item is not the current problem when an alternative exists.
- [ ] Its link is a permanent `/problems/{slug}` URL.
- [ ] Opening it preserves the selected-stage/list return context.
- [ ] It never points to a draft, archived-only revision, unavailable stage, or
      unsupported Release 0 task.
- [ ] Returning to the library restores filters and the prior list position as
      closely as browser navigation permits.
- [ ] The local continuation measure is bounded and stores no identity.

## 16. Loading, dependency failure, and safe errors

Use developer-tool throttling to observe loading states, then block the public
problem-list request.

- [ ] Loading retains the page/table or card dimensions without a large layout
      shift.
- [ ] A list failure shows a safe retry action and feedback path.
- [ ] Retry succeeds after unblocking the request.
- [ ] The failure view exposes no drafts, SQL, stack trace, provider error,
      object key, internal ID, or private network detail.

Repeat for a problem-detail request.

- [ ] Detail loading and unavailable states are distinct and understandable.
- [ ] Retrying a temporary failure does not turn a private slug into public
      content or leak whether an unpublished revision exists.

## 17. Keyboard, screen-reader, zoom, and responsive pass

Repeat the core browse -> filter -> open -> answer -> feedback -> continue flow
at `360`, `768`, `1024`, and `1440` px and at 200% browser zoom.

- [ ] A visible skip link or equivalent structure supports efficient navigation.
- [ ] Headings and landmarks describe page hierarchy in a sensible order.
- [ ] All controls have accessible names and visible focus indicators.
- [ ] Filters, topic disclosures, row details, hints, explanations, response
      forms, feedback dialog, and continuation work using keyboard only.
- [ ] Dialog/sheet focus is trapped, Escape behavior is safe, and focus returns
      to the trigger.
- [ ] Status, evidence, errors, success, pending state, and disabled state never
      rely on color alone.
- [ ] Text and controls remain readable at 200% zoom.
- [ ] No required content, feedback action, submit action, or navigation becomes
      clipped, overlapped, or unreachable.
- [ ] Touch interactions at mobile width do not trigger unintended row/card
      navigation.

## 18. Public/draft isolation spot check

Keep Studio and Learn open side by side while editing a published problem's
successor draft.

- [ ] Unsaved and saved draft changes appear only in Studio Preview.
- [ ] Learn list, detail, recommendation, submission, and feedback continue to
      use the current published snapshot.
- [ ] Guessing problem IDs, revision IDs, preview identifiers, or query flags on
      public routes does not expose unpublished content.
- [ ] Public API responses never include editorial notes/history, answer keys,
      hidden tests, validation state, internal revision identity, or object
      metadata.
- [ ] Archiving removes current public eligibility consistently from list,
      detail, recommendation, submission, and feedback.

Run the static cross-layer check:

```bash
bash scripts/public_isolation_check.sh
```

- [ ] The learner production build completes.
- [ ] No known author-only marker is found in the learner bundle.

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

- [ ] Ruff formatting/linting and Pyright pass.
- [ ] Backend unit and isolated PostgreSQL integration tests pass.
- [ ] Alembic migration and canonical vocabulary drift checks pass.
- [ ] OpenAPI/generated-client agreement and public-isolation checks pass.
- [ ] ESLint, strict TypeScript, Vitest/Testing Library, and both Next.js
      production builds pass.
- [ ] The focused Chromium learner workflow passes after redeployment.
- [ ] Browser coverage includes `360`, `768`, `1024`, and `1440` px.
- [ ] Every skipped or failing gate is recorded; Phase 8 is not accepted while
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

## 21. Final result record

```text
Stack, migration, and health:                 PASS / FAIL
Representative published content:            PASS / FAIL
Stage selection and first viewport:           PASS / FAIL
Search/filter/hierarchy/URL state:            PASS / FAIL
Sort/count/pagination:                        PASS / FAIL
Desktop/tablet results:                       PASS / FAIL
Mobile cards/filter sheet:                    PASS / FAIL
Recommendation/path guidance:                PASS / FAIL
Permanent detail and snapshot stability:      PASS / FAIL
Five response families and validation:        PASS / FAIL
Assessment feedback/retry/privacy:            PASS / FAIL
Anonymous local progress:                     PASS / FAIL
Problem feedback/abuse controls:              PASS / FAIL
Complete and continue:                        PASS / FAIL
Loading and safe failure behavior:            PASS / FAIL
Accessibility/responsive/zoom:                PASS / FAIL
Public/draft isolation:                       PASS / FAIL
Automated corroboration:                      PASS / FAIL / NOT RUN

Defects found:

Evidence (screenshots, request IDs, logs, traces):

Overall Phase 8 result:                       PASS / FAIL
```
