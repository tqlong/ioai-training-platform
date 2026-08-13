import { loadProblemDetail } from '../src/problem-detail-loader';


const problem = {
  slug: 'metrics-basics',
  public_short_id: 'metrics-basics',
  permanent_url: '/problems/metrics-basics',
  title: { en: 'Metrics', vi: 'Độ đo' },
  summary: { en: 'Read metrics.', vi: 'Đọc độ đo.' },
  objective: { en: 'Calculate metrics.', vi: 'Tính độ đo.' },
  blocks: [],
  stage_code: 'AI_1_FOUNDATIONS',
  difficulty_code: 'EASY',
  primary_competency_code: 'EVAL_METRICS',
  secondary_competency_codes: [],
  topic_codes: ['EVAL_CONFUSION_MATRIX'],
  prerequisite_codes: [],
  prerequisites: [],
  modality_codes: ['NONE'],
  task_type_code: 'QUIZ_SINGLE',
  expected_minutes: 10,
  resources: {
    compute_tier_code: 'NONE', runtime_class_code: 'INSTANT', cpu_cores: 0,
    ram_mb: 0, gpu_count: 0, gpu_vram_mb: 0, storage_mb: 0,
    runtime_seconds: 0, network_policy: 'DENIED',
  },
  response_schema: { type: 'QUIZ_SINGLE' },
  feedback_available: true,
  recommendation_url: '/api/v1/problems/metrics-basics/recommendation',
  published_at: '2026-08-09T00:00:00Z',
};

it('loads detail with canonical local labels and no vocabulary API fan-out', async () => {
  const api = {
    getPublicProblem: vi.fn().mockResolvedValue(problem),
    listPublicVocabulary: vi.fn().mockRejectedValue(new Error('must not be called')),
  };

  const loaded = await loadProblemDetail(api, 'metrics-basics');

  expect(api.getPublicProblem).toHaveBeenCalledTimes(1);
  expect(api.listPublicVocabulary).not.toHaveBeenCalled();
  expect(loaded.problem).toBe(problem);
  expect(loaded.labels).toEqual(expect.objectContaining({
    AI_1_FOUNDATIONS: 'AI Foundations',
    EASY: 'Easy',
    EVAL_METRICS: 'Metrics',
    EVAL_CONFUSION_MATRIX: 'Confusion Matrix',
    QUIZ_SINGLE: 'Single-answer Quiz',
    'COMPUTE_TIER:NONE': 'None',
    'DATA_MODALITY:NONE': 'No Dataset',
  }));
});
