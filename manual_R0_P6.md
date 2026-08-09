# Release 0 Phase 6 manual verification

This checklist verifies the completed **Phase 6 — Problem domain and
authoring** slice (`R0-06001` through `R0-06020`). It covers the author draft
domain, persistence, author API, Studio list/editor, autosave and recovery,
validation, and the isolated preview projection.

Phase 6 does **not** include editorial transitions, publication, or the rendered
learner-format preview page. Those belong to Phase 7. The Studio may expose a
**Preview as learner** link, but for Phase 6 the acceptance target is the
author-only preview API and its isolation from public routes.

## 1. Prerequisites

- Docker and Docker Compose are installed.
- Ports `5432`, `8000`, `3000`, and `3001` are available on the development
  host.
- Run commands from the repository root.
- Use a current Chromium, Firefox, or Safari browser with developer tools.
- For Vietnamese entry, enable a native operating-system input method such as
  UniKey or Simple Telex. Phase 6 intentionally does not ship browser-side
  Telex conversion because no evaluated JavaScript package met the stability
  gate; see `docs/decisions/06013-vietnamese-input.md`.

Record the tester, commit, browser, operating system, date, and result for each
section.

## 2. Start or redeploy the stack

For a normal start:

```bash
bash scripts/dev_start.sh
```

To recreate all services while preserving the PostgreSQL volume:

```bash
bash scripts/dev_redeploy.sh
```

Confirm all services are healthy:

```bash
docker compose ps
bash scripts/dev_health.sh
```

Expected:

- `postgres`, `api`, `learn`, and `studio` are running and healthy.
- API liveness and readiness checks succeed.
- Learner `/problems` and Studio `/author/problems` return successfully.
- Migration and canonical-vocabulary synchronization complete without errors.

If Studio runs on another host such as `dell310`, create the tunnel from the
workstation:

```bash
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -L 127.0.0.1:3001:127.0.0.1:3001 dell310
```

Then open <http://127.0.0.1:3001/author/problems>. A tunnel error containing
`connect failed: Connection refused` means nothing is listening on port `3001`
on the remote host; run `docker compose ps` and start or redeploy the stack
there first.

## 3. Verify the Studio problem list (`R0-06008`, `R0-06009`, `R0-06011`)

Open <http://127.0.0.1:3001/author/problems>.

- [ ] The header clearly says **IOAI Studio**, not IOAI Learn.
- [ ] The page provides a **Create problem** action.
- [ ] Existing rows show problem ID, editorial status, revision/version, last
      saved time, and validation state.
- [ ] **All**, **Draft**, **In review**, and **Changes requested** tabs are
      visible, and selecting a populated status limits the rows appropriately.
- [ ] Search accepts a problem or revision ID and updates the visible rows.
- [ ] **Clear filters** restores the list after a no-results search.
- [ ] **Resume editing** opens the selected draft.
- [ ] Loading, empty, and API error states reveal no stack trace, database
      detail, or unpublished content from another draft.

## 4. Create and identify a draft (`R0-06002`, `R0-06005`, `R0-06008`, `R0-06012`)

1. Select **Create problem**.
2. Create the draft and wait for its editor to open.
3. Note the problem ID, revision ID, and version.

Expected:

- [ ] A new draft has distinct problem and revision identities.
- [ ] Its editorial state is `DRAFT`.
- [ ] It has no public URL and does not appear in the learner problem list.
- [ ] The editor exposes separate **Save draft**, **Validate draft**, and
      **Preview as learner** actions.
- [ ] After navigating back, the draft is listed and can be resumed.

## 5. Edit bilingual structured content (`R0-06013`)

In the **Content** section:

1. Enter an English title and objective.
2. Switch from **EN** to **VI**, then enter Vietnamese title and objective text
   with the native Vietnamese input method. Example: `Ma trận nhầm lẫn`.
3. Switch between **EN** and **VI** several times.
4. Add repeated blocks including a problem statement, provided information,
   example, constraint, hint, explanation, and feedback.
5. Reorder and remove representative blocks.
6. Mark one translation pending.

Expected:

- [ ] The EN/VI control has a visible selected state and keyboard-accessible
      names **Edit English** and **Edit Vietnamese**.
- [ ] Switching language preserves both translations, dirty state, validation
      state, and the editing context.
- [ ] Native Vietnamese composition enters correct diacritics without duplicate
      characters or corrupted caret behavior.
- [ ] English and code fields are never transformed by an in-browser input
      method.
- [ ] The interface explains that browser conversion is not enabled.
- [ ] Repeated blocks retain their content and order after saving and reloading.
- [ ] Pending translations are visibly identified as author warnings and are
      not inserted into learner content.
- [ ] Every bilingual content field has a keyboard-focusable U+2753 (`❓`) help
      control with field-specific guidance.
- [ ] A non-observable objective remains saveable but produces an actionable
      validation error linked to the objective field.

## 6. Edit curriculum metadata and prerequisites (`R0-06004`, `R0-06014`)

In the **Curriculum** section:

- [ ] Select exactly one pathway stage, difficulty, task type, and primary
      competency from canonical vocabulary.
- [ ] Add zero to three secondary competencies; a fourth cannot be persisted.
- [ ] Search for topics using English and Vietnamese labels where available.
- [ ] Topic choices show hierarchy/breadcrumb context.
- [ ] Selecting an overly broad intermediate topic produces a specificity
      warning.
- [ ] Add `REQUIRED`, `RECOMMENDED`, and `CO_REQUISITE` prerequisite examples.
- [ ] Verify prerequisite target types remain explicit (`TOPIC`, `COMPETENCY`,
      `TASK`, or `LEARNING_UNIT`) and can carry optional minimum evidence.
- [ ] Save and reload; all selections remain canonical and unchanged.
- [ ] A proposed vocabulary value is kept separate from selectable approved
      metadata and cannot become publishable metadata automatically.

## 7. Verify every response variant and exact scoring (`R0-06003`, `R0-06015`)

Change **Response type** through each Phase 6 variant:

- [ ] `QUIZ_SINGLE`: add choices and choose exactly one correct answer.
- [ ] `QUIZ_MULTIPLE`: add choices and choose multiple correct answers.
- [ ] `NUMERIC_ANSWER`: enter an expected value, non-negative absolute
      tolerance, and optional unit.
- [ ] `SHORT_ANSWER`: enter bilingual reference answers, keywords, and rubric
      guidance.
- [ ] `CODE_FUNCTION`: enter a Python signature, starter code, and public and/or
      hidden tests.
- [ ] Leave a code signature, starter code, or test value incomplete and save;
      the draft persists, while Validate reports field-level Assessment errors.

For each change, verify only applicable fields remain; configuration belonging
to the previous variant must not reappear after save/reload.

Then test scoring:

1. Add two scoring components with weights `0.3` and `0.7`.
2. Confirm **Exact total: 1.0** and no total error.
3. Change the weights to `0.3` and `0.6`.

Expected:

- [ ] The UI displays **Exact total: 0.9**.
- [ ] It reports that weights must total exactly `1.0`.
- [ ] Draft validation remains blocked until positive decimal weights total
      exactly `1.0`.
- [ ] Repeated choice, test, and scoring controls are usable by keyboard and
      have distinct accessible names.

## 8. Verify resource and Release 0 policy rules (`R0-06004`, `R0-06016`)

In the **Resources** section:

- [ ] `expected_minutes` rejects zero and negative values.
- [ ] Duration/display categories change as a derived display when exact minutes
      change; they are not separately editable.
- [ ] Selecting `NONE` data modality removes or conflicts visibly with actual
      modalities; an invalid combination cannot validate.
- [ ] Exact compute/runtime limits remain unchanged after save/reload.
- [ ] Setting network policy to **Allowed** shows a Release 0 blocker; **Denied**
      clears it.
- [ ] Canonical but unavailable stages, task types, compute tiers, scoring
      methods, or resource combinations display actionable blockers rather than
      silently becoming eligible.

## 9. Verify explicit save and optimistic concurrency (`R0-06007`, `R0-06010`)

1. Make a small edit and select **Save draft**.
2. Observe **Saving...**, then **Saved**.
3. Reload and confirm the edit persisted and the version increased.
4. Open the same draft in two browser tabs.
5. Save a change in tab A, then save a different change from the stale tab B.

Expected:

- [ ] Tab B receives **Resolve draft conflict** instead of overwriting tab A.
- [ ] The dialog offers **Keep local changes and retry**, **Use server version**,
      and **Review differences before resolving**.
- [ ] Choosing the server version loads the newer server state.
- [ ] Choosing to retain local work preserves it for an explicit retry.
- [ ] A failed or stale save leaves no partially updated curriculum, response,
      scoring, prerequisite, or resource associations.
- [ ] Refreshing always loads the latest saved revision rather than a cached
      earlier version.
- [ ] An English title generates a URL-safe slug automatically; changing the
      title updates an auto-managed slug, while manually editing the slug stops
      further automatic replacement.

## 10. Verify autosave and recovery (`R0-06017`)

### Normal autosave

1. Edit a field and stop typing.
2. Wait for the idle autosave interval.

- [ ] The status progresses through **Saving...** to **Saved**.
- [ ] Rapid edits are coalesced rather than creating visibly overlapping saves.

### API outage and local recovery

1. Stop only the API:

   ```bash
   docker compose stop api
   ```

2. Edit a field and wait for autosave, or select **Save draft**.
3. Confirm **Save failed**.
4. Restart the API:

   ```bash
   docker compose start api
   ```

5. Reload the editor.

Expected:

- [ ] A **Recover unsaved draft** dialog appears for the matching revision.
- [ ] **Restore local copy** restores the local work without silently saving it.
- [ ] **Discard local copy** retains the server revision.
- [ ] Recovery is scoped to the correct revision/version.
- [ ] With browser storage disabled, the editor remains usable and reports save
      failure without crashing; local recovery is best effort only.

## 11. Validate the complete draft (`R0-06005`, `R0-06018`)

1. Leave representative required fields invalid and save.
2. Select **Validate draft**.
3. Correct each blocker, save again, and validate again.

Expected:

- [ ] Validation is disabled while unsaved changes exist, with guidance to save
      first.
- [ ] The report groups issues under **Content**, **Curriculum**,
      **Assessment**, **Resources**, and **Publication**.
- [ ] Errors use `✖ Error:` plus red treatment; warnings use `⚠ Warning:` plus
      amber treatment, so severity never depends on color alone.
- [ ] Explicitly pending translations say **Translation is explicitly
      pending.** and remain non-blocking warnings.
- [ ] Issue links move focus to the corresponding field; the first blocker can
      receive focus deterministically.
- [ ] The report shows `publication_eligible` but offers no Phase 7 approval or
      publication transition.
- [ ] Saving a later change invalidates the stale validation summary.

## 12. Verify the author-only preview projection (`R0-06019`)

Use browser developer tools or `curl`. Replace the placeholders with the values
shown by the editor or author API:

```bash
curl -sS -X POST \
  http://127.0.0.1:8000/api/v1/author/revisions/REVISION_ID/preview \
  -H 'Content-Type: application/json' \
  -d '{"expected_version": VERSION}'
```

If the generated OpenAPI schema requires an additional editor-state field for
the current revision, inspect the canonical request definition at
<http://127.0.0.1:8000/docs> and provide that field rather than guessing its
shape.

Expected:

- [ ] The response includes the exact marker **Draft preview - not public**.
- [ ] It is learner-shaped and includes author warnings separately.
- [ ] Answer keys, hidden tests, revision IDs, validation internals, and
      editorial workflow state are absent from learner content.
- [ ] Unsaved editor state can be projected explicitly without first publishing
      it.
- [ ] The draft cannot be found through learner `/problems`, a public slug,
      public search, recommendations, or a public API response.
- [ ] Opening `/author/problems/{problem_id}/preview` may remain unimplemented in
      Phase 6; rendered responsive preview is `R0-072` in Phase 7.

## 13. Accessibility and responsive spot checks (`R0-06011`–`R0-06018`)

At minimum, inspect the Studio at widths `360`, `768`, `1024`, and `1440` px.

- [ ] No required author field or primary action becomes unreachable.
- [ ] Visible labels remain associated with controls.
- [ ] Keyboard-only navigation reaches status filters, editor sections,
      repeated controls, EN/VI switch, Save, Validate, and Preview.
- [ ] Focus indicators are visible.
- [ ] Dialog choices are keyboard reachable and named.
- [ ] Status, warnings, errors, and selected language do not rely on color alone.
- [ ] At 200% browser zoom, content remains operable without loss of information.

## 14. Public/draft isolation smoke check

Keep the learner app open at <http://127.0.0.1:3000/problems> while editing the
draft.

- [ ] The draft never appears in the public list.
- [ ] No draft content, hidden answer/test data, revision identity, validation
      report, or local recovery content appears in learner network responses.
- [ ] Guessing the problem ID or revision ID on public routes does not return the
      draft.
- [ ] Saving, validating, and previewing do not create a published snapshot.

## 15. Optional automated corroboration

Manual acceptance does not replace automated gates. Run the Phase 6 baseline:

> **Database safety:** the current migration integration suite downgrades its
> configured database to `base`. Back up any unique local drafts before running
> the aggregate gate, or run it against a disposable test database.

```bash
bash scripts/foundation_quality.sh
```

Expected: backend tests, frontend tests, Ruff, Pyright, ESLint, strict
TypeScript, production builds, vocabulary drift, OpenAPI/client drift, and the
Alembic-head check all pass. Record any skipped or failing gate exactly; do not
mark Phase 6 accepted when a required gate is unknown or failing.

## 16. Result record

```text
Tester:
Date/time:
Commit:
Host/OS:
Browser/version:
Native Vietnamese IME:

Stack and health:                 PASS / FAIL
Author list and draft creation:   PASS / FAIL
Bilingual structured content:    PASS / FAIL
Curriculum and prerequisites:    PASS / FAIL
Response and scoring:             PASS / FAIL
Resources and policy:             PASS / FAIL
Save, autosave, and recovery:     PASS / FAIL
Validation:                       PASS / FAIL
Preview API and isolation:        PASS / FAIL
Accessibility/responsive spot:   PASS / FAIL
Automated corroboration:          PASS / FAIL / NOT RUN

Notes and evidence:
```
