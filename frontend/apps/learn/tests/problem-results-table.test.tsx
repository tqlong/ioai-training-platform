import { render, screen, within } from '@testing-library/react';

import { ProblemResultsTable } from '../src/components/problem-results-table';


const items = [{
  slug: 'confusion-basics',
  public_short_id: 'confusion-basics',
  title: { en: 'Confusion matrix basics', vi: 'Nhập môn ma trận nhầm lẫn' },
  objective: { en: 'Calculate TP, FP, TN, and FN.', vi: 'Tính TP, FP, TN và FN.' },
  stage_code: 'AI_1_FOUNDATIONS',
  difficulty_code: 'EASY',
  primary_competency_code: 'EVAL_METRICS',
  topic_codes: ['EVAL_CONFUSION_MATRIX', 'EVAL_ACCURACY'],
  remaining_topic_count: 1,
  task_type_code: 'QUIZ_SINGLE',
  expected_minutes: 10,
  compute_tier_code: 'NONE',
  published_at: '2026-08-09T00:00:00Z',
}];

const labels = {
  AI_1_FOUNDATIONS: 'AI Foundations', EASY: 'Easy',
  EVAL_METRICS: 'Evaluate models', EVAL_CONFUSION_MATRIX: 'Confusion matrix',
  EVAL_ACCURACY: 'Accuracy', QUIZ_SINGLE: 'Single answer', NONE: 'None',
};

describe('dense learner results table', () => {
  it('keeps status and evidence separate and renders all scannable columns', () => {
    render(
      <ProblemResultsTable
        items={items}
        labels={labels}
        returnUrl="/problems?stage=AI_1_FOUNDATIONS&q=metrics"
      />,
    );

    const table = screen.getByRole('table', { name: 'Published problems' });
    expect(within(table).getAllByRole('columnheader').map((item) => item.textContent)).toEqual([
      'Status', 'Evidence', 'Problem', 'Stage · Difficulty', 'Primary competency',
      'Topics', 'Type', 'Time', 'Compute',
    ]);
    const row = within(table).getAllByRole('row')[1]!;
    expect(within(row).getByText('Not started')).toBeInTheDocument();
    expect(within(row).getByLabelText('No learning evidence')).toHaveTextContent('—');
    expect(within(row).getByText('AI Foundations · Easy')).toBeInTheDocument();
    expect(within(row).getByText('Evaluate models')).toBeInTheDocument();
    expect(within(row).getByText('10 min')).toBeInTheDocument();
    expect(within(row).getByText('None')).toBeInTheDocument();
    expect(within(row).getByRole('button', { name: 'Show 1 more topic' })).toHaveTextContent('+1');
    expect(within(row).getByRole('link', { name: 'Confusion matrix basics' })).toHaveAttribute(
      'href',
      '/problems/confusion-basics?return_to=%2Fproblems%3Fstage%3DAI_1_FOUNDATIONS%26q%3Dmetrics',
    );
    expect(row).toHaveAttribute('tabindex', '0');
  });
});
