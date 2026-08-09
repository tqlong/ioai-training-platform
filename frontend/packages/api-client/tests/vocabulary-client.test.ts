import { describe, expect, it, vi } from 'vitest';

import { createApiClient } from '../src';

describe('generated vocabulary client', () => {
  it('returns the OpenAPI-derived public vocabulary response', async () => {
    const fetchFn = vi.fn(async () =>
      Response.json({
        items: [
          {
            identity: { vocabulary_type: 'TOPIC', code: 'TOPIC_MATHEMATICS' },
            labels: { en: 'Mathematics', vi: 'Toán học' },
            aliases: [],
            parent_identity: null,
            breadcrumbs: [
              { vocabulary_type: 'TOPIC', code: 'TOPIC_MATHEMATICS' },
            ],
          },
        ],
        count: 1,
      }),
    );
    const client = createApiClient({
      baseUrl: 'http://localhost:8000/api/v1',
      fetchFn,
    });

    const response = await client.listPublicVocabulary({
      vocabularyType: 'TOPIC',
      search: 'math',
      rootCode: 'TOPIC_MATHEMATICS',
      includeDescendants: true,
      limit: 50,
    });

    expect(response.items[0]?.identity.code).toBe('TOPIC_MATHEMATICS');
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/vocabulary?vocabulary_type=TOPIC&search=math&root_code=TOPIC_MATHEMATICS&include_descendants=true&limit=50',
      { headers: { accept: 'application/json' } },
    );
  });

  it('surfaces a typed API error instead of returning an invalid payload', async () => {
    const client = createApiClient({
      baseUrl: 'http://localhost:8000/api/v1/',
      fetchFn: async () =>
        Response.json(
          { error: { code: 'invalid_request', message: 'Invalid.' } },
          { status: 422 },
        ),
    });

    await expect(
      client.listPublicVocabulary({ vocabularyType: 'topic' }),
    ).rejects.toMatchObject({ code: 'invalid_request', status: 422 });
  });
});
