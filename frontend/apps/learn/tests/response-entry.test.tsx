import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { ResponseEntry } from '../src/components/response-entry';


const schema = { type: 'QUIZ_SINGLE', choices: [
  { id: 'a', content: { en: 'Alpha', vi: 'An-pha' } },
  { id: 'b', content: { en: 'Beta', vi: 'Bê-ta' } },
] };

it('retries safely with one key and renders actionable assessment feedback', async () => {
  const submit = vi.fn()
    .mockRejectedValueOnce(new Error('provider secret'))
    .mockResolvedValueOnce({ attempt_id: 'a1', outcome: 'ACCEPTED_RESULT', score: '0.5', passed: false, components: [{ method: 'EXACT_MATCH', score: '0.5' }], message: 'Your answer was assessed.' });
  render(<ResponseEntry slug="metrics" schema={schema} submit={submit} keyGenerator={() => 'stable-key'} />);
  fireEvent.click(screen.getByRole('radio', { name: 'Alpha' }));
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be assessed');
  expect(screen.getByRole('radio', { name: 'Alpha' })).toBeChecked();
  fireEvent.click(screen.getByRole('button', { name: 'Try submission again' }));
  expect(await screen.findByText('Score: 0.5')).toBeInTheDocument();
  await waitFor(() => expect(submit).toHaveBeenCalledTimes(2));
  expect(submit.mock.calls[0][1].submission_key).toBe('stable-key');
  expect(submit.mock.calls[1][1].submission_key).toBe('stable-key');
});

it('renders pending assessment without claiming completion', async () => {
  const submit = vi.fn().mockResolvedValue({ attempt_id: 'a1', outcome: 'PENDING_ASSESSMENT', message: 'Your answer is waiting for assessment.' });
  render(<ResponseEntry slug="metrics" schema={schema} submit={submit} keyGenerator={() => 'key'} />);
  fireEvent.click(screen.getByRole('radio', { name: 'Beta' }));
  fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }));
  expect(await screen.findByText('Your answer is waiting for assessment.')).toBeInTheDocument();
  expect(document.body).not.toHaveTextContent('Completed');
});
