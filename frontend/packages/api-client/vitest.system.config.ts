import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/running-api-contract.system.ts'],
    testTimeout: 15_000,
  },
});
