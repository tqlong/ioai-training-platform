import type { operations } from '../src/generated/openapi.js';
import type {
  ApiClient,
  ArchiveProblemRequest,
  AssessmentDecisionRequest,
  EditorialCommandRequest,
  PreviewDraftRequest,
  PublicFeedbackRequest,
  PublicSubmissionRequest,
  PublishRevisionRequest,
  SaveDraftRequest,
  StartRevisionRequest,
} from '../src/index.js';

type JsonRequest<Operation extends keyof operations> =
  operations[Operation] extends {
    requestBody: { content: { 'application/json': infer Request } };
  }
    ? Request
    : never;

type Assert<Condition extends true> = Condition;
type Equal<Left, Right> =
  (<Value>() => Value extends Left ? 1 : 2) extends
  (<Value>() => Value extends Right ? 1 : 2)
    ? true
    : false;

type AsyncResult<Method extends (...arguments_: never[]) => unknown> =
  Awaited<ReturnType<Method>>;

export type GeneratedRequestCompatibility = [
  Assert<Equal<PublicSubmissionRequest, JsonRequest<'submit_problem_api_v1_problems__slug__submissions_post'>>>,
  Assert<Equal<PublicFeedbackRequest, JsonRequest<'submit_feedback_api_v1_problems__slug__feedback_post'>>>,
  Assert<Equal<SaveDraftRequest, JsonRequest<'save_draft_api_v1_author_revisions__revision_id__put'>>>,
  Assert<Equal<PreviewDraftRequest, JsonRequest<'preview_draft_api_v1_author_revisions__revision_id__preview_post'>>>,
  Assert<Equal<EditorialCommandRequest, JsonRequest<'approve_revision_api_v1_author_revisions__revision_id__approve_post'>>>,
  Assert<Equal<PublishRevisionRequest, JsonRequest<'publish_revision_api_v1_author_revisions__revision_id__publish_post'>>>,
  Assert<Equal<StartRevisionRequest, JsonRequest<'start_revision_api_v1_author_problems__problem_id__revisions_post'>>>,
  Assert<Equal<ArchiveProblemRequest, JsonRequest<'archive_problem_api_v1_author_problems__problem_id__archive_post'>>>,
  Assert<Equal<AssessmentDecisionRequest, JsonRequest<'decide_api_v1_author_assessments__attempt_id__decisions_post'>>>,
];

export type GeneratedResponseCompatibility = [
  Assert<Equal<
    AsyncResult<ApiClient['listPublicProblems']>,
    operations['list_problems_api_v1_problems_get']['responses'][200]['content']['application/json']
  >>,
  Assert<Equal<
    AsyncResult<ApiClient['submitPublicProblem']>,
    operations['submit_problem_api_v1_problems__slug__submissions_post']['responses'][200]['content']['application/json']
  >>,
  Assert<Equal<
    AsyncResult<ApiClient['createAuthorDraft']>,
    operations['create_draft_api_v1_author_problems_post']['responses'][201]['content']['application/json']
  >>,
  Assert<Equal<
    AsyncResult<ApiClient['publishAuthorRevision']>,
    operations['publish_revision_api_v1_author_revisions__revision_id__publish_post']['responses'][200]['content']['application/json']
  >>,
];

declare const client: ApiClient;
void client;
