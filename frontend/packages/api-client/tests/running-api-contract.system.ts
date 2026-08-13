import { describe, expect, it } from 'vitest';

import { ApiError, createApiClient } from '../src/index.js';

const apiBase = process.env.IOAI_SYSTEM_API_BASE;
if (!apiBase) {
  throw new Error('IOAI_SYSTEM_API_BASE is required for the running API contract test');
}

let requestSequence = 0;
const observedRequestIds: string[] = [];
const fetchWithRequestIdCheck = async (
  input: string,
  init?: RequestInit,
): Promise<Response> => {
  const requestId = new Headers(init?.headers).get('x-request-id');
  expect(requestId).toMatch(/^contract-system-\d+$/);
  const response = await fetch(input, init);
  expect(response.headers.get('x-request-id')).toBe(requestId);
  observedRequestIds.push(requestId ?? '');
  return response;
};

const client = createApiClient({
  baseUrl: apiBase,
  fetchFn: fetchWithRequestIdCheck,
  requestIdFactory: () => `contract-system-${++requestSequence}`,
});

describe('generated client against the running FastAPI contract', () => {
  it('decodes public pagination and propagates request IDs', async () => {
    const page = await client.listPublicProblems({ page: 1, pageSize: 1 });

    expect(page.page).toBe(1);
    expect(page.page_size).toBe(1);
    expect(Array.isArray(page.items)).toBe(true);
    expect(observedRequestIds.at(-1)).toMatch(/^contract-system-\d+$/);
  });

  it('sends author commands and decodes generated validation responses', async () => {
    const draft = await client.createAuthorDraft();
    const validation = await client.validateAuthorDraft(draft.revision_id, draft.version);

    expect(draft.problem_id).toBeTruthy();
    expect(validation.revision_id).toBe(draft.revision_id);
    expect(Array.isArray(validation.errors)).toBe(true);
  });

  it('preserves stable error codes, status, and request ID', async () => {
    let error: unknown;
    try {
      await client.getPublicProblem('__missing_contract_problem__');
    } catch (caught) {
      error = caught;
    }

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      code: 'PUBLIC_NOT_FOUND',
      status: 404,
      requestId: expect.stringMatching(/^contract-system-\d+$/),
    });
  });
});
