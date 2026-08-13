# Release 0 browser and learner performance matrix

## Automated browser support

`bash scripts/learner_system_check.sh` runs the learner-critical matrix using
the browsers bundled with Playwright 1.55.0:

| Project | Release 0 coverage | Environment meaning |
| --- | --- | --- |
| `chromium` | Desktop learner journey | Playwright Desktop Chrome profile; Chromium 140.0.7339.16 |
| `firefox` | Desktop learner journey | Playwright Desktop Firefox profile; Firefox 141.0 |
| `webkit` | Desktop learner journey | Playwright Desktop Safari profile; WebKit 26.0 |
| `mobile-chrome` | Mobile learner journey | Pixel 7 viewport, touch, and mobile Chromium emulation |
| `mobile-safari` | Mobile learner journey | iPhone 15 viewport, touch, and mobile WebKit emulation |

Chromium projects run on the host. Firefox and WebKit projects run in the
matching pinned `mcr.microsoft.com/playwright:v1.55.0-noble` container because
the development host does not provide their shared-library dependencies and
does not grant sudo installation. The container uses host networking and the
same working tree and deployed API; it is not a separate test fixture.

The matrix covers enabled stage/library access, English and Vietnamese search,
ancestor-topic filtering with explicit descendants, canonical query restoration,
permanent/direct URLs, all five Release 0 response types, automated and pending
feedback, exactly one continuation, bounded device-local progress and submission
history, corrupt/unavailable storage, anonymous feedback, draft/archived
isolation, and recoverable submission failure.

Bundled engines and device emulation are deterministic CI evidence, not a claim
that Linux runs branded current-stable Chrome, macOS Safari, iOS Safari, or
Android Chrome. Those branded current-stable checks remain an explicit
environment-availability item for the final `R0-09016` baseline.

`bash scripts/author_system_check.sh` uses the same pinned desktop matrix for
the complete Studio create/edit/validate/preview/review/publish/revise/archive/
republish flow. Chromium additionally covers autosave failure and local
recovery, optimistic-conflict resolution, validation focus, and unavailable
canonical values. Pixel 7 mobile Chromium and iPhone 15 mobile WebKit provide
the smallest meaningful unsaved learner-preview and overflow checks; the local
Studio port remains a deployment boundary, not an authorization claim.

## Normal-broadband production profile

The same script stops the mounted development frontends, builds Learn with the
committed lockfile, and starts an isolated production server on loopback port
3100. Chromium DevTools emulation applies a cold cache, 40 ms latency, 10 Mbps
download, and 5 Mbps upload. Against at least 20 published public records it
requires:

- first meaningful library content (a published problem link) in less than
  2,000 ms from cold navigation; and
- a permanent detail heading plus enabled answer submission in less than
  3,000 ms from cold navigation.

The production check also scans the initial HTML for its private-draft marker
and internal draft/revision vocabulary, rejects account/authentication
handshakes, and proves pending submission feedback leaves the learning objective
readable. Timing annotations are attached to the Playwright result; failure
screenshots, traces, and the HTML report remain in ignored local artifact paths.

## R0-09010 execution record

On 2026-08-14, the host Chromium/mobile-Chrome group passed 8/8 cases in
30.3 seconds; the pinned container Firefox/WebKit/mobile-Safari group passed
12/12 in 50.3 seconds; and the browser-independent anonymous abuse check passed
1/1. The production run used 216 published records and measured 1,233 ms to
meaningful library content and 316 ms to usable permanent detail. Both budgets
passed without an account handshake or the private draft marker in initial
HTML.

The R0-09011 author run passed all 4 Chromium system cases in 43.3 seconds,
the complete Firefox/WebKit workflows in 49.2 seconds, mobile Chrome in 5.0
seconds, and mobile Safari in 6.4 seconds. No browser project was skipped.

`bash scripts/assessment_system_check.sh` owns the dedicated assessment matrix:
the complete snapshot/rubric/receipt/queue/result/correction system plus mixed
scoring/privacy in Chromium, the critical human/correction journey in Firefox
and WebKit, and storage-disabled keyboard/responsive use in both mobile profiles.
The R0-09012 run passed 3/3 Chromium cases in 16.5 seconds, the Firefox/WebKit
critical paths in 24.4 seconds, mobile Chrome in 6.2 seconds, and mobile Safari
in 7.3 seconds.

## R0-09016 aggregate execution record

On 2026-08-14, `bash scripts/release0_verification.sh all` reran the complete
configured matrix without a browser skip. The deployed accessibility suite
passed 4/4 in 48.2 seconds. Learner journeys passed 8/8 in Chromium/mobile
Chrome in 27.8 seconds and 12/12 in Firefox/WebKit/mobile Safari in 49.8
seconds; the abuse boundary passed 1/1 in 3.0 seconds. With 135 public records,
the cold production profile measured 816 ms to meaningful library content and
315 ms to usable permanent detail.

The author system passed 4/4 Chromium cases in 44.7 seconds, both complete
Firefox/WebKit lifecycles in 49.4 seconds, mobile Chrome in 4.9 seconds, and
mobile Safari in 6.1 seconds. Manual assessment passed 3/3 Chromium cases in
18.6 seconds, both critical Firefox/WebKit paths in 23.7 seconds, mobile Chrome
in 6.1 seconds, and mobile Safari in 7.0 seconds.

These results validate Playwright's pinned bundled engines and emulated Pixel 7
and iPhone 15 profiles. They do not replace branded current-stable browser,
physical-device touch, or pilot-display checks.
