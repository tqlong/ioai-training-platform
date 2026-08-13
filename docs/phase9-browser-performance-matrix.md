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
