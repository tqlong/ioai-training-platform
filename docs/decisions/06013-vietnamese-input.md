# R0-06013 Vietnamese input decision

Date: 2026-08-09

Release 0 does not embed a browser-side Telex converter. The package review
found no React/browser package with sufficient release history, adoption,
maintenance evidence, provenance, composition-event coverage, and controlled-
input tests to satisfy the Phase 6 stability gate.

`gotiengviet` was rejected for Release 0 because it is a recent package with
minimal demonstrated production adoption. AVIM-derived scripts were rejected
because their browser assumptions and maintenance history do not establish
compatibility with modern controlled React inputs. The mature UniKey engine has
long-lived provenance and broad operating-system use, but it is not distributed
as a maintained React/browser package.

The Studio therefore uses ordinary Unicode inputs and composition events and
supports native operating-system input methods, including UniKey and Simple
Telex. The Vietnamese editor explicitly explains this behavior. A browser Telex
toggle may be added only after a maintained package passes caret, selection,
undo/redo, paste, mobile, composition, native-IME interaction, accessibility,
license, provenance, and representative Vietnamese sequence tests.

Sources reviewed:

- <https://www.unikey.org/en/>
- <https://www.unikey.org/en/source.html>
- <https://github.com/duydev/gotiengviet-js>
