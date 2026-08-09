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
    };
    const draft = await request.post(`${apiBase}/author/problems`, { data: {} });
    expect(draft.ok()).toBeTruthy();
  });

  test('browse, filter, solve all five families, report feedback, restore progress, and continue', async ({ page }) => {
    await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Learner%20e2e`);
    await expect(page.getByRole('heading', { name: 'Problems' })).toBeVisible();
    await expect(page.getByRole('table', { name: 'Published problems' })).toBeVisible();
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
  });

  test('covers direct URLs, empty results, corrupt storage, draft isolation, and mobile cards', async ({ page, request }) => {
    await page.addInitScript(() => localStorage.setItem('ioai.learn.progress.v1', '{'));
    await page.goto(`${learnBase}/problems/${problems.single}`);
    await expect(page.getByRole('heading', { name: /Learner e2e/i })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Back to problem library' })).toHaveAttribute('href', '/problems');
    await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=no-such-published-problem`);
    await expect(page.getByRole('status', { name: 'No matching problems' })).toContainText('Clear filters');
    expect((await request.get(`${apiBase}/problems/not-published`)).status()).toBe(404);

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

async function publish(request: APIRequestContext, slug: string, type: string): Promise<string> {
  const createdResponse = await request.post(`${apiBase}/author/problems`, { data: {} });
  expect(createdResponse.ok(), await createdResponse.text()).toBeTruthy();
  const created = await createdResponse.json() as { problem_id: string; revision_id: string; version: number };
  const localized = (en: string, vi: string) => ({ en, vi, en_state: 'COMPLETE', vi_state: 'COMPLETE' });
  const response = responseConfiguration(type, localized);
  const save = await request.put(`${apiBase}/author/revisions/${created.revision_id}`, { data: {
    problem_id: created.problem_id, expected_version: created.version, client_save_key: `save-${slug}`, slug,
    content: { title: localized(`Learner e2e ${type}`, `Bài e2e ${type}`), summary: localized('Solve the published task.', 'Giải bài đã xuất bản.'), objectives: [localized('Calculate the correct response.', 'Tính đáp án đúng.')], blocks: [{ kind: 'STATEMENT', content: localized('Provide the correct response.', 'Cung cấp đáp án đúng.'), order: 1, reveal_order: null }] },
    metadata: { stage: ['PATHWAY_STAGE', 'AI_1_FOUNDATIONS'], difficulty: ['DIFFICULTY', 'EASY'], primary_competency: ['COMPETENCY', 'EVAL_METRICS'], secondary_competencies: [], task_type: ['TASK_TYPE', type], topics: [['TOPIC', 'EVAL_CONFUSION_MATRIX']], prerequisites: [], modalities: [['DATA_MODALITY', 'NONE']], expected_minutes: 10, resources: { compute_tier: ['COMPUTE_TIER', 'NONE'], runtime_class: ['RUNTIME_CLASS', 'INSTANT'], cpu_cores: 0, ram_mb: 0, gpu_count: 0, gpu_vram_mb: 0, storage_mb: 0, runtime_seconds: 0, network_policy: 'DENIED' } },
    response, scoring: { response_type: type, components: [{ method: type === 'SHORT_ANSWER' || type === 'CODE_FUNCTION' ? 'RUBRIC_HUMAN' : 'EXACT_MATCH', weight: '1.0', configuration: null }] },
  } });
  expect(save.ok(), await save.text()).toBeTruthy();
  await command(request, created.revision_id, 'submit-review', 2, `review-${slug}`);
  await command(request, created.revision_id, 'approve', 3, `approve-${slug}`);
  const published = await request.post(`${apiBase}/author/revisions/${created.revision_id}/publish`, { data: { expected_version: 4, note: 'Publish learner E2E.', actor_context: 'e2e-reviewer', idempotency_key: `publish-${slug}` } });
  expect(published.ok(), await published.text()).toBeTruthy();
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
