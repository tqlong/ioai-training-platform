import { expect, test, type APIRequestContext, type APIResponse } from '@playwright/test';

import { createHumanProblem, submitPendingAnswer } from './support/system-fixture';

const apiBase = process.env.API_BASE_URL ?? 'http://127.0.0.1:58010/api/v1';
const slug = 'backup-restore-representative';

test('creates representative recoverable PostgreSQL history', async ({ request }) => {
  const published = await createHumanProblem(request, slug, 'PUBLISHED');
  const { attemptId } = await submitPendingAnswer(request, slug);

  const feedback = await request.post(`${apiBase}/problems/${slug}/feedback`, {
    data: {
      feedback_key: 'backup-restore-feedback',
      category: 'CONTENT_ISSUE',
      message: 'Representative recoverable feedback.',
    },
  });
  await expectApiOk(feedback);

  const firstDecision = await request.post(
    `${apiBase}/author/assessments/${attemptId}/decisions`,
    { data: {
      selections: [{
        component_index: 0,
        criterion_id: 'reasoning',
        level_id: 'complete',
        feedback: 'First recoverable criterion decision.',
      }],
      overall_feedback: 'First recoverable assessment.',
    } },
  );
  await expectApiOk(firstDecision);
  const first = await firstDecision.json() as {
    latest_decision: { decision_id: string };
  };
  const correction = await request.post(
    `${apiBase}/author/assessments/${attemptId}/decisions`,
    { data: {
      selections: [{
        component_index: 0,
        criterion_id: 'reasoning',
        level_id: 'not-yet',
        feedback: 'Corrected recoverable criterion decision.',
      }],
      expected_decision_id: first.latest_decision.decision_id,
      correction_reason: 'Preserve append-only correction history.',
    } },
  );
  await expectApiOk(correction);

  const currentResponse = await request.get(
    `${apiBase}/author/problems/${published.problemId}`,
  );
  await expectApiOk(currentResponse);
  const current = await currentResponse.json() as Record<string, unknown> & {
    revision_id: string;
    version: number;
  };
  const startedResponse = await request.post(
    `${apiBase}/author/problems/${published.problemId}/revisions`,
    { data: {
      source_revision_id: current.revision_id,
      expected_version: current.version,
      operation_id: 'backup-restore-successor',
    } },
  );
  await expectApiOk(startedResponse);
  const started = await startedResponse.json() as Record<string, unknown> & {
    problem_id: string;
    revision_id: string;
    version: number;
    content: Record<string, unknown> & { title: Record<string, unknown> };
  };
  const savedResponse = await request.put(
    `${apiBase}/author/revisions/${started.revision_id}`,
    { data: {
      problem_id: started.problem_id,
      expected_version: started.version,
      client_save_key: 'backup-restore-successor-save',
      slug,
      content: {
        ...started.content,
        title: {
          ...started.content.title,
          en: 'Recoverable successor snapshot',
        },
      },
      metadata: started.metadata,
      response: started.response,
      scoring: started.scoring,
    } },
  );
  await expectApiOk(savedResponse);
  await editorialCommand(request, started.revision_id, 'submit-review', 2);
  await editorialCommand(request, started.revision_id, 'approve', 3);
  const successor = await request.post(
    `${apiBase}/author/revisions/${started.revision_id}/publish`,
    { data: {
      expected_version: 4,
      note: 'Publish recoverable successor.',
      actor_context: 'recovery-reviewer',
      idempotency_key: 'backup-restore-successor-publish',
    } },
  );
  await expectApiOk(successor);
});

async function editorialCommand(
  request: APIRequestContext,
  revisionId: string,
  action: 'submit-review' | 'approve',
  version: number,
) {
  const response = await request.post(`${apiBase}/author/revisions/${revisionId}/${action}`, {
    data: {
      expected_version: version,
      note: 'Recovery rehearsal editorial transition.',
      actor_context: 'recovery-reviewer',
      operation_id: `backup-restore-${action}`,
    },
  });
  await expectApiOk(response);
}

async function expectApiOk(response: APIResponse) {
  expect(response.ok(), `${response.status()} ${await response.text()}`).toBeTruthy();
}
