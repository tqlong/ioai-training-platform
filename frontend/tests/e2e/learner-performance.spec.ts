import { expect, test, type BrowserContext, type Page } from '@playwright/test';

import { createHumanProblem, type ProblemFixture } from './support/system-fixture';

const learnBase = process.env.LEARN_BASE_URL ?? 'http://127.0.0.1:3100';

test.describe('Release 0 production learner budgets', () => {
  let published: ProblemFixture;
  let privateDraft: ProblemFixture;

  test.beforeAll(async ({ request }) => {
    const prefix = `learner-performance-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    privateDraft = await createHumanProblem(request, `${prefix}-private-draft`, 'DRAFT');
    published = await createHumanProblem(request, `${prefix}-published`, 'PUBLISHED');
  });

  test('meets cold broadband library and permanent-detail usability budgets', async ({
    context,
    page,
    request,
  }) => {
    const publicPage = await request.get(
      `${process.env.API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'}/problems?page_size=25`,
    );
    expect(publicPage.ok(), await publicPage.text()).toBeTruthy();
    const publicPayload = await publicPage.json() as { total: number };
    expect(publicPayload.total, 'Run the learner browser matrix first to seed at least 20 public records.')
      .toBeGreaterThanOrEqual(20);

    await emulateNormalBroadband(context, page);
    const browserRequests: string[] = [];
    page.on('request', requestEvent => browserRequests.push(requestEvent.url()));

    const libraryStartedAt = Date.now();
    const documentResponse = await page.goto(
      `${learnBase}/problems?stage=AI_1_FOUNDATIONS&sort=NEWEST&page_size=25`,
    );
    await expect(page.locator('[data-problem-link]').first()).toBeVisible();
    const libraryMeaningfulMs = Date.now() - libraryStartedAt;
    expect(libraryMeaningfulMs).toBeLessThan(2_000);

    const html = await documentResponse?.text() ?? '';
    expect(html).not.toContain(privateDraft.slug);
    expect(html).not.toMatch(/Draft preview|editorial_status|revision_id/i);
    expect(browserRequests).not.toEqual(expect.arrayContaining([
      expect.stringMatching(/\/(?:login|auth|session|account)(?:\/|\?|$)/i),
    ]));

    await page.context().clearCookies();
    const detailStartedAt = Date.now();
    await page.goto(`${learnBase}/problems/${published.slug}`);
    await expect(page.getByRole('heading', { name: new RegExp(published.slug) })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Submit answer' })).toBeEnabled();
    const detailUsableMs = Date.now() - detailStartedAt;
    expect(detailUsableMs).toBeLessThan(3_000);

    await page.getByRole('textbox', { name: 'Short answer' }).fill('Readable while pending.');
    await page.getByRole('button', { name: 'Submit answer' }).click();
    await expect(page.getByText('waiting for assessment', { exact: false })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Learning objective' })).toBeVisible();

    test.info().annotations.push(
      { type: 'library-meaningful-ms', description: String(libraryMeaningfulMs) },
      { type: 'detail-usable-ms', description: String(detailUsableMs) },
      { type: 'network-profile', description: '40 ms latency, 10 Mbps down, 5 Mbps up, cold cache' },
    );
    console.log(JSON.stringify({
      event: 'learner_performance_budget',
      library_meaningful_ms: libraryMeaningfulMs,
      detail_usable_ms: detailUsableMs,
      public_record_count: publicPayload.total,
      network_profile: '40ms-10mbps-down-5mbps-up-cold',
    }));
  });
});

async function emulateNormalBroadband(context: BrowserContext, page: Page) {
  const session = await context.newCDPSession(page);
  await session.send('Network.enable');
  await session.send('Network.setCacheDisabled', { cacheDisabled: true });
  await session.send('Network.emulateNetworkConditions', {
    offline: false,
    latency: 40,
    downloadThroughput: (10 * 1024 * 1024) / 8,
    uploadThroughput: (5 * 1024 * 1024) / 8,
  });
}
