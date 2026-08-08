## Recommended product structure

Make the main experience:

> Choose a stage → receive a short recommended path → solve a problem → get feedback → continue to the next suitable problem.

- A dense, scannable problem list.
- Search and filters immediately above the list.
- Visible progress and completion state.
- Topic chips for quick exploration.
- Curated study plans alongside the full library.
- Very little information required before opening a problem.

The initial problemset page could contain:

1. **Stage selector**  
   AI Foundations, Competition Foundations, High-school Competition, Collegiate Competition, Open.

2. **Continue learning**  
   One prominent recommendation based on the learner’s current path.

3. **Problem table**

   | Column | Purpose |
   |---|---|
   | Task status | Not started, attempted, completed |
   | Learning evidence | Introduced, practiced, applied, proficient |
   | Problem | Title and short learning objective |
   | Stage · Difficulty | Always display together, as required by the vocabulary |
   | Primary competency | The main skill being assessed |
   | Topics | At most two visible, with the remainder collapsed |
   | Type | Quiz, code, experiment, analysis, etc. |
   | Time | Expected minutes |
   | Compute | Browser, light CPU, GPU, etc. |

4. **Compact filter bar**  
   Search, stage, competency, topic, difficulty, task type and “More filters.”

5. **Learning-path sidebar**  
   Replace LeetCode’s company-oriented sidebar with prerequisites, weekly goal, recently completed work and suggested next topics.

Do not show the complete topic vocabulary as chips. Show the top-level topic families defined in `vocab.md` and put their intermediate categories and leaf topics in a searchable hierarchical picker.

## Treat the taxonomy as curriculum infrastructure

[`vocab.md`](vocab.md) is the sole authoritative source for pathway stages, competencies, difficulty, task status, learning evidence, topics, task types, modalities, prerequisites, compute tiers, scoring methods, and learning-objective conventions. Product code, fixtures, and this master plan must reference its canonical codes instead of maintaining parallel vocabulary lists.

The topic taxonomy uses explicit root, intermediate, and leaf records. Each record stores a nested bilingual `labels: {en, vi}` object, and every non-root topic stores a `parent_code`. Markdown headings are presentation only and must not be interpreted as data relationships.

Vocabulary identity is the composite key `(vocabulary_type, code)`. A competency and topic may share a code or label, but they remain separate records throughout the database, APIs, imports, and analytics.

I would also distinguish these concepts in the interface:

- **Stage:** where the learner is in the pathway.
- **Competency:** what observable ability the task assesses.
- **Topic:** the concepts or methods involved.
- **Prerequisite:** what must or should be learned beforehand.
- **Difficulty:** challenge relative to the selected stage.

Most learners should mainly interact with stages and topics. Competencies can quietly power recommendations and progress reports.

Task status and learning evidence must remain separate:

- **Task status:** `NOT_STARTED`, `ATTEMPTED`, `COMPLETED`.
- **Learning evidence:** `INTRODUCED`, `PRACTICED`, `APPLIED`, `PROFICIENT`.
- Do not use `MASTERED` during the initial releases.

## Roll out vertically, not feature by feature

Each release should provide a complete learning loop to real users.

Vocabulary completeness and release availability are separate. `vocab.md` may define values required by later releases, but authors and learners may use only the values enabled for the current release. Future-facing canonical values should remain stable rather than being deleted or renamed because they are not yet exposed.

### Release 0 — Editorial pilot

Build the content system before the sophisticated judge:

- Canonical vocabulary stored as structured data.
- Simple task authoring and editorial review.
- Public task pages with permanent URLs.
- 20–30 carefully reviewed AI Foundations problems.
- Manual or lightweight automated scoring.
- Feedback form on every task.

Recruit 10–20 students and teachers. The goal is to validate content format, difficulty, vocabulary and navigation.

### Release 1 — Public learning library

Support task types that are inexpensive and reliable:

- Single/multiple-choice quizzes.
- Numeric and short answers.
- Small Python function problems.
- Debugging and code-completion tasks.
- Browser or light-CPU execution only.
- Anonymous solving, with optional accounts for saved progress.
- One curated “Start AI Foundations” path.

Release 1 publication is limited to the canonical task types `QUIZ_SINGLE`, `QUIZ_MULTIPLE`, `NUMERIC_ANSWER`, `SHORT_ANSWER`, `CODE_FUNCTION`, `CODE_DEBUGGING`, and `CODE_COMPLETION`, using the `NONE`, `BROWSER`, or `CPU_LIGHT` compute tier. The canonical task example in `vocab.md` must remain eligible under these constraints.

This is already a usable product. Do not wait for GPU training or leaderboards.

A good initial content target would be approximately:

- 30 AI Foundations tasks.
- 20 Competition Foundations tasks.
- 3–5 coherent learning sequences.
- At least 3 tasks for every competency you claim to measure.

### Release 2 — Learning guidance

Add the educational differentiation:

- Prerequisite-aware recommendations.
- “Why this problem is recommended.”
- Topic and competency progress.
- Hints with graduated disclosure.
- Explanations and reference solutions after completion.
- Personalized review queue.
- Bilingual search using labels and aliases.

Avoid claiming precise mastery. Report the evidence levels `INTRODUCED`, `PRACTICED`, `APPLIED`, and `PROFICIENT` only when supported by learner activity, and keep them separate from task completion status.

### Release 3 — Authentic AI tasks

Only after the basic loop is stable, add:

- Dataset downloads and hosted notebooks.
- Data-analysis submissions.
- Hidden-label prediction scoring.
- Controlled experiments and error-analysis tasks.
- CPU/GPU job queues.
- Reproducible environments and resource limits.
- Public/private evaluation splits.

Start with asynchronous jobs and clear runtime estimates. AI experiments do not need the instant feedback expected from ordinary coding problems.

### Release 4 — Competition layer

Add competitive mechanics last:

- Timed contests.
- Team challenges.
- Leaderboards.
- Submission limits and anti-leakage controls.
- Solution defense and human-assessed rubrics.
- Seasonal or school-based events.

Leaderboards introduced too early can reward prior expertise and metric gaming instead of learning.

## The first problem page

Keep the initial version focused:

- Title and stage/difficulty.
- One-sentence learning objective.
- Prerequisites.
- Problem statement.
- Dataset or examples.
- Starter code or response area.
- Run and submit actions.
- Test/score feedback.
- Hints.
- Explanation.
- Recommended next problem.

Put detailed taxonomy metadata in a collapsible section. It is important to the system, but should not dominate the learner’s attention.

## What to measure

For the pilot, avoid vanity metrics such as total registrations. Track:

- Percentage starting a first problem.
- Percentage completing a first problem.
- Percentage beginning the recommended next problem.
- Completion rate by stage and difficulty.
- Median completion time versus `expected_minutes`.
- Attempts and hints used.
- Where learners abandon a task.
- Incorrect-answer patterns.
- Tags that authors or learners frequently find misleading.
- Seven-day return rate.

Review this evidence before expanding pathway stages, task types, scoring methods, or compute tiers. In particular, do not introduce GPU workloads or competition mechanics merely because their vocabulary values already exist.

The most useful early signal is likely:

> Among learners who finish one problem, how many begin the recommended next problem?

That measures whether you have created a learning journey rather than merely a searchable repository.

## Vocabulary and publication governance

- New competency values require curriculum-owner approval.
- Enforce uniqueness on `(vocabulary_type, code)`; `code` alone does not need to be globally unique across vocabulary types.
- Every non-root topic must reference an existing parent in the `TOPIC` vocabulary. Reject missing parents, self-parenting, and cycles.
- New topics must not duplicate an existing canonical label or approved alias within the same parent branch.
- Authors may propose vocabulary values, but unapproved or release-ineligible values must not appear on published tasks.
- Validate every task against the canonical structured vocabulary before publication.
- Review task metadata during editorial review and again after pilot evidence is collected.
- Recalibrate difficulty using completion rate, attempts, elapsed time, hints used, and prerequisite evidence; always interpret difficulty relative to pathway stage.
- Deprecate vocabulary values instead of reusing or silently changing their codes.
- Preserve English and Vietnamese aliases for renamed labels. Within a search context, an alias must resolve to exactly one active canonical topic.

## My strongest recommendation

Launch with **AI Foundations + Competition Foundations only**, a polished problem list, about 50 strong tasks, and one complete guided path. Keep the other stages visible as “coming next” only if you want to communicate the long-term pathway.

The defensible advantage is not a LeetCode-like table or an online judge. It is the combination of:

> curated tasks + explicit prerequisites + competency evidence + a trustworthy next recommendation.

The best next design artifact would be a small product specification covering the problem-list page, problem page, taxonomy schema and the exact scope of Release 1.
