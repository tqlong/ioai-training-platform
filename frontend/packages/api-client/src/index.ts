import type { components } from './generated/openapi.js';

export type PublicVocabularyRecord = components['schemas']['PublicVocabularyRecord'];
export type PublicVocabularyResponse = components['schemas']['PublicVocabularyResponse'];
export type AuthorVocabularyRecord = components['schemas']['AuthorVocabularyRecord'];
export type AuthorVocabularyResponse = components['schemas']['AuthorVocabularyResponse'];
export type VocabularyProposal = components['schemas']['VocabularyProposalResponse'];
export type AuthorDraft = components['schemas']['AuthorDraftResponse'];
export type AuthorDraftList = components['schemas']['AuthorDraftListResponse'];
export type SaveDraftRequest = components['schemas']['SaveDraftRequest'];

export type PublicVocabularyQuery = {
  vocabularyType: string;
  search?: string;
  rootCode?: string;
  includeDescendants?: boolean;
  limit?: number;
};

export type FetchFunction = (
  input: string,
  init?: RequestInit,
) => Promise<Response>;

export type ApiClientOptions = {
  baseUrl: string;
  fetchFn?: FetchFunction;
};

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

export type ApiClient = {
  baseUrl: string;
  listPublicVocabulary: (
    query: PublicVocabularyQuery,
  ) => Promise<PublicVocabularyResponse>;
  listAuthorDrafts: () => Promise<AuthorDraftList>;
  createAuthorDraft: () => Promise<AuthorDraft>;
  getAuthorDraft: (problemId: string) => Promise<AuthorDraft>;
  saveAuthorDraft: (
    revisionId: string,
    request: SaveDraftRequest,
  ) => Promise<AuthorDraft>;
};

export const createApiClient = ({
  baseUrl,
  fetchFn = fetch,
}: ApiClientOptions): ApiClient => {
  const normalizedBaseUrl = baseUrl.replace(/\/$/, '');
  return {
    baseUrl: normalizedBaseUrl,
    async listPublicVocabulary(query) {
      const parameters = new URLSearchParams({
        vocabulary_type: query.vocabularyType,
      });
      if (query.search !== undefined) parameters.set('search', query.search);
      if (query.rootCode !== undefined) parameters.set('root_code', query.rootCode);
      if (query.includeDescendants !== undefined) {
        parameters.set('include_descendants', String(query.includeDescendants));
      }
      if (query.limit !== undefined) parameters.set('limit', String(query.limit));

      const response = await fetchFn(
        `${normalizedBaseUrl}/vocabulary?${parameters.toString()}`,
        { headers: { accept: 'application/json' } },
      );
      const payload: unknown = await response.json();
      if (!response.ok) throw toApiError(payload, response.status);
      return payload as PublicVocabularyResponse;
    },
    async listAuthorDrafts() {
      return requestJson<AuthorDraftList>(fetchFn, `${normalizedBaseUrl}/author/problems`);
    },
    async createAuthorDraft() {
      return requestJson<AuthorDraft>(fetchFn, `${normalizedBaseUrl}/author/problems`, {
        method: 'POST',
        body: '{}',
      });
    },
    async getAuthorDraft(problemId) {
      return requestJson<AuthorDraft>(
        fetchFn,
        `${normalizedBaseUrl}/author/problems/${encodeURIComponent(problemId)}`,
      );
    },
    async saveAuthorDraft(revisionId, request) {
      return requestJson<AuthorDraft>(
        fetchFn,
        `${normalizedBaseUrl}/author/problems/revisions/${encodeURIComponent(revisionId)}`,
        { method: 'PUT', body: JSON.stringify(request) },
      );
    },
  };
};

const requestJson = async <Result>(
  fetchFn: FetchFunction,
  url: string,
  init?: RequestInit,
): Promise<Result> => {
  const response = await fetchFn(url, {
    ...init,
    headers: { accept: 'application/json', 'content-type': 'application/json' },
  });
  const payload: unknown = await response.json();
  if (!response.ok) throw toApiError(payload, response.status);
  return payload as Result;
};

const toApiError = (payload: unknown, status: number): ApiError => {
  if (
    typeof payload === 'object' &&
    payload !== null &&
    'error' in payload &&
    typeof payload.error === 'object' &&
    payload.error !== null &&
    'code' in payload.error &&
    'message' in payload.error &&
    typeof payload.error.code === 'string' &&
    typeof payload.error.message === 'string'
  ) {
    return new ApiError(payload.error.code, payload.error.message, status);
  }
  return new ApiError('invalid_response', 'The API returned an invalid error response.', status);
};

export type { components, operations, paths } from './generated/openapi.js';
