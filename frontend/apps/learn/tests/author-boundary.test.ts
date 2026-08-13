import { NextRequest } from 'next/server';

import { middleware } from '../middleware';

describe('learner proxy author boundary', () => {
  it('returns a uniform not-found response for author API paths', async () => {
    const response = middleware(
      new NextRequest('http://127.0.0.1:3000/api/v1/author/problems'),
    );

    expect(response.status).toBe(404);
    await expect(response.json()).resolves.toEqual({
      error: {
        code: 'PUBLIC_NOT_FOUND',
        message: 'Resource not found.',
      },
    });
  });

  it('does not block public API paths when called directly', () => {
    const response = middleware(
      new NextRequest('http://127.0.0.1:3000/api/v1/problems'),
    );

    expect(response.headers.get('x-middleware-next')).toBe('1');
  });
});
