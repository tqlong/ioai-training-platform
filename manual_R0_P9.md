# Release 0 Phase 9 manual verification

This checklist verifies the human-assisted parts of **Phase 9 — Integration and
system verification** (`R0-09001` through `R0-09016`). It complements the
automated baseline in `docs/phase9-system-verification.md`; it does not replace
`bash scripts/release0_verification.sh all`.

The highest-priority manual evidence is:

- current branded Chrome, Firefox, Safari, mobile Chrome, and mobile Safari;
- NVDA + Firefox or VoiceOver + Safari screen-reader operation;
- full physical-keyboard and physical-touch operation;
- grayscale, focus, zoom, and responsive presentation on the pilot display;
- a GitHub-hosted run of the committed Release 0 workflow;
- any claimed macOS or Windows Docker Desktop support; and
- an approved backup provider, schedule, retention, off-host location, and
  recovery objective.

Do not mark an item passed solely because Playwright, axe, or a component test
covers a similar interaction. Use `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN` for
every check. A blank result is `NOT RUN`, never an implicit pass.

Commands shown in inline code may wrap visually in this document; enter each as
one shell command unless it is inside a multi-command fenced block. Replace
uppercase placeholders such as `RUN_ID` and `ATTEMPT_ID` with recorded
disposable values before execution.

## 1. Test record

```text
Tester:
Reviewer:
Date/time and timezone:
Commit (`git rev-parse HEAD`):
Environment name:
Host OS/version:
Docker/Compose version:
Python/uv version:
Node/pnpm version:
Browser and exact version:
Device/model and OS version:
Assistive technology and version:
Viewport/display scale:
Fixture problem IDs/slugs:
Evidence folder or issue link:
```

Result vocabulary:

- `PASS` — the stated procedure was performed and met every pass condition.
- `FAIL` — the procedure was performed and at least one condition failed.
- `BLOCKED` — the environment should support the check, but a defect or setup
  problem prevented completion.
- `NOT RUN` — the required browser, device, assistive technology, authority, or
  environment was unavailable.

For every failure, record the check ID, exact route, input, expected behavior,
actual behavior, request ID, browser console/network evidence, and a sanitized
screenshot or recording. Never attach answers, receipts, editorial notes,
credentials, database URLs, object keys, or private rubric guidance.

## 2. Safety and prerequisites

- [ ] `P9-M001` Run
      `bash scripts/db_backup_restore.sh backup backups/manual-r0-p9.dump`
      before creating fixtures (choose a new filename because overwrite is
      refused), then run `stat backups/manual-r0-p9.dump`. Pass if the command
      succeeds, the file is non-empty and private to the operator, and the file
      is kept outside any shared/public evidence upload.
- [ ] `P9-M002` Run `pwd`, `git rev-parse HEAD`, and `git status --short` from
      the intended repository. Pass if `pwd` is the repository root, HEAD equals
      the commit in the test record, and every reported worktree change is
      identified as intentional before testing.
- [ ] `P9-M003` Run `docker --version`, `docker compose version`, `uv --version`,
      `pnpm --version`, `node --version`, and `ss -ltn` (use the platform's
      equivalent socket-list command if `ss` is unavailable). Pass if each
      required tool starts and ports 5432/8000/3000/3001 are either free or
      already owned by this repository's recorded Compose project—not an
      unrelated process.
- [ ] `P9-M004` In Studio, create fixtures with a unique prefix such as
      `manual-r0-p9-YYYYMMDD-*`, record their problem IDs/slugs, and confirm no
      production/pilot record will be edited. Pass if all planned mutations are
      confined to those disposable records. Do not run the database `reset`
      command for this check.
- [ ] `P9-M005` Run `docker compose config` and
      `docker compose ps --format json`, then inspect host listening sockets with
      `ss -ltn`. Pass if Studio publishes only `127.0.0.1:3001`, API only
      `127.0.0.1:8000`, PostgreSQL only `127.0.0.1:5432`, and the tester records
      that these exposure controls are not authentication.

Redeploy without deleting the PostgreSQL volume:

```bash
bash scripts/dev_redeploy.sh
bash scripts/dev_health.sh
docker compose ps
```

- [ ] `P9-M006` Run `docker compose ps` after redeploy. Pass if `postgres`,
      `api`, `learn`, and `studio` are running and each status is `healthy`; any
      restarting, exited, starting beyond its timeout, or unhealthy service is a
      failure.
- [ ] `P9-M007` Run
      `curl -fsS http://127.0.0.1:8000/health/live` and
      `curl -fsS http://127.0.0.1:8000/health/ready`. Pass if liveness reports
      `status=ok`, readiness reports `status=ready`, `database=ready`, and
      `schema=current`, and neither response exposes connection details.
- [ ] `P9-M008` Open <http://127.0.0.1:3000/problems> and
      <http://127.0.0.1:3001/author/problems> in the recorded browser. Pass if
      the first visibly identifies **IOAI Learn**, the second **IOAI Studio**,
      both load without console errors, and neither identity can be mistaken
      for the other.

Prepare representative published, draft-only, successor-draft, archived, and
human-assessed content using `manual_R0_P7.md`, `manual_R0_P8.md`, and
`manual_R0_P8_1.md`. Use at least one problem from each of the five Release 0
response families. Record permanent slugs and opaque learner result links in
the test record; do not put receipts in shared evidence.

## 3. Automated baseline review

The manual reviewer need not rerun the 20-minute aggregate if a current trusted
run exists for the same commit, but must review its result.

```bash
bash scripts/release0_verification.sh all
```

- [ ] `P9-M010` Run `git rev-parse HEAD`, save its value, then run
      `set -o pipefail; bash scripts/release0_verification.sh all 2>&1 | tee
      /tmp/manual-r0-p9-all.log`. Pass if HEAD equals the recorded commit, the
      command exits 0, and the log ends with
      `Release 0 verification mode passed: all` after quality, PostgreSQL,
      browser, Compose, and recovery output.
- [ ] `P9-M011` Run
      `rg -n "skipped|did not run|allowed.failure|continue-on-error|failed|error"
      /tmp/manual-r0-p9-all.log` and review every match in context; also inspect
      `.github/workflows/release-0-ci.yml` for the five required jobs. Pass if no
      required test was skipped or tolerated and deliberate failure-injection
      messages are followed by their expected recovery/pass evidence.
- [ ] `P9-M012` Before rerunning a failure, preserve available artifacts with
      `tar -czf /tmp/manual-r0-p9-failure-artifacts.tgz test-results
      playwright-report` (omit a missing directory rather than creating fake
      evidence), or download the corresponding CI artifacts. Pass if the archive
      opens, is linked from the defect record, and contains no secrets/private
      answers before it is shared.
- [ ] `P9-M013` Open the **Final criterion audit**, **Final cross-system
      invariant audit**, and **Final environment, artifacts, and limitations**
      sections in `docs/phase9-system-verification.md`; compare every row with
      the current run and this manual record. Pass if each changed result or
      limitation is updated or linked to a defect/decision and no old baseline
      is presented as current evidence.

## 4. Current branded browser matrix

Run the critical journeys in current stable branded browsers available for the
pilot. Playwright's bundled engines are automated evidence, not substitutes for
this table.

| Check | Browser/device and exact procedure | Result/evidence |
| --- | --- | --- |
| `P9-M020` | Open Chrome's `chrome://version`, record the exact stable version, create a fresh profile, and execute browser procedure B1–B6 below on desktop Chrome. | |
| `P9-M021` | Open Firefox **Help → About Firefox**, record the exact stable version, create a fresh profile, and execute B1–B6 on desktop Firefox. | |
| `P9-M022` | On macOS, open Safari **About Safari**, record macOS/Safari versions, use a fresh profile/private window, and execute B1–B6. Studio steps require local access on that Mac; otherwise record the Studio portions `NOT RUN`. | |
| `P9-M023` | On a physical Android device, record model/Android/Chrome versions, clear site data, connect only to the approved learner LAN address, and execute B1–B3 and B6. Execute B4–B5 only through an approved secure local-device setup; otherwise mark them `NOT RUN`. | |
| `P9-M024` | On a physical iPhone/iPad, record model/iOS-or-iPadOS/Safari versions, clear site data, connect only to the approved learner LAN address, and execute B1–B3 and B6. Execute B4–B5 only through an approved secure local-device setup; otherwise mark them `NOT RUN`. | |

Browser procedure:

1. **B1 — learner discovery and solving:** open a recorded permanent problem URL
   directly, return to `/problems`, search once in English and once in
   Vietnamese, select a parent topic with descendants first off and then on,
   copy/reopen the resulting URL, submit representative response families,
   report problem feedback, and use the single continuation. Pass if state is
   restored from the URL and each action returns safe usable feedback.
2. **B2 — local state:** complete one problem, refresh, use Back/Forward, and
   reopen the site in the same profile and then a clean profile. Pass if local
   status/history persists only in the original profile and the UI never claims
   an account or cross-device synchronization.
3. **B3 — public isolation:** try recorded draft-only, approved-unpublished,
   superseded, and archived-only slugs through list search, direct URL, and
   recommendation. Pass if none is exposed and direct lookups share the safe
   unavailable behavior.
4. **B4 — editorial lifecycle:** in Studio create a uniquely prefixed draft,
   save, validate, preview unsaved content, submit review, request changes,
   address changes, approve, confirm publish, create a successor, publish it,
   archive, and republish. Pass if notes are required, save/approval/publication
   remain separate, the public snapshot changes only on publish, and the slug
   remains stable.
5. **B5 — manual assessment:** submit a human-scored answer in Learn, open the
   oldest pending Studio queue item, assess it with the published snapshot
   rubric, view the safe learner result, then correct the decision. Pass if the
   correction appends history and never exposes private rubric material.
6. **B6 — browser presentation:** keep developer console/network tools open
   while completing the journey and inspect every primary action at the target
   viewport. Pass if there is no browser-specific crash, uncaught console error,
   clipped action, unusable native control, or unintended page-level horizontal
   scroll.

Do not expose Studio on a LAN interface merely to test a physical device. Use
an approved secure device-lab/tunnel arrangement that preserves the local
operator boundary, or mark physical-device Studio checks `NOT RUN`.

## 5. Screen-reader verification

Perform at least one of these supported combinations and record the exact
versions:

- NVDA with Firefox on Windows; or
- VoiceOver with Safari on macOS/iOS.

### Learn

- [ ] `P9-M030` Enable the recorded screen reader, open `/problems`, use its
      landmark/heading/form-control/table navigation commands, select each
      enabled stage, open the recommendation reason, change one compact filter,
      traverse the result count and first two results, and move pagination when
      available. Pass if names, roles, selected/disabled state, headers, row/card
      context, and updated count are announced in logical task order.
- [ ] `P9-M031` From `/problems`, open the topic picker using only screen-reader
      navigation, search for a known leaf, traverse its ancestors, select a
      parent, toggle **Include subtopics**, and encounter one unavailable value.
      Pass if hierarchy, checked state, the descendants option, and the reason a
      value is unavailable are spoken without depending on visual indentation.
- [ ] `P9-M032` Open each recorded response-family problem directly, navigate by
      heading through objective/content/response, operate disclosures, submit an
      invalid then valid response, and follow pending/final feedback and the
      continuation. Pass if reading order is coherent, every input/error/state
      is named, the error is associated with its field, and unrelated content
      remains readable while feedback is pending.
- [ ] `P9-M033` On learner desktop open **Report a problem**; on a narrow viewport
      open **Open filters**. With the screen reader, traverse forward/backward
      past both dialog boundaries, press Escape, and continue reading. Pass if
      title/modal state is announced, focus wraps inside, Escape closes where
      safe, and focus returns to the exact trigger.
- [ ] `P9-M034` Trigger: a filtered empty result, a malformed query, a recoverable
      submission failure/retry, a storage-disabled state, and pending then final
      assessment. Pass if loading/empty/error/retry/storage/status messages are
      announced once meaningfully, task status and learning evidence are
      separate, and neither speech nor visible text says `MASTERED`.

### Studio

- [ ] `P9-M035` Open `/author/problems`, enter a recorded draft, navigate the
      list row/revision context and every editor section, switch EN/VI, open help,
      and add/move/remove one disposable content block. Pass if list status,
      revision, labels/help, translation state, repeated-control target and new
      focus position are announced predictably.
- [ ] `P9-M036` Create a disposable invalid draft with at least two validation
      groups and one unavailable future canonical value; run **Validate draft**,
      traverse the summary, and activate the first issue. Pass if severity and
      message are spoken, activation focuses the exact field, and unavailable
      values have a textual reason.
- [ ] `P9-M037` Change a title without saving, open **Preview as learner**, and
      navigate from the top of the preview. Pass if **Draft preview — not
      public** is announced before content, the unsaved title is present, and
      **Open public problem** is absent or disabled until publication.
- [ ] `P9-M038` Submit a valid draft for review, enter a required note, attempt
      another interaction while the transition is pending, approve, then open
      and cancel/confirm the publish dialog. Pass if status/history and required
      note are spoken, pending controls are disabled, errors are actionable,
      the permanent URL is announced, and focus returns to the publish trigger.
- [ ] `P9-M039` Open pending and assessed queue views, enter an assessment,
      navigate the submitted answer and snapshot rubric, select every criterion,
      save, create a stale correction conflict, and inspect decision history.
      Pass if groups/levels/comments/total/outcome/conflict and append-only
      versions have correct names, roles, state, and reading order.

Record any screen-reader/browser combination not run as a limitation. An axe
pass does not satisfy this section.

## 6. Physical keyboard verification

Start at the browser address bar and use only Tab, Shift+Tab, Enter, Space,
native arrow keys, and Escape until each journey is complete.

- [ ] `P9-M040` With the pointer put aside, start at the address bar and Tab/
      Shift+Tab through learner library, permanent detail, submission result,
      Studio list, editor/review, assessment queue, and assessment detail;
      operate every control with Enter/Space/native arrows. Pass if no action or
      information disclosure requires a pointer and no non-interactive element
      becomes an unexpected stop.
- [ ] `P9-M041` Repeat `P9-M040` first at normal display settings and then with
      the OS/browser high-contrast setting enabled. At every stop, visually
      locate focus and scroll sticky regions into/out of view. Pass if focus is
      always visible, distinguishable, and not covered by a header, footer,
      sheet, dialog, or sticky action region.
- [ ] `P9-M042` At 1440 px and 360 px, record the focus sequence from page start
      through the first result/editor section. Pass if it follows visible task
      order, mobile focus never enters hidden desktop filters/table controls,
      and desktop focus never enters the hidden mobile sheet.
- [ ] `P9-M043` Open learner feedback, mobile filters, publish, and archive
      dialogs by keyboard; cycle forward/backward, try Escape, cancel, then open
      again and confirm deliberately. Pass if focus wraps, Escape only closes a
      safe dialog, no publish/archive occurs from navigation alone, and close or
      completion returns focus to the initiating control.
- [ ] `P9-M044` In a disposable draft, keyboard-add two content blocks, move one,
      remove one, create a validation error, and activate its summary link. Pass
      if focus remains on a logical surviving/new control after each mutation
      and the validation link lands on the exact invalid field.
- [ ] `P9-M045` From the oldest pending assessment, select every rubric level,
      enter optional feedback, save, reopen, and submit a correction using only
      keyboard commands. Pass if completion and correction succeed, the reason
      is required, and all prior decision history remains reachable.

## 7. Grayscale, contrast, zoom, and pilot display

Use the actual pilot display when possible. Record OS scaling, browser zoom,
resolution, projector/display model, and ambient-light constraints.

- [ ] `P9-M050` Enable the OS grayscale/color-filter setting, then visit learner
      filtered results/detail/result and Studio invalid editor/review/assessment
      states. Pass if selected stages/filters, status/evidence, validation
      severity, editorial/assessment states, disabled values, success, warning,
      and error are identifiable by text, labels, shape, border, or icon—not hue.
- [ ] `P9-M051` Display the same routes on the actual pilot monitor/projector at
      its intended brightness and ambient light; Tab through links, controls,
      disabled controls, and errors. Pass if text/control boundaries, link state,
      focus, disabled state, warning, and error remain visually distinguishable.
      Record the display model/settings and attach sanitized photographs if
      permitted.
- [ ] `P9-M052` Set browser text/page zoom to 200%, reload learner detail, Studio
      editor/review, and assessment detail, then complete their primary action.
      Pass if content remains readable/operable with no page-level horizontal
      scroll; record any intentional code/data region that scrolls internally.
- [ ] `P9-M053` Use browser responsive mode or windows measured at exactly 360,
      768, 1024, and 1440 CSS px; at each width open library filters/results,
      problem detail, Studio editor/review, assessment detail, and dialogs. Pass
      if below-768 cards, 768+ table, intermediate sidebar/filter placement,
      editor reflow, and sticky actions match `ui_release_0.md` without clipping
      or page-level overflow.
- [ ] `P9-M054` Set a 1280-CSS-px viewport to 400% browser zoom, reload the same
      representative routes, and reach each primary action. Pass if essential
      content/actions reflow and remain operable; document any content-type
      exception, exact overflow region, and accepted rationale rather than
      silently passing it.

## 8. Physical touch and pointer verification

Use at least one physical Android device and one physical iOS/iPadOS device if
available. Device emulation alone does not pass this section.

- [ ] `P9-M060` On each recorded physical device, tap every enabled stage, open
      filters, select/remove tokens, open two cards/disclosures, complete one
      response, report feedback, and continue. Pass if each intended target
      activates once and adjacent targets never activate accidentally.
- [ ] `P9-M061` Tap **Open filters**, focus a text/search field so the software
      keyboard appears, scroll to **Show N problems**, apply, reopen, then close
      with the UI control. Pass if the sheet uses the intended viewport, browser
      chrome/keyboard never hides the primary action, selections persist, and
      focus/visual context returns to **Open filters**.
- [ ] `P9-M062` On learner response/feedback and any securely available Studio
      text/note fields, place the caret in first/middle/last fields, cause a
      validation error, and attempt save/submit. Pass if the software keyboard
      scrolls the active field, message, and required action into view and no
      dialog control becomes unreachable.
- [ ] `P9-M063` While a filter and a partially completed disposable form are
      active, rotate portrait→landscape→portrait before submission and once
      during a pending request. Pass if readable layout and local input/filter
      state survive and the request/navigation occurs no more than once.
- [ ] `P9-M064` Slowly and rapidly scroll long library/editor/assessment pages,
      use sticky actions, tap a card/row disclosure and its nested control, and
      use OS back gestures. Pass if no gesture trap occurs, sticky content does
      not cover targets, disclosure taps do not navigate the row, and nested
      controls perform only their named action.

## 9. Privacy, no-auth boundary, and safe failure review

Use browser developer tools and sanitized request/response inspection. Do not
probe systems outside the local pilot environment.

- [ ] `P9-M070` Run
      `curl -i "http://127.0.0.1:3000/api/v1/vocabulary?vocabulary_type=PATHWAY_STAGE"`
      and `curl -i http://127.0.0.1:3000/api/v1/author/problems`. Pass if the
      public request succeeds, the author request returns the uniform public
      404 through Learn, and no author content or redirect to Studio is present.
- [ ] `P9-M071` With recorded disposable values, request a nonexistent slug, a
      draft slug, an archived slug, a problem/revision UUID in place of a slug,
      and a random attempt ID through public list/detail/result UI or `curl`.
      Pass if private variants are indistinguishable from a missing public
      resource and no error confirms which identifier type or record exists.
- [ ] `P9-M072` Put a unique harmless canary such as
      `manual-r0-p9-private-canary` into a disposable author note, private rubric
      guidance, and draft-only content. Inspect View Source, Network response
      bodies, visible errors, browser console, and
      `docker compose logs --no-color api`. Pass if the canary and all answer
      keys, hidden tests, exemplars, object keys, stack traces, SQL, provider
      detail, local paths, and credentials are absent from public surfaces/logs.
- [ ] `P9-M073` Submit one human-scored response and record its result URL in the
      original profile. Open that URL in a clean profile with no local receipt,
      then call `curl -i -H 'x-submission-receipt: wrong-receipt-value'
      http://127.0.0.1:8000/api/v1/submissions/ATTEMPT_ID` using the disposable
      attempt ID. Pass if both missing/wrong receipt paths give safe unavailable
      behavior without result data or existence detail and the valid receipt
      never appears in a URL, page, console, or response body.
- [ ] `P9-M074` In the feedback dialog try empty text and more than 2,000
      characters; in each response form try empty, malformed, and oversized
      input; then run the single automated abuse probe with
      `pnpm exec playwright test frontend/tests/e2e/learner-solving-loop.spec.ts
      --project=chromium --grep "bounded anonymous abuse"`. Pass if UI/API
      rejects bounded-input violations safely and any 429 response contains no
      moderation, storage, throttle-key, or infrastructure detail.
- [ ] `P9-M075` Run `docker compose ps --format json` and `ss -ltn`, and from a
      second LAN device attempt only the documented Learn address—not Studio,
      API, or PostgreSQL. Pass if Learn is reachable only as intentionally
      configured, ports 3001/8000/5432 are loopback-only, and the release owner
      signs that the no-auth pilot is not exposed as a public production system.

## 10. Health, observability, and operator recovery

- [ ] `P9-M080` Run `curl -i http://127.0.0.1:8000/health/live` and
      `curl -i http://127.0.0.1:8000/health/ready` while the stack is healthy.
      Pass if both are machine-readable and successful, liveness reports only
      process/platform health, readiness separately reports database/schema
      state, and neither exposes a database URL, host, exception, or migration
      implementation detail.
- [ ] `P9-M081` Run `bash scripts/health_dependency_check.sh` and monitor
      `docker compose ps` in another terminal. Pass if the script exits 0,
      liveness stays 200 during its controlled PostgreSQL pause, readiness
      becomes safe 503, PostgreSQL is always resumed by cleanup, and readiness
      returns to 200. If interrupted, immediately run `docker compose unpause
      postgres` followed by `bash scripts/dev_health.sh`.
- [ ] `P9-M082` Run `bash scripts/observability_check.sh`, retain its request ID
      and sanitized log line, then inspect `docker compose logs --no-color api`.
      Pass if exactly one matching request completion event has safe method,
      route template, status, outcome, duration, and environment fields and the
      script's supplied query value is absent.
- [ ] `P9-M083` Through disposable UI flows, publish once, submit once, report
      feedback once, and decide one assessment; after each action inspect
      `docker compose logs --no-color api`. Pass if each operation event has an
      event name, outcome, duration, safe canonical slug, request correlation,
      and one-way operation digest, while bodies, answers, notes, receipts, raw
      UUIDs/keys, SQL, filesystem paths, and object keys remain absent.
- [ ] `P9-M084` First record healthy live/ready responses; run `P9-M081` for the
      unavailable-database state; review the failed-migration/readiness evidence
      from `bash scripts/release0_verification.sh compose` rather than modifying
      the development schema. Pass if an operator can label all three states—
      healthy, dependency unavailable, schema outdated—from safe status/code
      fields and the learner receives no infrastructure detail.

## 11. Backup, restore, and deployment policy sign-off

Run only the isolated rehearsal; never restore over the active `ioai` database:

```bash
pnpm test:recovery-system
```

- [ ] `P9-M090` Before the rehearsal record
      `docker volume ls --format '{{.Name}}'`; run
      `set -o pipefail; /usr/bin/time -p pnpm test:recovery-system 2>&1 | tee
      /tmp/manual-r0-p9-recovery.log`; then list volumes again and run
      `bash scripts/dev_health.sh`. Pass if the log says fingerprints match,
      restore targets only `ioai_restore_verify`, the disposable database and
      `ioai-r0-recovery` volume are gone, and the development stack/volume is
      unchanged and healthy.
- [ ] `P9-M091` Two operators read `scripts/db_backup_restore.sh` together and
      run it with no arguments to view usage; inspect, but do not execute, the
      `restore`, `drop-restore`, and `reset` branches. Pass if both verify that
      restore/drop accept only `ioai_restore_*` plus exact database confirmation
      and reset resolves and exactly confirms
      `ioai-training-platform_postgres-data`; record both reviewer names.
- [ ] `P9-M092` Open the approved operations policy/provider console with the
      deployment owner, identify the exact backup bucket/vault/location,
      encryption mechanism/key owner, and read/write principals, and paste only
      the non-secret policy/ADR link into the record. Pass if encryption at rest
      and in transit and least-privilege access are approved and testable; never
      paste credentials or keys here.
- [ ] `P9-M093` Review the scheduler/provider configuration and monitoring with
      the operations owner; record backup frequency, retention, off-host copy
      frequency, restore-test frequency, named owner, failure alert, and
      escalation path in the fields below. Pass only if each value is concrete,
      approved, and has evidence such as an ADR, ticket, or sanitized schedule.
- [ ] `P9-M094` Record the approved RPO, start a timed disposable restore
      rehearsal using `P9-M090`, and compare the measured restore duration and
      newest recoverable backup age with the RTO/RPO. Pass if both objectives
      are met and the release owner signs the measured result; otherwise fail or
      accept a documented revised objective.
- [ ] `P9-M095` Read the recovery runbook with the release owner and inspect
      browser Local Storage for the learner profile before and after using a
      clean profile. Pass if the runbook explicitly says device-local progress
      and receipt indexes are absent from PostgreSQL backups, cannot be restored
      as account data, and retained server attempts still need the opaque
      learner receipt.

```text
Backup provider/location:
Encryption/access owner:
Backup frequency:
Retention:
Off-host schedule:
Restore rehearsal schedule:
RPO:
RTO and measured restore time:
Decision/ADR/issue link:
Approver:
```

## 12. Hosted CI and platform verification

- [ ] `P9-M100` Push the recorded commit or open its pull request, then use the
      GitHub Actions UI or run `gh run list --workflow release-0-ci.yml` and
      `gh run view RUN_ID`. Pass if the run uses a GitHub-hosted runner at the
      exact commit SHA and the `quality`, `postgres`, `browser`, `compose`, and
      `recovery` jobs all finish `success`; retain the run URL and ID.
- [ ] `P9-M101` For one successful run and, when available, one failed run, open
      the Actions **Artifacts** panel or run `gh run download RUN_ID -D
      /tmp/manual-r0-p9-ci-artifacts`. Pass if browser, Compose, and recovery
      artifact entries were attempted under `always()`, available failure
      screenshots/traces/reports can be opened, and retention matches the
      approved project policy.
- [ ] `P9-M102` Run
      `rg -n "NODE_VERSION|PNPM_VERSION|UV_VERSION|PLAYWRIGHT_VERSION|frozen"
      .github/workflows/release-0-ci.yml scripts/release0_verification.sh` and
      compare the output with the Actions setup logs. Pass if versions match the
      documented pins, installs use committed frozen locks, and Firefox/WebKit
      use the Playwright container matching the package version.
- [ ] `P9-M103` If macOS local operations are claimed, record macOS and Docker
      Desktop versions and run `bash scripts/release0_verification.sh compose`
      followed by `bash scripts/release0_verification.sh recovery` from a clean
      checkout. Pass if both exit 0, loopback publishing and host networking
      work, persisted counts match, and cleanup succeeds. If macOS is not
      claimed/available, record `NOT RUN` or unsupported—never `PASS`.
- [ ] `P9-M104` If Windows local operations are claimed, record Windows, Docker
      Desktop, WSL/shell, Git line-ending, and filesystem location; from the
      documented shell run the same Compose and recovery commands as `P9-M103`.
      Pass if both exit 0 without path, ownership, executable-bit, CRLF, network,
      or cleanup failures. Otherwise record `NOT RUN` or unsupported.
- [ ] `P9-M105` After each platform run, execute `docker compose ps`,
      `docker ps -a --filter name=ioai-r0-`, and
      `docker volume ls --filter name=ioai-r0-`; inspect API/Studio/PostgreSQL
      published addresses and the clean-checkout directory ownership. Pass if
      the development services remain healthy, protected ports are loopback,
      no reserved system/recovery container or volume remains, and no root-owned
      or line-ending-modified source artifact was created.

## 13. Final manual sign-off

Summarize every non-pass result. A required manual check may remain `NOT RUN`
for a documented environment limitation, but the release owner must explicitly
accept the limitation; it must not be represented as tested support.

| Area | Checks | Result | Evidence/defect/accepted limitation |
| --- | --- | --- | --- |
| Safety and deployed health | `P9-M001`–`P9-M013` | | |
| Current branded browsers | `P9-M020`–`P9-M024` | | |
| Screen reader | `P9-M030`–`P9-M039` | | |
| Physical keyboard | `P9-M040`–`P9-M045` | | |
| Grayscale/zoom/display | `P9-M050`–`P9-M054` | | |
| Physical touch | `P9-M060`–`P9-M064` | | |
| Privacy/no-auth boundary | `P9-M070`–`P9-M075` | | |
| Health and observability | `P9-M080`–`P9-M084` | | |
| Backup/recovery policy | `P9-M090`–`P9-M095` | | |
| Hosted CI/platforms | `P9-M100`–`P9-M105` | | |

Criterion mapping:

- `AC-R0-015-01`–`03`: `P9-M030`–`P9-M064`.
- `AC-R0-015-04`–`06`: `P9-M020`–`P9-M024`, plus the reviewed automated
  production timing evidence.
- `AC-R0-015-07`–`09`: `P9-M010`–`P9-M013` and `P9-M090`, plus the reviewed
  PostgreSQL/migration/transaction evidence.
- `AC-R0-015-10`–`13`: `P9-M070`–`P9-M075`.
- `AC-R0-015-14`: `P9-M090`–`P9-M095`.
- `AC-R0-015-15`–`16`: `P9-M080`–`P9-M084`.
- `AC-R0-015-17`–`19`: `P9-M010`–`P9-M013` and `P9-M100`–`P9-M105`.
- Critical `R0-011`–`R0-014` and `R0-017` journeys: `P9-M020`–`P9-M024`.

```text
Failures/blockers:

Checks not run and why:

Accepted limitations and approver:

Release decision: PASS / PASS WITH ACCEPTED LIMITATIONS / FAIL

Tester signature/date:
Accessibility reviewer signature/date:
Operations reviewer signature/date:
Release owner signature/date:
```

The known Phase 9 automated baseline limitations remain open until this manual
record closes or explicitly accepts them: physical screen-reader traversal,
physical touch, branded current-stable browsers, pilot-display confirmation,
GitHub-hosted workflow execution, non-Linux Docker Desktop behavior, and
production backup provider/retention/off-host policy.
