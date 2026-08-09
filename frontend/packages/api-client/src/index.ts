import type { components } from './generated/openapi.js';

export type PublicVocabularyRecord = components['schemas']['PublicVocabularyRecord'];
export type PublicVocabularyResponse = components['schemas']['PublicVocabularyResponse'];
export type AuthorVocabularyRecord = components['schemas']['AuthorVocabularyRecord'];
export type AuthorVocabularyResponse = components['schemas']['AuthorVocabularyResponse'];
export type VocabularyProposal = components['schemas']['VocabularyProposalResponse'];
export type AuthorDraft = components['schemas']['AuthorDraftResponse'];
export type AuthorDraftList = components['schemas']['AuthorDraftListResponse'];
export type SaveDraftRequest = components['schemas']['SaveDraftRequest'];
export type RecordVocabularyProposalRequest = components['schemas']['RecordVocabularyProposalRequest'];
export type ValidationReport = components['schemas']['ValidationReportResponse'];
export type PreviewDraftRequest = components['schemas']['PreviewDraftRequest'];
export type PreviewResponse = components['schemas']['PreviewResponse'];
export type EditorialCommandRequest = components['schemas']['EditorialCommandRequest'];
export type EditorialHistory = components['schemas']['EditorialHistoryResponse'];
export type PublishRevisionRequest = components['schemas']['PublishRevisionRequest'];
export type PublicationResult = components['schemas']['PublicationResponse'];
export type StartRevisionRequest = components['schemas']['StartRevisionRequest'];
export type ArchiveProblemRequest = components['schemas']['ArchiveProblemRequest'];
export type ArchiveProblemResult = components['schemas']['ArchiveProblemResponse'];
export type PublicProblemList = components['schemas']['PublicProblemListResponse'];
export type PublicProblemDetail = components['schemas']['PublicProblemDetailResponse'];
export type PublicSubmissionRequest = components['schemas']['PublicSubmissionRequest'];
export type PublicSubmissionResult = components['schemas']['PublicSubmissionResponse'];
export type PublicProblemRecommendation = components['schemas']['PublicProblemRecommendationResponse'];
export type EditorialAction = 'submit-review' | 'request-changes' | 'approve';

export type PublicVocabularyQuery = {
  vocabularyType: string;
  search?: string;
  rootCode?: string;
  includeDescendants?: boolean;
  limit?: number;
};
export type AuthorVocabularyQuery = PublicVocabularyQuery;
export type AuthorDraftQuery = { search?: string; editorialStatus?: string };
export type PublicProblemQuery = {
  stage?: string;
  competency?: string;
  topic?: string;
  includeSubtopics?: boolean;
  difficulty?: string;
  taskType?: string;
  expectedMinutesMin?: number;
  expectedMinutesMax?: number;
  computeTier?: string;
  search?: string;
  sort?: 'EDITORIAL' | 'NEWEST' | 'EXPECTED_TIME' | 'TITLE';
  page?: number;
  pageSize?: number;
};
export type PublicRecommendationQuery = {
  stage: string;
  completed?: string[];
  evidence?: string[];
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
  listPublicProblems: (query?: PublicProblemQuery) => Promise<PublicProblemList>;
  getPublicProblem: (slug: string) => Promise<PublicProblemDetail>;
  submitPublicProblem: (slug: string, request: PublicSubmissionRequest) => Promise<PublicSubmissionResult>;
  getPublicRecommendation: (
    slug: string,
    query: PublicRecommendationQuery,
  ) => Promise<PublicProblemRecommendation | null>;
  listAuthorDrafts: (query?: AuthorDraftQuery) => Promise<AuthorDraftList>;
  listAuthorVocabulary: (
    query: AuthorVocabularyQuery,
  ) => Promise<AuthorVocabularyResponse>;
  createAuthorDraft: () => Promise<AuthorDraft>;
  getAuthorDraft: (problemId: string) => Promise<AuthorDraft>;
  saveAuthorDraft: (
    revisionId: string,
    request: SaveDraftRequest,
  ) => Promise<AuthorDraft>;
  recordVocabularyProposal: (
    request: RecordVocabularyProposalRequest,
  ) => Promise<VocabularyProposal>;
  validateAuthorDraft: (revisionId: string, expectedVersion: number) => Promise<ValidationReport>;
  previewAuthorDraft: (revisionId: string, request: PreviewDraftRequest) => Promise<PreviewResponse>;
  transitionAuthorRevision: (
    revisionId: string,
    action: EditorialAction,
    request: EditorialCommandRequest,
  ) => Promise<AuthorDraft>;
  getEditorialHistory: (revisionId: string) => Promise<EditorialHistory>;
  publishAuthorRevision: (
    revisionId: string,
    request: PublishRevisionRequest,
  ) => Promise<PublicationResult>;
  startAuthorRevision: (
    problemId: string,
    request: StartRevisionRequest,
  ) => Promise<AuthorDraft>;
  archiveAuthorProblem: (
    problemId: string,
    request: ArchiveProblemRequest,
  ) => Promise<ArchiveProblemResult>;
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
    async listPublicProblems(query = {}) {
      const parameters = new URLSearchParams();
      const values: Array<[string, string | number | boolean | undefined]> = [
        ['stage', query.stage],
        ['competency', query.competency],
        ['topic', query.topic],
        ['include_subtopics', query.includeSubtopics],
        ['difficulty', query.difficulty],
        ['task_type', query.taskType],
        ['expected_minutes_min', query.expectedMinutesMin],
        ['expected_minutes_max', query.expectedMinutesMax],
        ['compute_tier', query.computeTier],
        ['q', query.search],
        ['sort', query.sort],
        ['page', query.page],
        ['page_size', query.pageSize],
      ];
      for (const [key, value] of values) {
        if (value !== undefined) parameters.set(key, String(value));
      }
      const suffix = parameters.size ? `?${parameters.toString()}` : '';
      return requestJson<PublicProblemList>(
        fetchFn,
        `${normalizedBaseUrl}/problems${suffix}`,
        { cache: 'no-store' },
      );
    },
    async getPublicProblem(slug) {
      return requestJson<PublicProblemDetail>(
        fetchFn,
        `${normalizedBaseUrl}/problems/${encodeURIComponent(slug)}`,
        { cache: 'no-store' },
      );
    },
    async submitPublicProblem(slug, request) {
      return requestJson<PublicSubmissionResult>(
        fetchFn,
        `${normalizedBaseUrl}/problems/${encodeURIComponent(slug)}/submissions`,
        { method: 'POST', body: JSON.stringify(request) },
      );
    },
    async getPublicRecommendation(slug, query) {
      const parameters = new URLSearchParams({ stage: query.stage });
      for (const value of query.completed ?? []) {
        parameters.append('completed', value);
      }
      for (const value of query.evidence ?? []) {
        parameters.append('evidence', value);
      }
      const response = await fetchFn(
        `${normalizedBaseUrl}/problems/${encodeURIComponent(slug)}/recommendation?${parameters.toString()}`,
        { cache: 'no-store', headers: { accept: 'application/json' } },
      );
      if (response.status === 204) return null;
      const payload: unknown = await response.json();
      if (!response.ok) throw toApiError(payload, response.status);
      return payload as PublicProblemRecommendation;
    },
    async listAuthorDrafts(query = {}) {
      const parameters = new URLSearchParams();
      if (query.search !== undefined) parameters.set('search', query.search);
      if (query.editorialStatus !== undefined) parameters.set('editorial_status', query.editorialStatus);
      const suffix = parameters.size ? `?${parameters.toString()}` : '';
      return requestJson<AuthorDraftList>(fetchFn, `${normalizedBaseUrl}/author/problems${suffix}`, {
        cache: 'no-store',
      });
    },
    async listAuthorVocabulary(query) {
      const parameters = vocabularyParameters(query);
      return requestJson<AuthorVocabularyResponse>(
        fetchFn,
        `${normalizedBaseUrl}/author/vocabulary?${parameters.toString()}`,
      );
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
        { cache: 'no-store' },
      );
    },
    async saveAuthorDraft(revisionId, request) {
      return requestJson<AuthorDraft>(
        fetchFn,
        `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}`,
        { method: 'PUT', body: JSON.stringify(request) },
      );
    },
    async recordVocabularyProposal(request) {
      return requestJson<VocabularyProposal>(
        fetchFn,
        `${normalizedBaseUrl}/author/vocabulary/proposals`,
        { method: 'POST', body: JSON.stringify(request) },
      );
    },
    async validateAuthorDraft(revisionId, expectedVersion) {
      return requestJson<ValidationReport>(fetchFn, `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/validate`, {
        method: 'POST', body: JSON.stringify({ expected_version: expectedVersion }),
      });
    },
    async previewAuthorDraft(revisionId, request) {
      return requestJson<PreviewResponse>(fetchFn, `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/preview`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async transitionAuthorRevision(revisionId, action, request) {
      return requestJson<AuthorDraft>(fetchFn, `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/${action}`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async getEditorialHistory(revisionId) {
      return requestJson<EditorialHistory>(fetchFn, `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/history`, {
        cache: 'no-store',
      });
    },
    async publishAuthorRevision(revisionId, request) {
      return requestJson<PublicationResult>(fetchFn, `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/publish`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async startAuthorRevision(problemId, request) {
      return requestJson<AuthorDraft>(fetchFn, `${normalizedBaseUrl}/author/problems/${encodeURIComponent(problemId)}/revisions`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async archiveAuthorProblem(problemId, request) {
      return requestJson<ArchiveProblemResult>(fetchFn, `${normalizedBaseUrl}/author/problems/${encodeURIComponent(problemId)}/archive`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
  };
};

const vocabularyParameters = (query: PublicVocabularyQuery): URLSearchParams => {
  const parameters = new URLSearchParams({ vocabulary_type: query.vocabularyType });
  if (query.search !== undefined) parameters.set('search', query.search);
  if (query.rootCode !== undefined) parameters.set('root_code', query.rootCode);
  if (query.includeDescendants !== undefined) {
    parameters.set('include_descendants', String(query.includeDescendants));
  }
  if (query.limit !== undefined) parameters.set('limit', String(query.limit));
  return parameters;
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
  const candidate = typeof payload === 'object' && payload !== null && 'detail' in payload
    ? payload.detail
    : typeof payload === 'object' && payload !== null && 'error' in payload
      ? payload.error
      : null;
  if (
    typeof candidate === 'object' && candidate !== null &&
    'code' in candidate && 'message' in candidate &&
    typeof candidate.code === 'string' && typeof candidate.message === 'string'
  ) {
    return new ApiError(candidate.code, candidate.message, status);
  }
  return new ApiError('invalid_response', 'The API returned an invalid error response.', status);
};

export type { components, operations, paths } from './generated/openapi.js';
