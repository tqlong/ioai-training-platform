import { expect, test } from '@playwright/test';

import { createHumanProblem, submitPendingAnswer } from './support/system-fixture';

const apiBase = process.env.API_BASE_URL ?? 'http://127.0.0.1:58000/api/v1';
const learnBase = process.env.LEARN_BASE_URL ?? 'http://127.0.0.1:53000';
const studioBase = process.env.STUDIO_BASE_URL ?? 'http://127.0.0.1:53001';
const slug = process.env.IOAI_COMPOSE_FIXTURE_SLUG ?? 'compose-lifecycle-persisted';

test('creates representative system-of-record data through deployed boundaries', async ({ page, request }) => {
  await createHumanProblem(request, slug, 'PUBLISHED');
  const { attemptId, receipt } = await submitPendingAnswer(request, slug);
  const feedback = await request.post(`${apiBase}/problems/${slug}/feedback`, {
    data: {
      feedback_key: `compose-feedback-${slug}`,
      category: 'CONTENT_ISSUE',
      message: 'Persist this lifecycle feedback.',
    },
  });
  expect(feedback.ok(), await feedback.text()).toBeTruthy();

  const decision = await request.post(`${apiBase}/author/assessments/${attemptId}/decisions`, {
    data: {
      selections: [{
        component_index: 0,
        criterion_id: 'reasoning',
        level_id: 'complete',
        feedback: 'Persisted criterion feedback.',
      }],
      overall_feedback: 'Persisted lifecycle assessment.',
    },
  });
  expect(decision.ok(), await decision.text()).toBeTruthy();

  await page.goto(`${learnBase}/problems/${slug}`);
  await expect(page.getByRole('heading', { name: new RegExp(slug) })).toBeVisible();
  await page.goto(`${studioBase}/author/assessments/${attemptId}`);
  await expect(page.getByText(/Version 1/)).toBeVisible();

  const result = await request.get(`${apiBase}/submissions/${attemptId}`, {
    headers: { 'X-Submission-Receipt': receipt },
  });
  expect(result.ok(), await result.text()).toBeTruthy();
  expect((await result.json()).passed).toBe(true);
});
