import { render, screen } from '@testing-library/react';

import { ProblemDetail } from '../src/components/problem-detail';
import { safeReturnUrl } from '../src/problem-navigation';


const problem = {
  slug: 'metrics-basics', public_short_id: 'metrics-basics',
  permanent_url: '/problems/metrics-basics',
  title: { en: 'Metrics basics', vi: 'Độ đo cơ bản' },
  summary: { en: 'Read a confusion matrix.', vi: 'Đọc ma trận nhầm lẫn.' },
  objective: { en: 'Calculate precision.', vi: 'Tính precision.' },
  blocks: [
    { kind: 'STATEMENT', content: { en: 'Find precision.', vi: 'Tìm precision.' }, order: 1, reveal_order: null },
    { kind: 'HINT', content: { en: 'Use TP / predicted positive.', vi: 'Dùng TP / dự đoán dương.' }, order: 2, reveal_order: 1 },
  ],
  stage_code: 'AI_1_FOUNDATIONS', difficulty_code: 'EASY',
  primary_competency_code: 'EVAL_METRICS', secondary_competency_codes: [],
  topic_codes: ['EVAL_CONFUSION_MATRIX'], prerequisite_codes: ['MATH_RATIOS'],
  prerequisites: [{ relationship: 'RECOMMENDED', target_type: 'TOPIC', target_code: 'MATH_RATIOS', target_id: null, minimum_evidence: 'INTRODUCED' }],
  modality_codes: ['NONE'], task_type_code: 'QUIZ_SINGLE', expected_minutes: 10,
  resources: { compute_tier_code: 'NONE', runtime_class_code: 'NONE', cpu_cores: 0, ram_mb: 0, gpu_count: 0, gpu_vram_mb: 0, storage_mb: 0, runtime_seconds: 0, network_policy: 'DENIED' },
  response_schema: { type: 'QUIZ_SINGLE', choices: [{ id: 'a', content: { en: '0.5', vi: '0,5' } }], unit: null, absolute_tolerance: null, language: null, signature: null, starter_code: null, public_tests: null },
  feedback_available: true, recommendation_url: '/api/v1/problems/metrics-basics/recommendation',
  published_at: '2026-08-09T00:00:00Z',
};

describe('permanent learner problem detail', () => {
  it('accepts only internal problem-library return context', () => {
    expect(safeReturnUrl('/problems?stage=AI_1_FOUNDATIONS')).toBe('/problems?stage=AI_1_FOUNDATIONS');
    expect(safeReturnUrl('https://example.test/problems')).toBe('/problems');
    expect(safeReturnUrl('/problems-redirect')).toBe('/problems');
  });
  it('renders the published reading order, metadata, and solving affordances', () => {
    render(<ProblemDetail problem={problem} labels={{ AI_1_FOUNDATIONS: 'AI Foundations', EASY: 'Easy', EVAL_METRICS: 'Evaluate models', EVAL_CONFUSION_MATRIX: 'Confusion matrix', MATH_RATIOS: 'Ratios', NONE: 'None', QUIZ_SINGLE: 'Single answer' }} returnUrl="/problems?stage=AI_1_FOUNDATIONS" />);

    expect(screen.getByRole('heading', { name: 'Metrics basics' })).toBeInTheDocument();
    expect(screen.getByText('AI Foundations · Easy')).toBeInTheDocument();
    expect(screen.getByText('Calculate precision.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Show hint 1' })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Your response' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Report a problem' })).toBeInTheDocument();
    expect(screen.getByText('Data')).toBeInTheDocument();
    expect(screen.getByText('No Dataset')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Back to problem library' })).toHaveAttribute('href', '/problems?stage=AI_1_FOUNDATIONS');
    expect(document.body.textContent).not.toContain('revision_id');
  });
});
