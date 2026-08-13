# Release 0 accessibility and responsive checklist

## Automated gate

Run `bash scripts/accessibility_check.sh` against a healthy local stack. The
gate creates isolated approved and published fixtures through the real API and
checks these representative surfaces:

- learner library and permanent problem detail;
- Studio problem list and structured editor/review;
- Studio assessment queue and assessment detail;
- WCAG 2.0/2.1 A and AA plus detectable WCAG 2.2 AA axe rules;
- 360, 768, 1024, and 1440 px viewports, the below-768 card/table switch, and
  absence of document-level horizontal overflow;
- 200% text zoom on learner detail, Studio editor, and assessment detail; and
- keyboard entry, focus wrapping, Escape dismissal, and trigger-focus return
  for learner feedback and publication confirmation dialogs.

The browser gate complements component tests for labeled feedback controls,
loading and empty `status` regions, safe error/retry UI, text-backed task status
and learning evidence, intermediate table disclosures, validation-to-field
focus, keyboard-named repeated controls, translation announcements, and
editorial status/history. Axe passing is not a claim of complete WCAG
conformance.

## Human-assisted checks automation cannot prove

Run this table before an observed pilot and after material navigation, content,
color, or responsive changes. Record browser/OS/assistive-technology versions,
route/fixture, result, defect link, and reviewer. A blank result is an explicit
unperformed check, never an implicit pass.

| Check | Procedure and pass condition | R0-09009 execution |
| --- | --- | --- |
| Screen reader | With current NVDA + Firefox or VoiceOver + Safari, traverse landmarks/headings, library filters/results, editor sections/validation, assessment decision, both dialogs, loading/error/status changes, and repeated-field add/reorder/remove. Names, roles, order, state, errors, and live updates must be understandable without visual context. | Not executable in the headless Linux container; required as an observed-pilot check. Automated role/name, focus, announcement, and axe evidence is recorded separately. |
| Grayscale/non-color | Apply OS grayscale (or browser rendering emulation) and inspect status/evidence, validation severity, selected filters/stages, pending/assessed state, disabled values, links, focus, success, and error UI. Every meaning must retain text, iconography, border, shape, or another non-color cue. | Representative learner/editor/assessment routes inspected using grayscale rendering on 2026-08-13; status and state remain text-backed. Re-run on the pilot display. |
| Keyboard interaction | From the address bar, use Tab/Shift+Tab, Enter/Space, arrow keys where native controls support them, and Escape. Reach every action, see focus, avoid traps except bounded modal wrapping, return focus after close, and preserve logical order after repeated-field changes and validation jumps. | Dialog behavior is browser-automated. Component tests cover repeated controls and validation jumps. Full physical-keyboard traversal remains required on the pilot OS/browser. |
| Touch/pointer | On a physical touch device or device lab, operate stage/filter controls, card links, disclosures, editor section links, repeated controls, sticky actions, assessment controls, and dialogs without accidental activation or obscured content. | Responsive browser automation proves visibility and overflow only; physical touch accuracy remains an observed-pilot check. |
| Text zoom/reflow | At 200% browser text size, traverse learner detail, editor/review, and assessment detail. Content and controls must remain operable without document-level horizontal scrolling; intentionally scrollable data/code regions may scroll internally. | Automated at a 1280 px viewport on Chromium and passing. |
| Breakpoint transition | Resize through 360, 768, 1024, and 1440 px. Confirm learner cards below 768, dense table at and above 768, intermediate filter/sidebar placement, readable editor/review/assessment layouts, and no clipped sticky actions. | Automated on Chromium and passing; visual pilot-display confirmation remains required. |

## Evidence record

- Automated command: `bash scripts/accessibility_check.sh`
- Browser project: Playwright Chromium
- Automated specification:
  `frontend/tests/e2e/accessibility-responsive.spec.ts`
- Local failure artifacts (ignored by Git): `test-results/` and
  `playwright-report/`
- Known limitation: this development container has no supported desktop screen
  reader or physical touch device. Those two human-assisted checks cannot be
  honestly marked passed here and remain explicit pilot-entry checks.
