import {
  expect,
  test,
  type APIRequestContext,
  type APIResponse,
  type Page,
} from '@playwright/test';

import { createHumanProblem } from './support/system-fixture';

const apiBase = process.env.API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const learnBase = process.env.LEARN_BASE_URL ?? 'http://127.0.0.1:3000';
const studioBase = process.env.STUDIO_BASE_URL ?? 'http://127.0.0.1:3001';

test('runs the snapshot-bound human queue, result, and correction journey', async ({ page, request }) => {
  const slug = `assessment-system-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const published = await createHumanProblem(request, slug, 'PUBLISHED');

  await page.goto(`${learnBase}/problems/${slug}`);
  await page.getByRole('textbox', { name: 'Short answer' }).fill('Old snapshot answer.');
  const submittedResponse = page.waitForResponse(response => (
    response.url().includes(`/api/v1/problems/${slug}/submissions`)
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Submit answer' }).click();
  const firstSubmission = await submittedResponse;
  await expectApiOk(firstSubmission);
  const first = await firstSubmission.json() as { attempt_id: string; receipt: string };
  await expect(page.getByText('waiting for assessment', { exact: false })).toBeVisible();
  const localHistory = await page.evaluate(() => JSON.parse(
    localStorage.getItem('ioai.learn.submissions.v1') ?? '[]',
  ) as Array<Record<string, unknown>>);
  expect(localHistory[0]).toMatchObject({ attemptId: first.attempt_id, receipt: first.receipt, slug });
  expect(first.receipt).toMatch(/^[0-9a-f-]{20,}$/i);
  await expect(page.locator('body')).not.toContainText(first.receipt);

  const secondReceipt = `second-private-${slug}`;
  const secondResponse = await request.post(`${apiBase}/problems/${slug}/submissions`, {
    data: {
      submission_key: `second-${slug}`,
      receipt: secondReceipt,
      response: { type: 'SHORT_ANSWER', text: 'Second pending answer.' },
    },
  });
  await expectApiOk(secondResponse);
  const second = await secondResponse.json() as { attempt_id: string };

  const pendingQueue = await request.get(
    `${apiBase}/author/assessments?status=PENDING&problem=${slug}&limit=10`,
  );
  await expectApiOk(pendingQueue);
  expect((await pendingQueue.json()).items.map((item: { attempt_id: string }) => item.attempt_id))
    .toEqual([first.attempt_id, second.attempt_id]);

  await publishChangedSuccessor(request, published.problemId, slug);
  await page.goto(`${studioBase}/author/assessments`);
  await page.getByRole('textbox', { name: 'Problem slug' }).fill(slug);
  const queueLinks = page.locator(`a[href^="/author/assessments/"]`);
  await expect(queueLinks).toHaveCount(2);
  expect(await queueLinks.evaluateAll(links => links.map(link => link.getAttribute('href'))))
    .toEqual([
      `/author/assessments/${first.attempt_id}`,
      `/author/assessments/${second.attempt_id}`,
    ]);
  await queueLinks.first().click();
  await expect(page.getByRole('heading', { name: `Accessible system problem ${slug}` }))
    .toBeVisible();
  await expect(page.getByRole('heading', { name: 'Published rubric' })).toBeVisible();
  await expect(page.getByText('Reasoning', { exact: true })).toBeVisible();
  await expect(page.getByText('New revision criterion', { exact: true })).toHaveCount(0);

  const complete = page.getByRole('radio', { name: /Complete — 1 points/ });
  await complete.focus();
  await page.keyboard.press('Space');
  await expect(complete).toBeChecked();
  await page.getByRole('textbox', { name: 'Criterion feedback (optional)' })
    .fill('Snapshot rubric feedback.');
  await page.getByRole('textbox', { name: 'Overall learner feedback (optional)' })
    .fill('Safe learner feedback.');
  page.once('dialog', dialog => dialog.accept());
  await page.getByRole('button', { name: 'Complete assessment' }).click();
  await expect(page.getByText('Assessment saved.')).toBeVisible();

  await page.goto(`${learnBase}/submissions`);
  await page.locator(`a[href="/submissions/${first.attempt_id}"]`).click();
  await expect(page.getByText('Passed', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Rubric result' })).toBeVisible();
  await expect(page.getByText('Safe learner feedback.')).toBeVisible();

  const assessedDetail = await request.get(`${apiBase}/author/assessments/${first.attempt_id}`);
  await expectApiOk(assessedDetail);
  const assessed = await assessedDetail.json() as {
    latest_decision: { decision_id: string };
  };
  const stale = await request.post(
    `${apiBase}/author/assessments/${first.attempt_id}/decisions`,
    { data: {
      selections: [{
        component_index: 0,
        criterion_id: 'reasoning',
        level_id: 'not-yet',
        feedback: null,
      }],
      expected_decision_id: 'stale-decision',
      correction_reason: 'Stale concurrent correction.',
    } },
  );
  expect(stale.status()).toBe(409);

  await page.goto(`${studioBase}/author/assessments/${first.attempt_id}`);
  await page.getByRole('radio', { name: /Not yet — 0 points/ }).check();
  await page.getByRole('textbox', { name: 'Correction reason' })
    .fill('Correct the recorded rubric level.');
  page.once('dialog', dialog => dialog.accept());
  await page.getByRole('button', { name: 'Save correction' }).click();
  await expect(page.getByText('Assessment saved.')).toBeVisible();
  await expect(page.getByText(/Version 1/)).toBeVisible();
  await expect(page.getByText(/Version 2/)).toBeVisible();

  await page.goto(`${learnBase}/submissions/${first.attempt_id}`);
  await expect(page.getByText('Assessed — not yet passed')).toBeVisible();
  const finalDetail = await request.get(`${apiBase}/author/assessments/${first.attempt_id}`);
  await expectApiOk(finalDetail);
  expect((await finalDetail.json()).decision_history).toHaveLength(2);
  expect(assessed.latest_decision.decision_id).toBeTruthy();
});

test('preserves the automated part of mixed scoring and redacts private rubric data', async ({ request }) => {
  const slug = `assessment-mixed-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  await createHumanProblem(request, slug, 'PUBLISHED', 'MIXED');
  const receipt = `mixed-private-${slug}`;
  const pendingResponse = await request.post(`${apiBase}/problems/${slug}/submissions`, {
    data: {
      submission_key: `mixed-${slug}`,
      receipt,
      response: { type: 'QUIZ_SINGLE', choice_id: 'correct' },
    },
  });
  await expectApiOk(pendingResponse);
  const pending = await pendingResponse.json() as {
    attempt_id: string;
    components: Array<{ method: string; score: string; weight: string }>;
  };
  expect(pending.components).toEqual([
    expect.objectContaining({ method: 'EXACT_MATCH', score: '1.0', weight: '0.4' }),
  ]);

  expect((await request.get(`${apiBase}/submissions/${pending.attempt_id}`)).status()).toBe(422);
  expect((await request.get(`${apiBase}/submissions/${pending.attempt_id}`, {
    headers: { 'X-Submission-Receipt': 'wrong-private-receipt' },
  })).status()).toBe(404);

  const authorDetailResponse = await request.get(
    `${apiBase}/author/assessments/${pending.attempt_id}`,
  );
  await expectApiOk(authorDetailResponse);
  expect(await authorDetailResponse.text()).toContain('Private guidance must remain private.');
  const firstDecision = await request.post(
    `${apiBase}/author/assessments/${pending.attempt_id}/decisions`,
    { data: {
      selections: [{
        component_index: 1,
        criterion_id: 'reasoning',
        level_id: 'complete',
        feedback: 'Mixed human feedback.',
      }],
      overall_feedback: 'Mixed assessment complete.',
    } },
  );
  await expectApiOk(firstDecision);
  const firstPayload = await firstDecision.json() as {
    latest_decision: { decision_id: string; result: { components: Array<Record<string, unknown>> } };
  };
  const firstAutomated = automatedComponent(firstPayload.latest_decision.result.components);

  const correction = await request.post(
    `${apiBase}/author/assessments/${pending.attempt_id}/decisions`,
    { data: {
      selections: [{
        component_index: 1,
        criterion_id: 'reasoning',
        level_id: 'not-yet',
        feedback: null,
      }],
      expected_decision_id: firstPayload.latest_decision.decision_id,
      correction_reason: 'Correct only the human component.',
    } },
  );
  await expectApiOk(correction);
  const corrected = await correction.json();
  expect(automatedComponent(corrected.latest_decision.result.components)).toEqual(firstAutomated);
  expect(corrected.decision_history).toHaveLength(2);

  const publicResult = await request.get(`${apiBase}/submissions/${pending.attempt_id}`, {
    headers: { 'X-Submission-Receipt': receipt },
  });
  await expectApiOk(publicResult);
  expect(await publicResult.text()).not.toMatch(/Private guidance|exemplar|hidden/i);
});

test('keeps storage-disabled mobile submission and keyboard assessment usable', async ({ page, request }) => {
  const slug = `assessment-mobile-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  await createHumanProblem(request, slug, 'PUBLISHED');
  await page.addInitScript(() => {
    Object.defineProperty(Storage.prototype, 'getItem', {
      configurable: true,
      value: () => { throw new DOMException('blocked'); },
    });
    Object.defineProperty(Storage.prototype, 'setItem', {
      configurable: true,
      value: () => { throw new DOMException('blocked'); },
    });
  });
  await page.goto(`${learnBase}/problems/${slug}`);
  await page.getByRole('textbox', { name: 'Short answer' }).fill('Storage-free answer.');
  const submittedResponse = page.waitForResponse(response => (
    response.url().includes(`/api/v1/problems/${slug}/submissions`)
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Submit answer' }).click();
  const submitted = await submittedResponse;
  await expectApiOk(submitted);
  const { attempt_id: attemptId } = await submitted.json() as { attempt_id: string };
  await expect(page.getByText('waiting for assessment', { exact: false })).toBeVisible();
  await page.goto(`${learnBase}/submissions`);
  await expect(page.getByText('No submissions are stored on this device yet.')).toBeVisible();

  await page.goto(`${studioBase}/author/assessments/${attemptId}`);
  const complete = page.getByRole('radio', { name: /Complete — 1 points/ });
  await complete.focus();
  await page.keyboard.press('Space');
  await expect(complete).toBeChecked();
  const submit = page.getByRole('button', { name: 'Complete assessment' });
  await submit.focus();
  page.once('dialog', dialog => dialog.accept());
  await page.keyboard.press('Enter');
  await expect(page.getByText('Assessment saved.')).toBeVisible();
  await expectNoPageOverflow(page);
});

async function publishChangedSuccessor(
  request: APIRequestContext,
  problemId: string,
  slug: string,
) {
  const currentResponse = await request.get(`${apiBase}/author/problems/${problemId}`);
  await expectApiOk(currentResponse);
  const current = await currentResponse.json() as Record<string, unknown> & {
    revision_id: string;
    version: number;
  };
  const startedResponse = await request.post(`${apiBase}/author/problems/${problemId}/revisions`, {
    data: {
      source_revision_id: current.revision_id,
      expected_version: current.version,
      operation_id: `assessment-successor-${slug}`,
    },
  });
  await expectApiOk(startedResponse);
  const started = await startedResponse.json() as Record<string, unknown> & {
    problem_id: string;
    revision_id: string;
    version: number;
    content: Record<string, unknown> & { title: Record<string, unknown> };
    scoring: Record<string, unknown> & { components: Array<Record<string, unknown>> };
  };
  const changedContent = {
    ...started.content,
    title: { ...started.content.title, en: 'Newly published revision title' },
  };
  const changedComponents = started.scoring.components.map(component => (
    component.method === 'RUBRIC_HUMAN' ? {
      ...component,
      configuration: {
        ...(component.configuration as Record<string, unknown>),
        reviewer_guidance: 'New private successor guidance.',
        criteria: [
          ...(((component.configuration as Record<string, unknown>).criteria as Array<Record<string, unknown>>)
            .map(criterion => ({
              ...criterion,
              title: { ...(criterion.title as Record<string, unknown>), en: 'New revision criterion' },
            }))),
        ],
      },
    } : component
  ));
  const savedResponse = await request.put(`${apiBase}/author/revisions/${started.revision_id}`, {
    data: {
      problem_id: started.problem_id,
      expected_version: started.version,
      client_save_key: `assessment-successor-save-${slug}`,
      slug: started.slug,
      content: changedContent,
      metadata: started.metadata,
      response: started.response,
      scoring: { ...started.scoring, components: changedComponents },
    },
  });
  await expectApiOk(savedResponse);
  await editorialCommand(request, started.revision_id, 'submit-review', 2, slug);
  await editorialCommand(request, started.revision_id, 'approve', 3, slug);
  const published = await request.post(`${apiBase}/author/revisions/${started.revision_id}/publish`, {
    data: {
      expected_version: 4,
      note: 'Publish successor after pending attempt.',
      actor_context: 'assessment-reviewer',
      idempotency_key: `assessment-successor-publish-${slug}`,
    },
  });
  await expectApiOk(published);
}

async function editorialCommand(
  request: APIRequestContext,
  revisionId: string,
  action: 'submit-review' | 'approve',
  version: number,
  slug: string,
) {
  const response = await request.post(`${apiBase}/author/revisions/${revisionId}/${action}`, {
    data: {
      expected_version: version,
      note: 'Assessment successor review.',
      actor_context: 'assessment-reviewer',
      operation_id: `assessment-${action}-${slug}`,
    },
  });
  await expectApiOk(response);
}

function automatedComponent(components: Array<Record<string, unknown>>) {
  return components.find(component => component.method === 'EXACT_MATCH');
}

async function expectApiOk(response: APIResponse) {
  expect(response.ok(), `${response.status()} ${await response.text()}`).toBeTruthy();
}

async function expectNoPageOverflow(page: Page) {
  await expect.poll(() => page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )).toBeLessThanOrEqual(1);
}
