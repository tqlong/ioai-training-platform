import { createApiClient } from '../src';

import { describe, expect, it } from 'vitest';

describe('api-client', () => {
  it('can create a minimal client', () => {
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1' });

    expect(client.baseUrl).toBe('http://localhost:8000/api/v1');
  });
});
