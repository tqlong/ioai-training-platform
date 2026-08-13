import { expect, test, type APIRequestContext, type Page } from '@playwright/test';

const apiBase = process.env.API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const learnBase = process.env.LEARN_BASE_URL ?? 'http://127.0.0.1:3000';

test.describe.serial('Release 0 learner solving loop', () => {
  let problems: Record<string, string>;

  test.beforeAll(async ({ request }) => {
    const prefix = `learner-e2e-${Date.now()}`;
    problems = {
      single: await publish(request, `${prefix}-single`, 'QUIZ_SINGLE'),
      multiple: await publish(request, `${prefix}-multiple`, 'QUIZ_MULTIPLE'),
      numeric: await publish(request, `${prefix}-numeric`, 'NUMERIC_ANSWER'),
      short: await publish(request, `${prefix}-short`, 'SHORT_ANSWER'),
      code: await publish(request, `${prefix}-code`, 'CODE_FUNCTION'),
      archived: await publish(request, `${prefix}-archived`, 'QUIZ_SINGLE', true),
    };
    const draft = await request.post(`${apiBase}/author/problems`, { data: {} });
    expect(draft.ok()).toBeTruthy();
  });

  test('browse, filter, solve all five families, report feedback, restore progress, and continue', async ({ page }) => {
    await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Learner%20e2e`);
    await expect(page.getByRole('heading', { name: 'Problems' })).toBeVisible();
    if ((page.viewportSize()?.width ?? 1280) < 768) {
      await expect(page.getByRole('list', { name: 'Published problem cards' })).toBeVisible();
    } else {
      await expect(page.getByRole('table', { name: 'Published problems' })).toBeVisible();
    }
    await solve(page, problems.single, async () => page.getByRole('radio', { name: 'Correct' }).check(), 'Score: 1.0');
    await expect(page.getByRole('link', { name: /^Continue to / })).toHaveCount(1);

    await solve(page, problems.multiple, async () => {
      await page.getByRole('checkbox', { name: 'Correct', exact: true }).check();
      await page.getByRole('checkbox', { name: 'Also correct' }).check();
    }, 'Score: 1.0');
    await solve(page, problems.numeric, async () => page.getByRole('textbox', { name: 'Numeric answer' }).fill('0.3'), 'Score: 1.0');
    await solve(page, problems.short, async () => page.getByRole('textbox', { name: 'Short answer' }).fill('Reasoned answer'), 'waiting for assessment');
    await solve(page, problems.code, async () => page.getByRole('textbox', { name: 'Python code' }).fill('def solve(x):\n    return x'), 'waiting for assessment');

    const report = page.getByRole('button', { name: 'Report a problem' });
    await report.click();
    await page.getByRole('combobox', { name: 'Category' }).selectOption('TYPO');
    await page.getByRole('textbox', { name: 'Message' }).fill('The wording has a typo.');
    await page.getByRole('button', { name: 'Send feedback' }).click();
    await expect(page.getByText('Thank you. Your feedback was recorded.')).toBeVisible();
    await page.getByRole('button', { name: 'Close feedback' }).click();
    await expect(report).toBeFocused();

    await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Learner%20e2e`);
    await expect(page.getByText('Completed').first()).toBeVisible();
    await page.goto(`${learnBase}/submissions`);
    await expect(page.getByRole('link', { name: /Learner e2e/ })).toHaveCount(5);
  });

  test('restores bilingual search and hierarchical filters through a permanent URL', async ({ page }) => {
    const vietnameseSearch = `Bài e2e QUIZ_SINGLE ${problems.single}`;
    const libraryUrl = `${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=${encodeURIComponent(vietnameseSearch)}&topic=TOPIC_EVALUATION&include_subtopics=true&sort=TITLE`;
    const isMobile = (page.viewportSize()?.width ?? 1280) < 768;
    await page.goto(libraryUrl);
    if (isMobile) {
      await openMobileFilters(page);
    }
    await expect(page.getByRole('searchbox', { name: 'Search problems' })).toHaveValue(vietnameseSearch);
    await expect(page.getByRole('combobox', { name: 'Topic' })).toHaveValue('TOPIC_EVALUATION');
    await expect(page.getByRole('checkbox', { name: 'Include subtopics' })).toBeChecked();
    if (isMobile) {
      await page.getByRole('button', { name: 'Close filters' }).click();
    }
    const results = isMobile
      ? page.getByRole('list', { name: 'Published problem cards' })
      : page.getByRole('table', { name: 'Published problems' });
    const problemLink = results.locator(`a[href^="/problems/${problems.single}?"]`);
    await expect(problemLink).toBeVisible();
    await problemLink.click();
    const back = page.getByRole('link', { name: 'Back to problem library' });
    const backUrl = new URL(await back.getAttribute('href') ?? '', learnBase);
    expect(Object.fromEntries(backUrl.searchParams)).toMatchObject({
      stage: 'AI_1_FOUNDATIONS',
      q: vietnameseSearch,
      topic: 'TOPIC_EVALUATION',
      include_subtopics: 'true',
      sort: 'TITLE',
    });
    await back.click();
    await expect(page).toHaveURL(/\/problems\?/);
    if (isMobile) {
      await openMobileFilters(page);
    }
    await expect(page.getByRole('searchbox', { name: 'Search problems' })).toHaveValue(vietnameseSearch);
    await expect(page.getByRole('checkbox', { name: 'Include subtopics' })).toBeChecked();
  });

  test('covers direct URLs, empty results, corrupt storage, draft isolation, and mobile cards', async ({ page, request }) => {
    await page.addInitScript(() => localStorage.setItem('ioai.learn.progress.v1', '{'));
    await page.goto(`${learnBase}/problems/${problems.single}`);
    await expect(page.getByRole('heading', { name: /Learner e2e/i })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Back to problem library' })).toHaveAttribute('href', '/problems');
    await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=no-such-published-problem`);
    await expect(page.getByRole('status', { name: 'No matching problems' })).toContainText('Clear filters');
    expect((await request.get(`${apiBase}/problems/not-published`)).status()).toBe(404);
    expect((await request.get(`${apiBase}/problems/${problems.archived}`)).status()).toBe(404);

    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Learner%20e2e`);
    await expect(page.getByRole('list', { name: 'Published problem cards' })).toBeVisible();
    await page.getByRole('button', { name: 'Open filters' }).click();
    await expect(page.getByRole('button', { name: /Show \d+ problems/ })).toBeVisible();

    for (const width of [768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Learner%20e2e`);
      await expect(page.getByRole('table', { name: 'Published problems' })).toBeVisible();
      await expect(page.getByRole('list', { name: 'Published problem cards' })).toBeHidden();
    }
  });

  test('opens a prefetched warm problem detail within 500 ms without vocabulary fan-out', async ({ page }) => {
    const libraryUrl = `${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Learner%20e2e&sort=NEWEST`;
    await page.goto(`${learnBase}/problems/${problems.single}`);
    await expect(page.getByRole('heading', { name: /Learner e2e/i })).toBeVisible();
    await page.goto(libraryUrl);
    const problemLink = page.locator(`a[href^="/problems/${problems.single}?"]`).first();
    await expect(problemLink).toBeVisible();
    await page.waitForTimeout(500);

    let vocabularyRequests = 0;
    page.on('request', (request) => {
      if (request.url().includes('/api/v1/vocabulary')) vocabularyRequests += 1;
    });
    await page.evaluate((slug) => {
      const state = window as typeof window & {
        ioaiDetailVisible?: Promise<number>;
      };
      state.ioaiDetailVisible = new Promise((resolve) => {
        let startedAt: number | undefined;
        const observer = new MutationObserver(() => {
          if (startedAt === undefined) return;
          const heading = document.querySelector('main h1');
          if (heading?.textContent?.includes('Learner e2e')) {
            observer.disconnect();
            resolve(performance.now() - startedAt);
          }
        });
        document.addEventListener('click', (event) => {
          const link = event.target instanceof Element
            ? event.target.closest(`a[href*="/problems/${slug}"]`)
            : null;
          if (!link) return;
          startedAt = performance.now();
          observer.observe(document.body, { childList: true, subtree: true });
        }, { once: true });
      });
    }, problems.single);
    await problemLink.click();
    await page.waitForURL(new RegExp(`/problems/${problems.single}(?:\\?|$)`));
    await expect(page.locator('main').getByRole('heading', { name: /Learner e2e/i }))
      .toBeVisible();
    const clickToDetailMs = await page.evaluate(() => (
      window as typeof window & { ioaiDetailVisible: Promise<number> }
    ).ioaiDetailVisible);

    expect(vocabularyRequests).toBe(0);
    expect(clickToDetailMs).toBeLessThan(500);
  });

  test('keeps solving usable when storage and a submission dependency fail', async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(Storage.prototype, 'getItem', { value: () => { throw new Error('denied'); } });
      Object.defineProperty(Storage.prototype, 'setItem', { value: () => { throw new Error('denied'); } });
    });
    await page.goto(`${learnBase}/problems/${problems.single}`);
    await page.route('**/api/v1/problems/*/submissions', route => route.abort());
    await page.getByRole('radio', { name: 'Correct' }).check();
    await page.getByRole('button', { name: 'Submit answer' }).click();
    await expect(page.getByRole('alert').filter({ hasText: 'could not be assessed' })).toBeVisible();
    await expect(page.getByRole('radio', { name: 'Correct' })).toBeChecked();
  });

  test('returns a bounded anonymous abuse response without moderation details', async ({ request }) => {
    let response;
    for (let index = 0; index < 6; index += 1) {
      response = await request.post(`${apiBase}/problems/${problems.single}/feedback`, {
        data: { feedback_key: `abuse-${Date.now()}-${index}`, category: 'OTHER', message: 'Bounded report.' },
      });
    }
    expect(response?.status()).toBe(429);
    expect(await response?.text()).not.toMatch(/snapshot|moderation|traceback/i);
  });
});

async function solve(page: Page, slug: string, answer: () => Promise<unknown>, expected: string) {
  await page.goto(`${learnBase}/problems/${slug}?return_to=${encodeURIComponent('/problems?stage=AI_1_FOUNDATIONS')}`);
  await answer();
  await page.getByRole('button', { name: 'Submit answer' }).click();
  await expect(page.getByText(expected, { exact: false })).toBeVisible();
}

async function openMobileFilters(page: Page) {
  const open = page.getByRole('button', { name: 'Open filters' });
  const close = page.getByRole('button', { name: 'Close filters' });
  await expect(open).toBeVisible();
  await expect(async () => {
    if (await close.isVisible()) return;
    await open.click();
    await expect(close).toBeVisible({ timeout: 1_000 });
  }).toPass({ timeout: 5_000 });
}

async function publish(
  request: APIRequestContext,
  slug: string,
  type: string,
  archive = false,
): Promise<string> {
  const createdResponse = await request.post(`${apiBase}/author/problems`, { data: {} });
  expect(createdResponse.ok(), await createdResponse.text()).toBeTruthy();
  const created = await createdResponse.json() as { problem_id: string; revision_id: string; version: number };
  const localized = (en: string, vi: string) => ({ en, vi, en_state: 'COMPLETE', vi_state: 'COMPLETE' });
  const response = responseConfiguration(type, localized);
  const save = await request.put(`${apiBase}/author/revisions/${created.revision_id}`, { data: {
    problem_id: created.problem_id, expected_version: created.version, client_save_key: `save-${slug}`, slug,
    content: { title: localized(`Learner e2e ${type} ${slug}`, `Bài e2e ${type} ${slug}`), summary: localized('Solve the published task.', 'Giải bài đã xuất bản.'), objectives: [localized('Calculate the correct response.', 'Tính đáp án đúng.')], blocks: [{ kind: 'STATEMENT', content: localized('Provide the correct response.', 'Cung cấp đáp án đúng.'), order: 1, reveal_order: null }] },
    metadata: { stage: ['PATHWAY_STAGE', 'AI_1_FOUNDATIONS'], difficulty: ['DIFFICULTY', 'EASY'], primary_competency: ['COMPETENCY', 'EVAL_METRICS'], secondary_competencies: [], task_type: ['TASK_TYPE', type], topics: [['TOPIC', 'EVAL_CONFUSION_MATRIX']], prerequisites: [], modalities: [['DATA_MODALITY', 'NONE']], expected_minutes: 10, resources: { compute_tier: ['COMPUTE_TIER', 'NONE'], runtime_class: ['RUNTIME_CLASS', 'INSTANT'], cpu_cores: 0, ram_mb: 0, gpu_count: 0, gpu_vram_mb: 0, storage_mb: 0, runtime_seconds: 0, network_policy: 'DENIED' } },
    response, scoring: { response_type: type, pass_threshold: '1.0', components: [{ method: type === 'SHORT_ANSWER' || type === 'CODE_FUNCTION' ? 'RUBRIC_HUMAN' : 'EXACT_MATCH', weight: '1.0', configuration: type === 'SHORT_ANSWER' || type === 'CODE_FUNCTION' ? { criteria: [{ id: 'correctness', title: localized('Correctness', 'Tính đúng'), description: localized('Produces a correct and well-reasoned response.', 'Tạo câu trả lời đúng và có lập luận.'), maximum_points: '1', levels: [{ id: 'not-yet', label: localized('Not yet', 'Chưa đạt'), description: localized('The response is not yet correct.', 'Câu trả lời chưa đúng.'), points: '0' }, { id: 'complete', label: localized('Complete', 'Hoàn thành'), description: localized('The response is correct.', 'Câu trả lời đúng.'), points: '1' }] }], reviewer_guidance: 'Review the response.', exemplar: null } : null }] },
  } });
  expect(save.ok(), await save.text()).toBeTruthy();
  await command(request, created.revision_id, 'submit-review', 2, `review-${slug}`);
  await command(request, created.revision_id, 'approve', 3, `approve-${slug}`);
  const published = await request.post(`${apiBase}/author/revisions/${created.revision_id}/publish`, { data: { expected_version: 4, note: 'Publish learner E2E.', actor_context: 'e2e-reviewer', idempotency_key: `publish-${slug}` } });
  expect(published.ok(), await published.text()).toBeTruthy();
  if (archive) {
    const archived = await request.post(`${apiBase}/author/problems/${created.problem_id}/archive`, {
      data: {
        expected_version: 5,
        note: 'Archive learner E2E isolation fixture.',
        actor_context: 'e2e-reviewer',
        operation_id: `archive-${slug}`,
      },
    });
    expect(archived.ok(), await archived.text()).toBeTruthy();
  }
  return slug;
}

async function command(request: APIRequestContext, revision: string, action: string, version: number, operation: string) {
  const response = await request.post(`${apiBase}/author/revisions/${revision}/${action}`, { data: { expected_version: version, note: 'E2E editorial decision.', actor_context: 'e2e-reviewer', operation_id: operation } });
  expect(response.ok(), await response.text()).toBeTruthy();
}

function responseConfiguration(type: string, localized: (en: string, vi: string) => object) {
  if (type === 'QUIZ_SINGLE') return { type, choices: [{ id: 'a', content: localized('Correct', 'Đúng') }, { id: 'b', content: localized('Wrong', 'Sai') }], correct_choice_id: 'a' };
  if (type === 'QUIZ_MULTIPLE') return { type, choices: [{ id: 'a', content: localized('Correct', 'Đúng') }, { id: 'b', content: localized('Also correct', 'Cũng đúng') }, { id: 'c', content: localized('Wrong', 'Sai') }], correct_choice_ids: ['a', 'b'] };
  if (type === 'NUMERIC_ANSWER') return { type, expected: '0.3', absolute_tolerance: '0.001', unit: null };
  if (type === 'SHORT_ANSWER') return { type, reference_answer: localized('Reasoned answer', 'Câu trả lời'), accepted_keywords: [], rubric_guidance: 'Review reasoning.' };
  return { type, language: 'PYTHON', signature: 'def solve(x):', starter_code: 'def solve(x):\n    pass', public_tests: [{ id: 'public', invocation: 'solve(1)', expected: '1' }], hidden_tests: [{ id: 'hidden', invocation: 'solve(2)', expected: '2' }], rubric_guidance: 'Review code.' };
}
