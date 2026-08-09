import { render, screen, waitFor } from '@testing-library/react';

import {
  LearningGuidance,
  parseLearningGuidanceContext,
} from '../src/components/learning-guidance';


const starter = {
  slug: 'metrics-basics',
  title: 'Metrics basics',
  objective: 'Calculate evaluation metrics.',
  stageLabel: 'AI Foundations',
  difficultyLabel: 'Easy',
  expectedMinutes: 15,
  computeLabel: 'None',
};

describe('learning path guidance', () => {
  it('shows one editorial start without implying personalization or failure', () => {
    render(<LearningGuidance starter={starter} storage={undefined} />);

    expect(screen.getByText('Recommended start')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Metrics basics' })).toBeInTheDocument();
    expect(screen.getByText('AI Foundations · Easy')).toBeInTheDocument();
    expect(screen.getByText('15 min · None')).toBeInTheDocument();
    expect(screen.getByText('First published problem in this stage.')).toBeInTheDocument();
    expect(screen.getByText('Set a weekly goal when you are ready.')).toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/personalized|mastered|0 completed/i);
  });

  it('restores only bounded supportive context and limits guidance lists', async () => {
    const storage = {
      getItem: () => JSON.stringify({
        schemaVersion: 1,
        weeklyGoal: { target: 5, completed: 2 },
        currentPath: { label: 'Evaluation basics', completed: 2, total: 6 },
        prerequisites: ['Probability', 'Linear algebra', 'Python', 'Ignored'],
        recentCompleted: [
          { slug: 'one', title: 'One' }, { slug: 'two', title: 'Two' },
          { slug: 'three', title: 'Three' }, { slug: 'four', title: 'Ignored' },
        ],
        suggestedTopics: [
          { code: 'TOPIC_EVALUATION', label: 'Evaluation' },
          { code: 'TOPIC_DATA', label: 'Data' },
          { code: 'TOPIC_AI_DOMAINS', label: 'Ignored' },
        ],
      }),
    };

    render(<LearningGuidance starter={starter} storage={storage} />);

    await waitFor(() => expect(screen.getByText('2 of 5 completed')).toBeInTheDocument());
    expect(screen.getByText('Evaluation basics — 2 of 6')).toBeInTheDocument();
    expect(screen.getAllByTestId('prerequisite-review')).toHaveLength(3);
    expect(screen.getAllByTestId('recent-completion')).toHaveLength(3);
    expect(screen.getAllByTestId('suggested-topic')).toHaveLength(2);
  });

  it('uses bounded completion history to request one public continuation', async () => {
    const storage = {
      getItem: () => JSON.stringify({
        schemaVersion: 1,
        recentCompleted: [{ slug: 'metrics-basics', title: 'Metrics basics' }],
      }),
    };
    const api = {
      getPublicRecommendation: vi.fn(async () => ({
        slug: 'precision-recall',
        permanent_url: '/problems/precision-recall',
        title: { en: 'Precision and recall', vi: 'Precision và recall' },
        stage_code: 'AI_1_FOUNDATIONS',
        difficulty_code: 'EASY',
        expected_minutes: 20,
        compute_tier_code: 'NONE',
        label: 'Recommended next',
        reason: 'Matches your stage and editorial path with available prerequisites.',
      })),
    };

    render(
      <LearningGuidance
        starter={{ ...starter, stageCode: 'AI_1_FOUNDATIONS' }}
        storage={storage}
        api={api}
        labels={{ AI_1_FOUNDATIONS: 'AI Foundations', EASY: 'Easy', NONE: 'None' }}
      />,
    );

    await waitFor(() => expect(screen.getByText('Recommended next')).toBeInTheDocument());
    expect(screen.getByRole('heading', { name: 'Precision and recall' })).toBeInTheDocument();
    expect(api.getPublicRecommendation).toHaveBeenCalledWith('metrics-basics', {
      stage: 'AI_1_FOUNDATIONS', completed: ['metrics-basics'],
    });
  });

  it('rejects corrupt, unversioned, and unbounded local context', () => {
    expect(parseLearningGuidanceContext('{')).toBeNull();
    expect(parseLearningGuidanceContext('{}')).toBeNull();
    expect(parseLearningGuidanceContext(JSON.stringify({
      schemaVersion: 1,
      weeklyGoal: { target: 100_000, completed: -1 },
    }))).toBeNull();
  });
});
