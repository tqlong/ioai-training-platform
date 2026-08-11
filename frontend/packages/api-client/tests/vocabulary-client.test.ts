import { describe, expect, it, vi } from 'vitest';

import { createApiClient } from '../src';

describe('generated vocabulary client', () => {
  it('sends bounded anonymous feedback with its retry key', async () => {
    const fetchFn = vi.fn(async () => Response.json({ receipt_id: 'feedback-1', message: 'Recorded.' }, { status: 201 }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const result = await client.submitPublicFeedback('metrics', {
      feedback_key: 'feedback-key', category: 'TYPO', message: 'A typo.',
    });
    expect(result.receipt_id).toBe('feedback-1');
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/problems/metrics/feedback',
      expect.objectContaining({ method: 'POST' }),
    );
  });
  it('submits a discriminated learner answer with its retry key', async () => {
    const fetchFn = vi.fn(async () => Response.json({ attempt_id: 'attempt-1', outcome: 'ACCEPTED_RESULT', score: '1.0', passed: true, components: [], message: 'Assessed.' }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const result = await client.submitPublicProblem('metrics', {
      submission_key: 'retry-key', receipt: 'private-receipt-1234', response: { type: 'QUIZ_SINGLE', choice_id: 'a' },
    });
    expect(result.outcome).toBe('ACCEPTED_RESULT');
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/problems/metrics/submissions',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ submission_key: 'retry-key', receipt: 'private-receipt-1234', response: { type: 'QUIZ_SINGLE', choice_id: 'a' } }) }),
    );
  });
  it('gets one typed published problem detail by stable slug', async () => {
    const fetchFn = vi.fn(async () => Response.json({ slug: 'metrics-basics' }));
    const client = createApiClient({
      baseUrl: 'http://localhost:8000/api/v1',
      fetchFn,
    });

    const result = await client.getPublicProblem('metrics basics');

    expect(result.slug).toBe('metrics-basics');
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/problems/metrics%20basics',
      expect.objectContaining({ cache: 'no-store' }),
    );
  });
  it('lists published problems with canonical discovery parameters', async () => {
    const fetchFn = vi.fn(async () => Response.json({
      items: [], total: 0, page: 2, page_size: 10,
      active_filters: { stage: 'AI_1_FOUNDATIONS', sort: 'TITLE' },
    }));
    const client = createApiClient({
      baseUrl: 'http://localhost:8000/api/v1',
      fetchFn,
    });

    await client.listPublicProblems({
      stage: 'AI_1_FOUNDATIONS',
      includeSubtopics: false,
      sort: 'TITLE',
      page: 2,
      pageSize: 10,
    });

    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/problems?stage=AI_1_FOUNDATIONS&include_subtopics=false&sort=TITLE&page=2&page_size=10',
      expect.objectContaining({ cache: 'no-store' }),
    );
  });

  it('requests one next recommendation with bounded local context', async () => {
    const fetchFn = vi.fn(async () => Response.json({
      slug: 'next-problem', permanent_url: '/problems/next-problem',
      title: { en: 'Next', vi: 'Tiếp theo' }, stage_code: 'AI_1_FOUNDATIONS',
      difficulty_code: 'EASY', expected_minutes: 10, compute_tier_code: 'NONE',
      label: 'Recommended next', reason: 'Matches the editorial path.',
    }));
    const client = createApiClient({
      baseUrl: 'http://localhost:8000/api/v1',
      fetchFn,
    });

    const result = await client.getPublicRecommendation('current', {
      stage: 'AI_1_FOUNDATIONS',
      completed: ['current'],
      evidence: ['TOPIC:EVAL_CONFUSION_MATRIX:PRACTICED'],
    });

    expect(result?.slug).toBe('next-problem');
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/problems/current/recommendation?stage=AI_1_FOUNDATIONS&completed=current&evidence=TOPIC%3AEVAL_CONFUSION_MATRIX%3APRACTICED',
      expect.objectContaining({ cache: 'no-store' }),
    );
  });

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

  it('records a vocabulary proposal through the author command', async () => {
    const fetchFn = vi.fn(async () => Response.json({
      proposal_id: 'proposal-1', vocabulary_type: 'TOPIC', note: 'Add graph cuts',
      status: 'PENDING', created_at: '2026-08-09T00:00:00Z',
    }, { status: 201 }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });

    await client.recordVocabularyProposal({ vocabulary_type: 'TOPIC', note: 'Add graph cuts' });

    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/author/vocabulary/proposals',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ vocabulary_type: 'TOPIC', note: 'Add graph cuts' }) }),
    );
  });

  it('surfaces FastAPI detail errors with their stable machine code', async () => {
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn: async () => Response.json({ detail: { code: 'REVISION_CONFLICT', message: 'A newer draft version exists.', current_version: 3 } }, { status: 409 }) });
    await expect(client.saveAuthorDraft('revision-1', { problem_id: 'problem-1', expected_version: 2 })).rejects.toMatchObject({ code: 'REVISION_CONFLICT', status: 409 });
  });

  it('validates an exact saved author revision version', async () => {
    const fetchFn = vi.fn(async () => Response.json({ revision_id: 'revision-1', revision_version: 2, errors: [], warnings: [], publication_eligible: true }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    await client.validateAuthorDraft('revision-1', 2);
    expect(fetchFn).toHaveBeenCalledWith('http://localhost:8000/api/v1/author/revisions/revision-1/validate', expect.objectContaining({ method: 'POST', body: '{"expected_version":2}' }));
  });

  it('requests an isolated author preview with explicit unsaved state', async () => {
    const fetchFn = vi.fn(async () => Response.json({ marker: 'Draft preview - not public', learner_problem: {}, author_issues: [] }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const request = { expected_version: 2, unsaved_state: { problem_id: 'problem-1', slug: 'preview-only', content: null, metadata: null, response: null, scoring: null } };
    await client.previewAuthorDraft('revision-1', request);
    expect(fetchFn).toHaveBeenCalledWith('http://localhost:8000/api/v1/author/revisions/revision-1/preview', expect.objectContaining({ method: 'POST', body: JSON.stringify(request) }));
  });

  it('sends author-list search and editorial status filters', async () => {
    const fetchFn = vi.fn(async () => Response.json({ items: [], count: 0 }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    await client.listAuthorDrafts({ search: 'metrics', editorialStatus: 'DRAFT' });
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/author/problems?search=metrics&editorial_status=DRAFT',
      expect.any(Object),
    );
  });

  it('never caches mutable author draft reads', async () => {
    const fetchFn = vi.fn(async () => Response.json({
      problem_id: 'problem-1', revision_id: 'revision-1', version: 8,
      editorial_status: 'DRAFT', slug: null, content: null, metadata: null,
      response: null, scoring: null,
    }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });

    await client.getAuthorDraft('problem-1');

    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/author/problems/problem-1',
      expect.objectContaining({ cache: 'no-store' }),
    );
  });

  it('sends versioned editorial commands and reads uncached history', async () => {
    const fetchFn = vi.fn(async () => Response.json({ items: [] }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const request = {
      expected_version: 2, note: 'Approved.', actor_context: 'local-reviewer',
      operation_id: 'approve-1',
    };

    await client.transitionAuthorRevision('revision-1', 'approve', request);
    await client.getEditorialHistory('revision-1');

    expect(fetchFn).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/author/revisions/revision-1/approve',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(request) }),
    );
    expect(fetchFn).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/api/v1/author/revisions/revision-1/history',
      expect.objectContaining({ cache: 'no-store' }),
    );
  });

  it('publishes with a bounded idempotent author command', async () => {
    const fetchFn = vi.fn(async () => Response.json({
      snapshot_id: 'snapshot-1', slug: 'metrics',
      public_url: '/problems/metrics', published_at: '2026-08-09T00:00:00Z',
    }));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const request = {
      expected_version: 3, note: 'Publish.', actor_context: 'local-reviewer',
      idempotency_key: 'publish-1',
    };

    const result = await client.publishAuthorRevision('revision-1', request);

    expect(result.public_url).toBe('/problems/metrics');
    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/author/revisions/revision-1/publish',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(request) }),
    );
  });

  it('starts a successor revision through the author problem boundary', async () => {
    const fetchFn = vi.fn(async () => Response.json({}));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const request = {
      source_revision_id: 'revision-1', expected_version: 4, operation_id: 'revise-1',
    };

    await client.startAuthorRevision('problem-1', request);

    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/author/problems/problem-1/revisions',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(request) }),
    );
  });

  it('archives through an explicit versioned author command', async () => {
    const fetchFn = vi.fn(async () => Response.json({}));
    const client = createApiClient({ baseUrl: 'http://localhost:8000/api/v1', fetchFn });
    const request = {
      expected_version: 4, note: 'Outdated.', actor_context: 'local-reviewer',
      operation_id: 'archive-1',
    };

    await client.archiveAuthorProblem('problem-1', request);

    expect(fetchFn).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/author/problems/problem-1/archive',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(request) }),
    );
  });
});
