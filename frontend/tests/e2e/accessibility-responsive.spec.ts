import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';

import {
  createHumanProblem,
  submitPendingAnswer,
  type ProblemFixture,
} from './support/system-fixture';

const learnBase = process.env.LEARN_BASE_URL ?? 'http://127.0.0.1:3000';
const studioBase = process.env.STUDIO_BASE_URL ?? 'http://127.0.0.1:3001';

test.describe.serial('Release 0 accessibility and responsive system checks', () => {
  let approved: ProblemFixture;
  let published: ProblemFixture;
  let attemptId: string;

  test.beforeAll(async ({ request }) => {
    const prefix = `a11y-system-${Date.now()}`;
    approved = await createHumanProblem(request, `${prefix}-approved`, 'APPROVED');
    published = await createHumanProblem(request, `${prefix}-published`, 'PUBLISHED');
    ({ attemptId } = await submitPendingAnswer(request, published.slug));
  });

  test('has no detectable WCAG A/AA violations on representative routes', async ({ page }) => {
    const routes = [
      `${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Accessible%20system`,
      `${learnBase}/problems/${published.slug}`,
      `${studioBase}/author/problems`,
      `${studioBase}/author/problems/${approved.problemId}`,
      `${studioBase}/author/assessments`,
      `${studioBase}/author/assessments/${attemptId}`,
    ];

    for (const route of routes) {
      await page.goto(route);
      await expect(page.locator('main').getByRole('heading').first()).toBeVisible();
      await assertNoA11yViolations(page, route);
    }
  });

  test('keeps learner and Studio layouts within four required widths', async ({ page }) => {
    for (const width of [360, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto(`${learnBase}/problems?stage=AI_1_FOUNDATIONS&q=Accessible%20system`);
      if (width < 768) {
        await expect(page.getByRole('list', { name: 'Published problem cards' })).toBeVisible();
        await expect(page.getByRole('table', { name: 'Published problems' })).toBeHidden();
      } else {
        await expect(page.getByRole('table', { name: 'Published problems' })).toBeVisible();
        await expect(page.getByRole('list', { name: 'Published problem cards' })).toBeHidden();
      }
      await expectNoPageOverflow(page);

      await page.goto(`${learnBase}/problems/${published.slug}`);
      await expectNoPageOverflow(page);
      await page.goto(`${studioBase}/author/problems/${approved.problemId}`);
      await expect(page.getByRole('heading', { name: /Edit problem/ })).toBeVisible();
      await expectNoPageOverflow(page);
      await page.goto(`${studioBase}/author/assessments/${attemptId}`);
      await expectNoPageOverflow(page);
    }
  });

  test('supports 200 percent text zoom without horizontal page overflow', async ({ page }) => {
    for (const route of [
      `${learnBase}/problems/${published.slug}`,
      `${studioBase}/author/problems/${approved.problemId}`,
      `${studioBase}/author/assessments/${attemptId}`,
    ]) {
      await page.setViewportSize({ width: 1280, height: 900 });
      await page.goto(route);
      await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
      await expectNoPageOverflow(page);
    }
  });

  test('traps, escapes, and restores focus in learner and publication dialogs', async ({ page }) => {
    await page.goto(`${learnBase}/problems/${published.slug}`);
    const report = page.getByRole('button', { name: 'Report a problem' });
    await report.click();
    const feedback = page.getByRole('dialog', { name: 'Report a problem' });
    await expect(feedback.getByRole('combobox', { name: 'Category' })).toBeFocused();
    await feedback.getByRole('button', { name: 'Close feedback' }).focus();
    await page.keyboard.press('Tab');
    await expect(feedback.getByRole('combobox', { name: 'Category' })).toBeFocused();
    await page.keyboard.press('Escape');
    await expect(feedback).toBeHidden();
    await expect(report).toBeFocused();

    await page.goto(`${studioBase}/author/problems/${approved.problemId}`);
    const publish = page.getByRole('button', { name: 'Publish', exact: true });
    await publish.click();
    const dialog = page.getByRole('dialog', { name: 'Publish approved revision' });
    await expect(dialog.getByRole('textbox', { name: 'Publication note' })).toBeFocused();
    await dialog.getByRole('button', { name: 'Cancel' }).focus();
    await page.keyboard.press('Tab');
    await expect(dialog.getByRole('textbox', { name: 'Publication note' })).toBeFocused();
    await page.keyboard.press('Escape');
    await expect(dialog).toBeHidden();
    await expect(publish).toBeFocused();
  });
});

async function assertNoA11yViolations(page: Page, route: string) {
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
  expect(result.violations, `${route}\n${JSON.stringify(result.violations, null, 2)}`)
    .toEqual([]);
}

async function expectNoPageOverflow(page: Page) {
  await expect.poll(() => page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )).toBeLessThanOrEqual(1);
}
