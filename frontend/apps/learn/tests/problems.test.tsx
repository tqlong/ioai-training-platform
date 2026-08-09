import { render, screen } from '@testing-library/react';

import {
  ProblemDiscovery,
  parseProblemSearchParams,
} from '../src/components/problem-discovery';


const stages = [
  ['AI_1_FOUNDATIONS', 'AI Foundations', true],
  ['AI_2_COMPETITION_FOUNDATIONS', 'Competition Foundations', true],
  ['AI_3_HIGHSCHOOL', 'High-school Competition', false],
  ['AI_4_STUDENT', 'Collegiate Competition', false],
  ['AI_OPEN', 'Open / Cross-level', false],
] as const;

const topics = [
  ['TOPIC_MATHEMATICS', 'Mathematics', null],
  ['MATH_PROBABILITY', 'Probability', 'TOPIC_MATHEMATICS'],
  ['MATH_BAYES', 'Bayes theorem', 'MATH_PROBABILITY'],
  ['TOPIC_DATA', 'Data', null],
  ['TOPIC_MACHINE_LEARNING', 'Machine Learning', null],
  ['TOPIC_DEEP_LEARNING', 'Deep Learning', null],
  ['TOPIC_EVALUATION', 'Evaluation', null],
  ['TOPIC_PYTHON_COMPUTING', 'Python and Computing', null],
  ['TOPIC_AI_DOMAINS', 'AI Domains', null],
  ['TOPIC_RESPONSIBLE_RESEARCH', 'Responsible AI and Research', null],
] as const;

const vocabulary = {
  stages: stages.map(([code, label, available]) => ({
    code, label, available, availabilityMessage: available ? 'Available' : 'Coming next',
  })),
  topics: topics.map(([code, label, parentCode]) => ({ code, label, parentCode })),
  competencies: [{ code: 'EVAL_METRICS', label: 'Evaluate models' }],
  difficulties: [{ code: 'EASY', label: 'Easy' }],
  taskTypes: [{ code: 'QUIZ_SINGLE', label: 'Single answer' }],
  computeTiers: [{ code: 'NONE', label: 'None' }],
};

describe('IOAI Learn URL-owned discovery', () => {
  it('parses only bounded canonical query state', () => {
    expect(parseProblemSearchParams({
      stage: 'AI_1_FOUNDATIONS', q: ' metrics ', topic: 'MATH_BAYES',
      include_subtopics: 'true', page: '2', page_size: '500', sort: 'TITLE',
      editorial_status: 'APPROVED',
    }, vocabulary)).toEqual(expect.objectContaining({
      stage: 'AI_1_FOUNDATIONS', search: 'metrics', topic: 'MATH_BAYES',
      includeSubtopics: true, page: 2, pageSize: 100, sort: 'TITLE',
    }));
  });

  it('renders ordered stages, compact filters, hierarchy, and URL filter tokens', () => {
    const query = parseProblemSearchParams({
      stage: 'AI_1_FOUNDATIONS', topic: 'MATH_BAYES',
      include_subtopics: 'true', q: 'metrics',
    }, vocabulary);
    render(
      <ProblemDiscovery
        vocabulary={vocabulary}
        query={query}
        resultCount={3}
        problemTitles={['Metrics basics']}
      />,
    );

    const stageRegion = screen.getByRole('group', { name: 'Choose pathway stage' });
    expect(Array.from(stageRegion.children).map((item) => item.textContent)).toEqual([
      'AI Foundations', 'Competition Foundations', 'High-school CompetitionComing next',
      'Collegiate CompetitionComing next', 'Open / Cross-levelComing next',
    ]);
    expect(screen.getByRole('button', { name: /High-school Competition/ })).toBeDisabled();
    expect(screen.getByRole('searchbox', { name: 'Search problems' })).toHaveValue('metrics');
    expect(screen.getByRole('combobox', { name: 'Topic' })).toHaveValue('MATH_BAYES');
    expect(screen.getByRole('checkbox', { name: 'Include subtopics' })).toBeChecked();
    expect(screen.getByText('3 problems')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Remove topic: Bayes theorem' })).toHaveAttribute(
      'href', expect.not.stringContaining('topic='),
    );
    expect(screen.getByRole('link', { name: 'Clear filters' })).toHaveAttribute('href', '/problems');
    expect(screen.getByRole('list', { name: 'Topic family shortcuts' }).children).toHaveLength(8);
    expect(screen.getByText('Metrics basics')).toBeInTheDocument();
    expect(document.body.textContent).not.toContain('Draft preview');
  });
});
