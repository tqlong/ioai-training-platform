# Release 0 UI Design

## 1. Purpose

Release 0 is an editorial pilot for a small, carefully reviewed AI problem library. The interface should help two groups complete one simple loop:

- Learners: choose a stage, find a suitable problem, open it, and continue along a recommended path.
- Authors: draft a problem, apply canonical curriculum metadata, preview it as a learner, and move it through editorial review to publication.

The visual structure takes inspiration from the density and scanability of the [LeetCode problem set](https://leetcode.com/problemset/), but replaces competitive and company-oriented signals with curriculum stages, learning evidence, prerequisites, and recommendations.

`vocab.md` is the only source of truth for controlled vocabulary. Labels may be translated, but UI values and fixtures must store canonical codes.

## 2. Release 0 boundaries

### Included

- Public problem-set page with permanent links to published problems.
- Stage selection, search, compact filters, topic-family shortcuts, and a dense problem table.
- A prominent recommended next problem.
- Device-local task status for anonymous learners: `NOT_STARTED`, `ATTEMPTED`, or `COMPLETED`.
- A separate author interface for drafting, validating, previewing, reviewing, and publishing problems.
- Editorial status that is separate from learner task status.
- English-first labels with a Vietnamese label available where useful in selectors and search.

### Not included

- Learner or author accounts.
- Leaderboards, contests, streak pressure, social features, or organization management.
- Precise mastery claims or a `MASTERED` state.
- GPU execution, complex judging, dataset hosting, or advanced analytics dashboards.
- Editing the canonical vocabulary from inside the problem editor. Authors may flag a missing value for curriculum-owner review.

## 3. Product structure and access model

Use two applications in one repository so the public and editorial surfaces are unmistakably separate while sharing types, vocabulary data, and UI primitives.

```text
apps/
  learn/       public learner UI
  studio/      author/editor UI
packages/
  vocabulary/  generated structured data from vocab.md
  problems/    shared problem schema and validation
  ui/          shared visual primitives
```

Development endpoints:

| Surface | Default URL | Network exposure |
|---|---|---|
| Learner UI | `http://localhost:3000/problems` | May bind to `0.0.0.0` for classroom testing |
| Author Studio | `http://localhost:3001/author/problems` | Bind to loopback only |

Recommended scripts:

```text
dev:learn   start learner UI on port 3000
dev:studio  start author UI on port 3001, host 127.0.0.1
dev         start both applications
```

A different port is organization, not security. During Release 0, the Studio should remain local to an author's machine or on a private development network. Do not publicly deploy it without adding an access-control layer. The learner application reads only published problem snapshots; drafts must never be included in its build or public API responses.

## 4. Shared visual direction

The product should feel like a calm technical workbook rather than a competition dashboard.

- High information density with generous line height and clear grouping.
- Warm off-white page background; white content surfaces; dark navy text.
- Indigo as the primary action color; teal for completed/evidence states; amber for warnings and attempted work; coral only for destructive actions or validation failures.
- Rounded corners should be modest. Prefer crisp borders and subtle shadows over floating cards everywhere.
- Use a readable sans-serif UI typeface and a monospace face only for codes, identifiers, and code content.
- Icons always have text or an accessible label. Color never carries status by itself.
- Default desktop content width: approximately 1440 px. The problem table should use the available width before truncating meaningful learning information.

### Shared header

Learner UI:

```text
[IOAI Learn]  Problems  Study paths                         [EN / VI] [Feedback]
```

Author Studio:

```text
[IOAI Studio]  Problems  Review queue  Vocabulary       [Development only]
```

The two headers should use visibly different labels and accent colors so an author cannot mistake a draft preview for the public product.

## 5. Learner problem-set page

Route: `/problems`

### 5.1 Page hierarchy

```text
Global header

Problem library                                      progress summary
Choose what to practise next. Search all published problems.

Stage selector
[AI Foundations] [Competition Foundations] [High-school · Coming next]
[Collegiate · Coming next] [Open · Coming next]

Recommended next problem                             Weekly goal / path

Search and compact filters
Topic-family shortcuts

Problem table                                        Learning-path sidebar

Pagination / result count
```

The first viewport should contain the stage selector, recommendation, and the beginning of the problem list. Avoid a large marketing hero.

### 5.2 Stage selector

Show the five canonical stages in curriculum order:

- `AI_1_FOUNDATIONS` — AI Foundations
- `AI_2_COMPETITION_FOUNDATIONS` — Competition Foundations
- `AI_3_HIGHSCHOOL` — High-school Competition
- `AI_4_STUDENT` — Collegiate Competition
- `AI_OPEN` — Open / Cross-level

For the pilot, AI Foundations and Competition Foundations are selectable. Later stages may remain visible as “Coming next,” but disabled controls must explain why they are unavailable. The selected stage scopes recommendations and difficulty interpretation; it is not merely another tag.

### 5.3 Recommended next problem

Use one horizontal feature card, not a carousel.

Example content:

```text
CONTINUE YOUR PATH · 3 OF 8
Precision, recall, and F1 from a confusion matrix
Implement metric calculations and explain the trade-off between precision and recall.
AI Foundations · Easy   25 min   Browser
[Continue problem]  [Why this?]
```

For anonymous users with no local history, label the card “Recommended start” and use the editorially chosen first problem. “Why this?” opens a small popover with plain-language reasons such as stage match and prerequisites, without claiming personalization.

### 5.4 Search and filters

Keep filters on one compact row on desktop:

```text
[Search titles, objectives, topics…] [Stage] [Topic] [Difficulty] [Type] [More filters] [Clear]
```

- Search covers English and Vietnamese labels plus approved aliases, while selections store canonical codes.
- Topic opens a searchable hierarchical picker: family → intermediate category → leaf topic.
- A parent topic includes descendants only when the user explicitly enables “Include subtopics.”
- `More filters` contains primary competency, task status, learning evidence, expected time, and compute tier.
- Active filters appear as removable tokens below the row.
- The URL query string stores the current filter state so a filtered library can be shared.

Immediately below, show only the eight top-level topic families as shortcuts. Never render the entire topic vocabulary as a flat chip cloud.

### 5.5 Problem table

Desktop columns:

| Column | Content and behavior |
|---|---|
| Status | Icon plus accessible text for `NOT_STARTED`, `ATTEMPTED`, or `COMPLETED` |
| Evidence | `INTRODUCED`, `PRACTICED`, `APPLIED`, or `PROFICIENT`; display `—` when no evidence exists |
| Problem | Title, permanent short ID, and one-line observable learning objective |
| Stage · Difficulty | Always presented together, for example “AI Foundations · Easy” |
| Primary competency | One canonical competency label |
| Topics | At most two leaf-topic chips, then `+N` for the remainder |
| Type | Short label such as “Function” or “Single answer” |
| Time | Exact expected minutes |
| Compute | None, Browser, or Light CPU for the pilot |

Row rules:

- Clicking the title or row opens the permanent problem URL; interactive controls within the row do not trigger navigation.
- Preserve the user’s filtered list position when they return from a problem.
- Default sort is editorial learning-path order, then difficulty. Optional sorts are newest, expected time, and title.
- Sticky table header on long lists.
- Zebra striping should be very subtle; use a stronger hover/focus row treatment.
- Never show task completion and learning evidence as the same indicator.

Example row:

```text
○  —  Confusion Matrix Basics                         AI Foundations · Introductory
      Calculate TP, FP, TN, and FN from predictions.  Evaluation Metrics
      Confusion Matrix · Accuracy +1                  Quiz · 10 min · None
```

### 5.6 Learning-path sidebar

Replace LeetCode-style company or popularity modules with curriculum guidance:

1. Weekly goal — locally stored target and completed count.
2. Current path — current unit and progress, with a “View path” action.
3. Prerequisites to review — no more than three concrete topics.
4. Recently completed — last three problems from local history.
5. Suggested next topics — two topic-family or leaf-topic links.

The sidebar is supportive, not mandatory. On narrower screens it moves below the recommendation and above the list.

### 5.7 Empty, loading, and error states

- No local history: show the recommended starting problem; do not show zeros as failure.
- No filter results: state which filters are active and offer “Clear filters.”
- Loading: retain the page skeleton and table dimensions to avoid layout shift.
- Public data unavailable: show a retry action and a link to send feedback. Do not expose draft or infrastructure details.
- Local storage unavailable: the library still works; explain that progress will not persist on this device.

### 5.8 Responsive behavior

- At 1024–1279 px, move the sidebar below the recommended card and hide competency/evidence columns behind row details.
- Below 768 px, replace the table with compact problem cards.
- Mobile cards must still display title, status, stage · difficulty, primary topic, type, and expected time.
- Filters open in a full-height sheet with “Show N problems” as the primary action.
- All controls must work by keyboard, touch, and screen reader.

## 6. Author problem editor

Routes:

```text
/author/problems                 author problem list
/author/problems/new             new draft
/author/problems/:id/edit        edit existing draft or revision
/author/problems/:id/preview     learner-format preview
```

Keep all Studio routes under `/author`. This allows the learner and author
surfaces to move into one application later without changing their URLs or
creating a collision with the learner-facing `/problems` route.

### 6.1 Editor layout

Use a three-part workspace on desktop:

```text
Top bar: breadcrumb · draft status · validation status · preview · save

Left rail                  Main editor                         Right rail
1 Basics                   Current section fields              Validation
2 Content                                                        checklist
3 Response & scoring                                            Editorial notes
4 Curriculum metadata                                          Publication
5 Resources
6 Review & publish

Bottom sticky bar: [Save draft] [Preview as learner] [Submit for review]
```

The editor is a structured authoring form, not a raw JSON or Markdown document. Long-form content may use a focused Markdown editor with a rendered preview.

### 6.2 Editorial states

Editorial status must use its own vocabulary and must never reuse learner task status:

```text
DRAFT → IN_REVIEW → CHANGES_REQUESTED → APPROVED → PUBLISHED → ARCHIVED
```

Release 0 may implement these as simple fields and buttons rather than role-based permissions. Every transition records time and an author-entered note. Publishing is blocked until validation passes.

### 6.3 Section 1 — Basics

Fields:

- Internal problem ID: generated, stable, read-only after creation.
- URL slug: generated from English title, editable before first publication, uniqueness checked.
- English title and Vietnamese title.
- English and Vietnamese one-sentence summary.
- One or more learning objectives using observable verbs.
- Expected minutes: positive integer with derived duration label.

Inline guidance should show good objective syntax: “Observable verb + knowledge or skill + conditions or constraints.” Warn on vague verbs such as “know,” “learn,” or “understand.”

### 6.4 Section 2 — Content

Structured blocks in learner reading order:

1. Problem statement.
2. Dataset or provided information.
3. Examples.
4. Constraints and assumptions.
5. Hints, each with a reveal order.
6. Explanation or reference solution.
7. Recommended next problem.
8. Feedback prompt.

Each block supports English and Vietnamese content, but the author may mark a translation as pending. The preview should make missing translations visible to authors without exposing warnings on the public page.

### 6.5 Section 3 — Response and scoring

The selected canonical task type determines the response form:

- `QUIZ_SINGLE`: choices and exactly one correct answer.
- `QUIZ_MULTIPLE`: choices and one or more correct answers.
- `NUMERIC_ANSWER`: value, tolerance, and unit.
- `SHORT_ANSWER`: reference answer and manual/keyword guidance.
- `CODE_FUNCTION`: language, function signature, starter code, public cases, and hidden cases.
- Other vocabulary values may be displayed as unavailable for Release 0 rather than deleted from the vocabulary.

Scoring components use canonical methods and must total `1.0`. The editor displays both component weights and their sum. For the pilot, prefer `EXACT_MATCH`, `UNIT_TESTS`, `PARTIAL_TESTS`, or `RUBRIC_HUMAN`.

### 6.6 Section 4 — Curriculum metadata

Required single-select fields:

- Pathway stage.
- Difficulty.
- Primary competency.
- Task type.

Optional or multi-select fields:

- Up to three secondary competencies.
- Topics selected through the searchable hierarchy.
- Data modalities, with `NONE` mutually exclusive with actual modalities.
- Typed prerequisites: relationship, target type, target ID, and optional minimum evidence.

Important UI rules:

- Stage and difficulty are separate inputs but always previewed together.
- Topic breadcrumbs show the hierarchy, for example “Evaluation / Evaluation Analysis and Decisions / Confusion Matrix.”
- Prefer leaf topics; warn when an intermediate category is selected and a more specific descendant exists.
- Competency and topic searches show their vocabulary type because identical codes or labels may exist in both vocabularies.
- Store `(vocabulary_type, code)`, never a display label alone.
- Authors can select “Can’t find the right value?” to record a proposal note, but the proposal cannot be published as task metadata.

### 6.7 Section 5 — Resources

Fields:

- Compute tier and runtime class.
- Exact limits: CPU cores, RAM, GPU count/VRAM, storage, runtime seconds, and network access.
- Data modality and origin when a dataset is present.
- Download/resource links for pilot materials.

Release 0 warns on any GPU tier or unsupported task type and blocks public publication if the current release policy disallows it.

### 6.8 Section 6 — Review and publish

Show a grouped checklist:

```text
Content          title, objective, statement, answer area
Curriculum       stage, difficulty, competency, leaf topics, prerequisites
Assessment       valid scoring weights, answer/test data
Resources        allowed compute, numeric limits, network policy
Publication      unique slug, learner preview, editorial approval
```

Each failing item links back to its field. Warnings allow review but not necessarily publication; errors block publication. The primary action changes by state: “Submit for review,” “Request changes,” “Approve,” or “Publish.” Publishing requires a confirmation dialog that shows the permanent public URL and clearly distinguishes it from Preview.

### 6.9 Preview behavior

- Preview uses the learner problem-page layout and learner labels.
- A persistent striped banner says “Draft preview — not public.”
- Preview reads the unsaved editor state so authors can inspect changes before saving.
- Desktop and mobile preview widths are available without opening a public URL.
- Links from preview to the public problem are disabled until publication.

### 6.10 Autosave and conflict behavior

- Autosave local edits after a short idle period and show `Saving…`, `Saved`, or `Save failed` in the top bar.
- Keep a recoverable local draft if the server save fails.
- Warn before leaving with unsaved changes.
- If a stored problem changed since the editor opened it, do not silently overwrite it. Offer “Reload latest” and “Copy my changes.” Full collaborative editing is outside Release 0.

## 7. Author problem list

Although the problem editor is the main author page, authors need a lightweight entry list at `/author/problems` on port 3001.

Columns:

```text
Status | Problem | Stage · Difficulty | Type | Owner | Updated | Validation | Actions
```

Default tabs are Drafts, In review, Published, and All. Search covers title, ID, slug, and canonical codes. Row actions are Edit, Preview, Duplicate as draft, and Archive. “New problem” is the only primary action.

## 8. Core interaction rules

- Use visible labels; placeholders are examples, not labels.
- Preserve focus after adding or removing repeated fields.
- Validation messages state the problem and the corrective action.
- Confirm only destructive or externally visible actions such as archive and publish.
- Save buttons never imply publication.
- Tooltips may clarify terms, but essential instructions must remain visible.
- All dialogs trap focus, close with Escape when safe, and return focus to their trigger.
- Meet WCAG 2.2 AA contrast and interaction requirements.

## 9. Data and state separation

Keep these concepts separate throughout the UI and data model:

| Concept | Example | Used by |
|---|---|---|
| Learner task status | `ATTEMPTED` | Learner progress |
| Learning evidence | `PRACTICED` | Curriculum guidance |
| Editorial status | `IN_REVIEW` | Author workflow |
| Publication state | published snapshot/version | Public visibility |

The public learner UI receives only published snapshots. Editing a published problem creates a new draft revision; the live version remains unchanged until the revision is approved and published.

## 10. Suggested Release 0 acceptance criteria

### Learner page

- A learner can select an enabled stage, search, apply filters, and open a permanent problem URL.
- Every problem displays stage and difficulty together.
- No row shows more than two topic chips before `+N`.
- Topic search is hierarchical and supports English, Vietnamese, and approved aliases.
- Anonymous progress survives a page refresh when local storage is available.
- Task status and learning evidence have distinct labels and visual treatments.
- The page is usable at 360 px, 768 px, 1024 px, and 1440 px widths.

### Author page

- An author can create, save, reopen, preview, validate, review, and publish a problem.
- Controlled fields store canonical codes from `vocab.md`.
- Invalid topic parents, missing required fields, disallowed Release 0 values, and scoring weights not totaling `1.0` block publication.
- Draft content never appears in the learner application's list or public endpoints.
- The author app binds only to `127.0.0.1` by default and uses a separate port.
- Preview is clearly marked as non-public.

## 11. Recommended implementation sequence

1. Parse or transcribe `vocab.md` into validated structured data and add invariants for composite identity and topic hierarchy.
2. Define the shared problem schema, editorial status, and publication snapshot model.
3. Build the public problem-set page with realistic Release 0 fixtures.
4. Build the author list and structured editor against the same schema.
5. Add learner preview, validation checklist, and publish flow.
6. Verify responsive behavior, keyboard operation, bilingual search, and strict draft/public separation.
