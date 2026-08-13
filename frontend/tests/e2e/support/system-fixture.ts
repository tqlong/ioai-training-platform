import { expect, type APIRequestContext } from '@playwright/test';

const apiBase = process.env.API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

export type ProblemFixture = {
  problemId: string;
  revisionId: string;
  slug: string;
  version: number;
};

const localized = (en: string, vi: string) => ({
  en,
  vi,
  en_state: 'COMPLETE',
  vi_state: 'COMPLETE',
});

export async function createHumanProblem(
  request: APIRequestContext,
  slug: string,
  target: 'APPROVED' | 'PUBLISHED',
): Promise<ProblemFixture> {
  const createdResponse = await request.post(`${apiBase}/author/problems`, { data: {} });
  expect(createdResponse.ok(), await createdResponse.text()).toBeTruthy();
  const created = await createdResponse.json() as {
    problem_id: string;
    revision_id: string;
    version: number;
  };
  const saveResponse = await request.put(
    `${apiBase}/author/revisions/${created.revision_id}`,
    { data: {
      problem_id: created.problem_id,
      expected_version: created.version,
      client_save_key: `a11y-save-${slug}`,
      slug,
      content: {
        title: localized('Accessible system problem', 'Bài toán hệ thống dễ tiếp cận'),
        summary: localized('Explain one classification result.', 'Giải thích một kết quả phân loại.'),
        objectives: [localized('Explain precision from a confusion matrix.', 'Giải thích precision từ ma trận nhầm lẫn.')],
        blocks: [{
          kind: 'STATEMENT',
          content: localized('Explain the result in one paragraph.', 'Giải thích kết quả trong một đoạn.'),
          order: 1,
          reveal_order: null,
        }],
      },
      metadata: {
        stage: ['PATHWAY_STAGE', 'AI_1_FOUNDATIONS'],
        difficulty: ['DIFFICULTY', 'EASY'],
        primary_competency: ['COMPETENCY', 'EVAL_METRICS'],
        secondary_competencies: [],
        task_type: ['TASK_TYPE', 'SHORT_ANSWER'],
        topics: [['TOPIC', 'EVAL_CONFUSION_MATRIX']],
        prerequisites: [],
        modalities: [['DATA_MODALITY', 'NONE']],
        expected_minutes: 10,
        resources: {
          compute_tier: ['COMPUTE_TIER', 'NONE'],
          runtime_class: ['RUNTIME_CLASS', 'INSTANT'],
          cpu_cores: 0,
          ram_mb: 0,
          gpu_count: 0,
          gpu_vram_mb: 0,
          storage_mb: 0,
          runtime_seconds: 0,
          network_policy: 'DENIED',
        },
      },
      response: {
        type: 'SHORT_ANSWER',
        reference_answer: localized('A reasoned explanation.', 'Một lời giải thích có lập luận.'),
        accepted_keywords: [],
        rubric_guidance: 'Assess the explanation.',
      },
      scoring: {
        response_type: 'SHORT_ANSWER',
        pass_threshold: '1.0',
        components: [{
          method: 'RUBRIC_HUMAN',
          weight: '1.0',
          configuration: {
            criteria: [{
              id: 'reasoning',
              title: localized('Reasoning', 'Lập luận'),
              description: localized('Explains the result correctly.', 'Giải thích kết quả đúng.'),
              maximum_points: '1',
              levels: [
                {
                  id: 'not-yet',
                  label: localized('Not yet', 'Chưa đạt'),
                  description: localized('The explanation is incomplete.', 'Lời giải thích chưa hoàn chỉnh.'),
                  points: '0',
                },
                {
                  id: 'complete',
                  label: localized('Complete', 'Hoàn thành'),
                  description: localized('The explanation is correct.', 'Lời giải thích đúng.'),
                  points: '1',
                },
              ],
            }],
            reviewer_guidance: 'Private guidance must remain private.',
            exemplar: null,
          },
        }],
      },
    } },
  );
  expect(saveResponse.ok(), await saveResponse.text()).toBeTruthy();
  await editorialCommand(request, created.revision_id, 'submit-review', 2, slug);
  await editorialCommand(request, created.revision_id, 'approve', 3, slug);
  if (target === 'PUBLISHED') {
    const published = await request.post(
      `${apiBase}/author/revisions/${created.revision_id}/publish`,
      { data: {
        expected_version: 4,
        note: 'Publish accessibility fixture.',
        actor_context: 'a11y-reviewer',
        idempotency_key: `a11y-publish-${slug}`,
      } },
    );
    expect(published.ok(), await published.text()).toBeTruthy();
  }
  return {
    problemId: created.problem_id,
    revisionId: created.revision_id,
    slug,
    version: target === 'PUBLISHED' ? 5 : 4,
  };
}

export async function submitPendingAnswer(
  request: APIRequestContext,
  slug: string,
): Promise<{ attemptId: string; receipt: string }> {
  const receipt = `a11y-private-receipt-${slug}`;
  const response = await request.post(`${apiBase}/problems/${slug}/submissions`, {
    data: {
      submission_key: `a11y-submission-${slug}`,
      receipt,
      response: { type: 'SHORT_ANSWER', text: 'A reasoned accessible answer.' },
    },
  });
  expect(response.ok(), await response.text()).toBeTruthy();
  const payload = await response.json() as { attempt_id: string };
  return { attemptId: payload.attempt_id, receipt };
}

async function editorialCommand(
  request: APIRequestContext,
  revisionId: string,
  action: 'submit-review' | 'approve',
  version: number,
  slug: string,
) {
  const response = await request.post(`${apiBase}/author/revisions/${revisionId}/${action}`, {
    data: {
      expected_version: version,
      note: 'Accessibility system review.',
      actor_context: 'a11y-reviewer',
      operation_id: `a11y-${action}-${slug}`,
    },
  });
  expect(response.ok(), await response.text()).toBeTruthy();
}
