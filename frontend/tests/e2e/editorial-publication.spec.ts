import { expect, test } from '@playwright/test';

const apiBase = process.env.API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

test('author preview, review, publication, revision, and archive stay separated', async ({ page, request }) => {
  const createdResponse = await request.post(`${apiBase}/author/problems`, { data: {} });
  await expectApiOk(createdResponse);
  const created = await createdResponse.json() as {
    problem_id: string; revision_id: string; version: number;
  };
  const slug = `editorial-e2e-${Date.now()}`;
  const localized = (en: string, vi: string) => ({
    en, vi, en_state: 'COMPLETE', vi_state: 'COMPLETE',
  });
  const saveResponse = await request.put(
    `${apiBase}/author/revisions/${created.revision_id}`,
    { data: {
      problem_id: created.problem_id,
      expected_version: created.version,
      client_save_key: `seed-${slug}`,
      slug,
      content: {
        title: localized('Editorial workflow problem', 'Bài quy trình biên tập'),
        summary: localized('Calculate a classification metric.', 'Tính một độ đo phân loại.'),
        objectives: [localized('Calculate precision from a confusion matrix.', 'Tính precision từ ma trận nhầm lẫn.')],
        blocks: [{ kind: 'STATEMENT', content: localized('Choose the correct value.', 'Chọn giá trị đúng.'), order: 1, reveal_order: null }],
      },
      metadata: {
        stage: ['PATHWAY_STAGE', 'AI_1_FOUNDATIONS'],
        difficulty: ['DIFFICULTY', 'EASY'],
        primary_competency: ['COMPETENCY', 'EVAL_METRICS'],
        secondary_competencies: [],
        task_type: ['TASK_TYPE', 'QUIZ_SINGLE'],
        topics: [['TOPIC', 'EVAL_CONFUSION_MATRIX']],
        prerequisites: [],
        modalities: [['DATA_MODALITY', 'NONE']],
        expected_minutes: 15,
        resources: {
          compute_tier: ['COMPUTE_TIER', 'NONE'], runtime_class: ['RUNTIME_CLASS', 'INSTANT'],
          cpu_cores: 0, ram_mb: 0, gpu_count: 0, gpu_vram_mb: 0,
          storage_mb: 0, runtime_seconds: 0, network_policy: 'DENIED',
        },
      },
      response: {
        type: 'QUIZ_SINGLE',
        choices: [
          { id: 'A', content: localized('One', 'Một') },
          { id: 'B', content: localized('Two', 'Hai') },
        ],
        correct_choice_id: 'A',
      },
      scoring: {
        response_type: 'QUIZ_SINGLE',
        components: [{ method: 'EXACT_MATCH', weight: '1.0', configuration: null }],
      },
    } },
  );
  await expectApiOk(saveResponse);

  await page.goto(`/author/problems/${created.problem_id}`);
  await expect(page.getByText('Version 2')).toBeVisible();
  await waitForEditorPolicies(page);
  await page.getByRole('textbox', { name: 'English title' }).fill('Unsaved learner preview title');
  await page.getByRole('link', { name: 'Preview as learner' }).click();
  await expect(page.getByText('Draft preview - not public')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Unsaved learner preview title' })).toBeVisible();
  await expect(page.getByTestId('preview-frame')).toHaveAttribute('data-viewport', 'desktop');
  await page.getByRole('button', { name: 'Mobile width' }).click();
  await expect(page.getByTestId('preview-frame')).toHaveAttribute('data-viewport', 'mobile');
  await expect(page.getByRole('button', { name: 'Open public problem' })).toBeDisabled();

  await page.goto(`/author/problems/${created.problem_id}`);
  await waitForEditorPolicies(page);
  await page.getByRole('button', { name: 'Validate draft' }).click();
  await expect(page.getByText('Eligible for publication')).toBeVisible();
  await decide(page, 'Ready for first review.', 'Submit for review');
  await expect(page.getByText('In review', { exact: true })).toBeVisible();
  await decide(page, 'Clarify the learner explanation.', 'Request changes');
  await expect(page.getByText('Changes requested', { exact: true })).toBeVisible();

  await page.goto('/author/problems');
  const problemRow = page.getByRole('row', { name: new RegExp(created.problem_id) });
  await problemRow.getByRole('button', { name: 'Address changes' }).click();
  await expect(page.getByText('Structured draft · DRAFT')).toBeVisible();
  await waitForEditorPolicies(page);
  await page.getByRole('button', { name: 'Validate draft' }).click();
  await expect(page.getByText('Eligible for publication')).toBeVisible();
  await decide(page, 'Revised and ready.', 'Submit for review');
  await decide(page, 'Content and scoring checked.', 'Approve');
  await expect(page.getByText('Approved', { exact: true })).toBeVisible();

  await page.getByRole('button', { name: 'Publish' }).click();
  const publishDialog = page.getByRole('dialog', { name: 'Publish approved revision' });
  await expect(publishDialog).toContainText(`/problems/${slug}`);
  await publishDialog.getByRole('textbox', { name: 'Publication note' }).fill('Publish pilot content.');
  await publishDialog.getByRole('button', { name: 'Confirm publish' }).click();
  await expect(page.getByRole('link', { name: `/problems/${slug}` })).toHaveAttribute('href', `/problems/${slug}`);

  await page.goto('/author/problems');
  await page.getByRole('row', { name: new RegExp(created.problem_id) })
    .getByRole('button', { name: 'Archive' }).click();
  const archiveDialog = page.getByRole('dialog', { name: 'Archive published problem' });
  await archiveDialog.getByRole('textbox', { name: 'Archive note' }).fill('Archive after pilot verification.');
  await archiveDialog.getByRole('button', { name: 'Confirm archive' }).click();
  await expect(page.getByRole('row', { name: new RegExp(created.problem_id) })
    .getByText('archived').first()).toBeVisible();
});

async function decide(page: import('@playwright/test').Page, note: string, action: string) {
  await page.getByRole('textbox', { name: 'Editorial note' }).fill(note);
  await page.getByRole('button', { name: action }).click();
}

async function waitForEditorPolicies(page: import('@playwright/test').Page) {
  await expect(page.getByText('Loading curriculum values...')).toBeHidden({ timeout: 20_000 });
  await expect(page.getByText('Loading resource policy…')).toBeHidden({ timeout: 20_000 });
}

async function expectApiOk(response: import('@playwright/test').APIResponse) {
  expect(response.ok(), `${response.status()} ${await response.text()}`).toBeTruthy();
}
