import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './frontend/tests/e2e',
  fullyParallel: false,
  retries: 0,
  timeout: 90_000,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.STUDIO_BASE_URL ?? 'http://127.0.0.1:3001',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', testIgnore: /learner-performance\.spec\.ts/, use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', testIgnore: /learner-performance\.spec\.ts/, use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', testIgnore: /learner-performance\.spec\.ts/, use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', testIgnore: /learner-performance\.spec\.ts/, use: { ...devices['Pixel 7'] } },
    { name: 'mobile-safari', testIgnore: /learner-performance\.spec\.ts/, use: { ...devices['iPhone 15'] } },
    ...(process.env.IOAI_RUN_LEARNER_PERFORMANCE === '1' ? [{
      name: 'learner-performance',
      testMatch: /learner-performance\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
    }] : []),
  ],
});
