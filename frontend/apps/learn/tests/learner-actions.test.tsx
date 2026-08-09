import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { LearnerActions } from '../src/components/learner-actions';


const schema = { type: 'QUIZ_SINGLE', choices: [
  { id: 'a', content: { en: 'Alpha', vi: 'An-pha' } },
  { id: 'b', content: { en: 'Beta', vi: 'Bê-ta' } },
] };

it('keeps feedback labeled, bounded, retryable, and returns focus on close', async () => {
  const feedback = vi.fn()
    .mockRejectedValueOnce(new Error('rate/internal secret'))
    .mockResolvedValueOnce({ receipt_id: 'f1', message: 'Thank you. Your feedback was recorded.' });
  render(<LearnerActions slug="metrics" title="Metrics" stage="AI_1_FOUNDATIONS" schema={schema} submitFeedback={feedback} feedbackKeyGenerator={() => 'feedback-key'} />);
  const open = screen.getByRole('button', { name: 'Report a problem' });
  fireEvent.click(open);
  expect(screen.getByRole('dialog', { name: 'Report a problem' })).toBeInTheDocument();
  expect(screen.getByRole('combobox', { name: 'Category' })).toHaveFocus();
  expect(screen.getByRole('textbox', { name: 'Message' })).toHaveAttribute('maxlength', '2000');
  fireEvent.change(screen.getByRole('textbox', { name: 'Message' }), { target: { value: 'A typo.' } });
  fireEvent.click(screen.getByRole('button', { name: 'Send feedback' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be sent');
  fireEvent.click(screen.getByRole('button', { name: 'Try feedback again' }));
  expect(await screen.findByText('Thank you. Your feedback was recorded.')).toBeInTheDocument();
  expect(feedback.mock.calls[0][1].feedback_key).toBe('feedback-key');
  expect(feedback.mock.calls[1][1].feedback_key).toBe('feedback-key');
  fireEvent.click(screen.getByRole('button', { name: 'Close feedback' }));
  await waitFor(() => expect(open).toHaveFocus());
});

it('shows exactly one eligible continuation only after accepted completion', async () => {
  const assess = vi.fn().mockResolvedValue({ attempt_id: 'a1', outcome: 'ACCEPTED_RESULT', score: '1.0', passed: true, components: [], message: 'Assessed.' });
  const recommend = vi.fn().mockResolvedValue({ slug: 'next', permanent_url: '/problems/next', title: { en: 'Next problem', vi: 'Bài tiếp' }, stage_code: 'AI_1_FOUNDATIONS', difficulty_code: 'EASY', expected_minutes: 10, compute_tier_code: 'NONE', label: 'Recommended next', reason: 'Editorial path.' });
  render(<LearnerActions slug="metrics" title="Metrics" stage="AI_1_FOUNDATIONS" schema={schema} submitAssessment={assess} getRecommendation={recommend} assessmentKeyGenerator={() => 'key'} />);
  expect(screen.queryByRole('link', { name: 'Continue to Next problem' })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('radio', { name: 'Alpha' }));
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }));
  const next = await screen.findByRole('link', { name: 'Continue to Next problem' });
  expect(next).toHaveAttribute('href', '/problems/next?return_to=%2Fproblems%3Fstage%3DAI_1_FOUNDATIONS');
  expect(screen.getAllByRole('link', { name: 'Continue to Next problem' })).toHaveLength(1);
  await waitFor(() => expect(recommend).toHaveBeenCalledOnce());
});
