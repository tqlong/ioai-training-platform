import type { components, operations } from './generated/openapi.js';

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
export type PublicFeedbackRequest = components['schemas']['PublicFeedbackRequest'];
export type PublicFeedbackReceipt = components['schemas']['PublicFeedbackReceipt'];
export type PublicProblemRecommendation = components['schemas']['PublicProblemRecommendationResponse'];
export type AssessmentList = components['schemas']['AssessmentListResponse'];
export type AssessmentDetail = components['schemas']['AssessmentDetailResponse'];
export type AssessmentDecisionRequest = components['schemas']['AssessmentDecisionRequest'];
export type EditorialAction = 'submit-review' | 'request-changes' | 'approve';

type PublicVocabularyApiQuery =
  operations['list_public_vocabulary_api_v1_vocabulary_get']['parameters']['query'];
type AuthorDraftApiQuery = NonNullable<
  operations['list_drafts_api_v1_author_problems_get']['parameters']['query']
>;
type PublicProblemApiQuery = NonNullable<
  operations['list_problems_api_v1_problems_get']['parameters']['query']
>;
type PublicRecommendationApiQuery =
  operations['recommend_problem_api_v1_problems__slug__recommendation_get']['parameters']['query'];
type AuthorAssessmentApiQuery = NonNullable<
  operations['list_assessments_api_v1_author_assessments_get']['parameters']['query']
>;

export type PublicVocabularyQuery = {
  vocabularyType: PublicVocabularyApiQuery['vocabulary_type'];
  search?: NonNullable<PublicVocabularyApiQuery['search']>;
  rootCode?: NonNullable<PublicVocabularyApiQuery['root_code']>;
  includeDescendants?: PublicVocabularyApiQuery['include_descendants'];
  limit?: PublicVocabularyApiQuery['limit'];
};
export type AuthorVocabularyQuery = PublicVocabularyQuery;
export type AuthorDraftQuery = {
  search?: NonNullable<AuthorDraftApiQuery['search']>;
  editorialStatus?: NonNullable<AuthorDraftApiQuery['editorial_status']>;
};
export type PublicProblemQuery = {
  stage?: NonNullable<PublicProblemApiQuery['stage']>;
  competency?: NonNullable<PublicProblemApiQuery['competency']>;
  topic?: NonNullable<PublicProblemApiQuery['topic']>;
  includeSubtopics?: PublicProblemApiQuery['include_subtopics'];
  difficulty?: NonNullable<PublicProblemApiQuery['difficulty']>;
  taskType?: NonNullable<PublicProblemApiQuery['task_type']>;
  expectedMinutesMin?: NonNullable<PublicProblemApiQuery['expected_minutes_min']>;
  expectedMinutesMax?: NonNullable<PublicProblemApiQuery['expected_minutes_max']>;
  computeTier?: NonNullable<PublicProblemApiQuery['compute_tier']>;
  search?: NonNullable<PublicProblemApiQuery['q']>;
  sort?: PublicProblemApiQuery['sort'];
  page?: PublicProblemApiQuery['page'];
  pageSize?: PublicProblemApiQuery['page_size'];
};
export type PublicRecommendationQuery = {
  stage: PublicRecommendationApiQuery['stage'];
  completed?: PublicRecommendationApiQuery['completed'];
  evidence?: PublicRecommendationApiQuery['evidence'];
};
export type AuthorAssessmentQuery = {
  status?: 'PENDING' | 'ASSESSED' | 'ALL';
  problem?: NonNullable<AuthorAssessmentApiQuery['problem']>;
  limit?: AuthorAssessmentApiQuery['limit'];
  offset?: AuthorAssessmentApiQuery['offset'];
};

export type FetchFunction = (
  input: string,
  init?: RequestInit,
) => Promise<Response>;

export type ApiClientOptions = {
  baseUrl: string;
  fetchFn?: FetchFunction;
  requestIdFactory?: () => string;
};

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly requestId?: string;

  constructor(code: string, message: string, status: number, requestId?: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.requestId = requestId;
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
  getPublicSubmission: (attemptId: string, receipt: string) => Promise<PublicSubmissionResult>;
  submitPublicFeedback: (slug: string, request: PublicFeedbackRequest) => Promise<PublicFeedbackReceipt>;
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
  getAuthorRevision: (revisionId: string) => Promise<AuthorDraft>;
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
  listAuthorAssessments: (query?: AuthorAssessmentQuery) => Promise<AssessmentList>;
  getAuthorAssessment: (attemptId: string) => Promise<AssessmentDetail>;
  decideAuthorAssessment: (attemptId: string, request: AssessmentDecisionRequest) => Promise<AssessmentDetail>;
};

export const createApiClient = ({
  baseUrl,
  fetchFn = fetch,
  requestIdFactory,
}: ApiClientOptions): ApiClient => {
  const normalizedBaseUrl = baseUrl.replace(/\/$/, '');
  const apiRequest = <Result>(url: string, init?: RequestInit): Promise<Result> =>
    requestJson<Result>(fetchFn, url, init, requestIdFactory);
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

      return apiRequest<PublicVocabularyResponse>(
        `${normalizedBaseUrl}/vocabulary?${parameters.toString()}`,
        { headers: { accept: 'application/json' } },
      );
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
      return apiRequest<PublicProblemList>(
        `${normalizedBaseUrl}/problems${suffix}`,
        { cache: 'no-store' },
      );
    },
    async getPublicProblem(slug) {
      return apiRequest<PublicProblemDetail>(
        `${normalizedBaseUrl}/problems/${encodeURIComponent(slug)}`,
        { cache: 'no-store' },
      );
    },
    async submitPublicProblem(slug, request) {
      return apiRequest<PublicSubmissionResult>(
        `${normalizedBaseUrl}/problems/${encodeURIComponent(slug)}/submissions`,
        { method: 'POST', body: JSON.stringify(request) },
      );
    },
    async getPublicSubmission(attemptId, receipt) {
      return apiRequest<PublicSubmissionResult>(
        `${normalizedBaseUrl}/submissions/${encodeURIComponent(attemptId)}`,
        { cache: 'no-store', headers: { 'x-submission-receipt': receipt } },
      );
    },
    async submitPublicFeedback(slug, request) {
      return apiRequest<PublicFeedbackReceipt>(
        `${normalizedBaseUrl}/problems/${encodeURIComponent(slug)}/feedback`,
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
        {
          cache: 'no-store',
          headers: requestHeaders({ accept: 'application/json' }, requestIdFactory),
        },
      );
      if (response.status === 204) return null;
      const payload: unknown = await response.json();
      if (!response.ok) {
        throw toApiError(payload, response.status, response.headers.get('x-request-id'));
      }
      return payload as PublicProblemRecommendation;
    },
    async listAuthorDrafts(query = {}) {
      const parameters = new URLSearchParams();
      if (query.search !== undefined) parameters.set('search', query.search);
      if (query.editorialStatus !== undefined) parameters.set('editorial_status', query.editorialStatus);
      const suffix = parameters.size ? `?${parameters.toString()}` : '';
      return apiRequest<AuthorDraftList>(`${normalizedBaseUrl}/author/problems${suffix}`, {
        cache: 'no-store',
      });
    },
    async listAuthorVocabulary(query) {
      const parameters = vocabularyParameters(query);
      return apiRequest<AuthorVocabularyResponse>(
        `${normalizedBaseUrl}/author/vocabulary?${parameters.toString()}`,
      );
    },
    async createAuthorDraft() {
      return apiRequest<AuthorDraft>(`${normalizedBaseUrl}/author/problems`, {
        method: 'POST',
        body: '{}',
      });
    },
    async getAuthorDraft(problemId) {
      return apiRequest<AuthorDraft>(
        `${normalizedBaseUrl}/author/problems/${encodeURIComponent(problemId)}`,
        { cache: 'no-store' },
      );
    },
    async getAuthorRevision(revisionId) {
      return apiRequest<AuthorDraft>(
        `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}`,
        { cache: 'no-store' },
      );
    },
    async saveAuthorDraft(revisionId, request) {
      return apiRequest<AuthorDraft>(
        `${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}`,
        { method: 'PUT', body: JSON.stringify(request) },
      );
    },
    async recordVocabularyProposal(request) {
      return apiRequest<VocabularyProposal>(
        `${normalizedBaseUrl}/author/vocabulary/proposals`,
        { method: 'POST', body: JSON.stringify(request) },
      );
    },
    async validateAuthorDraft(revisionId, expectedVersion) {
      return apiRequest<ValidationReport>(`${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/validate`, {
        method: 'POST', body: JSON.stringify({ expected_version: expectedVersion }),
      });
    },
    async previewAuthorDraft(revisionId, request) {
      return apiRequest<PreviewResponse>(`${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/preview`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async transitionAuthorRevision(revisionId, action, request) {
      return apiRequest<AuthorDraft>(`${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/${action}`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async getEditorialHistory(revisionId) {
      return apiRequest<EditorialHistory>(`${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/history`, {
        cache: 'no-store',
      });
    },
    async publishAuthorRevision(revisionId, request) {
      return apiRequest<PublicationResult>(`${normalizedBaseUrl}/author/revisions/${encodeURIComponent(revisionId)}/publish`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async startAuthorRevision(problemId, request) {
      return apiRequest<AuthorDraft>(`${normalizedBaseUrl}/author/problems/${encodeURIComponent(problemId)}/revisions`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async archiveAuthorProblem(problemId, request) {
      return apiRequest<ArchiveProblemResult>(`${normalizedBaseUrl}/author/problems/${encodeURIComponent(problemId)}/archive`, {
        method: 'POST', body: JSON.stringify(request),
      });
    },
    async listAuthorAssessments(query = {}) {
      const parameters = new URLSearchParams();
      if (query.status) parameters.set('status', query.status);
      if (query.problem) parameters.set('problem', query.problem);
      if (query.limit !== undefined) parameters.set('limit', String(query.limit));
      if (query.offset !== undefined) parameters.set('offset', String(query.offset));
      const suffix = parameters.size ? `?${parameters.toString()}` : '';
      return apiRequest<AssessmentList>(`${normalizedBaseUrl}/author/assessments${suffix}`, { cache: 'no-store' });
    },
    async getAuthorAssessment(attemptId) {
      return apiRequest<AssessmentDetail>(`${normalizedBaseUrl}/author/assessments/${encodeURIComponent(attemptId)}`, { cache: 'no-store' });
    },
    async decideAuthorAssessment(attemptId, request) {
      return apiRequest<AssessmentDetail>(`${normalizedBaseUrl}/author/assessments/${encodeURIComponent(attemptId)}/decisions`, { method: 'POST', body: JSON.stringify(request) });
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
  requestIdFactory?: () => string,
): Promise<Result> => {
  const headers: Record<string, string> = { accept: 'application/json' };
  if (init?.body !== undefined) headers['content-type'] = 'application/json';
  const response = await fetchFn(url, {
    ...init,
    headers: requestHeaders(
      { ...headers, ...init?.headers },
      requestIdFactory,
    ),
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    throw toApiError(payload, response.status, response.headers.get('x-request-id'));
  }
  return payload as Result;
};

const requestHeaders = (
  headers: HeadersInit,
  requestIdFactory?: () => string,
): HeadersInit => {
  const normalized = new Headers(headers);
  if (requestIdFactory) normalized.set('x-request-id', requestIdFactory());
  const result: Record<string, string> = {};
  normalized.forEach((value, key) => {
    result[key] = value;
  });
  return result;
};

const toApiError = (
  payload: unknown,
  status: number,
  requestId: string | null = null,
): ApiError => {
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
    return new ApiError(candidate.code, candidate.message, status, requestId ?? undefined);
  }
  return new ApiError(
    'invalid_response',
    'The API returned an invalid error response.',
    status,
    requestId ?? undefined,
  );
};

export type { components, operations, paths } from './generated/openapi.js';
