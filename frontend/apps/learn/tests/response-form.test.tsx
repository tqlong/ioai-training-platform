import { fireEvent, render, screen } from '@testing-library/react';

import { ResponseForm } from '../src/components/response-form';


describe('Release 0 response forms', () => {
  it('renders one required single-choice group and keeps an invalid answer editable', () => {
    render(<ResponseForm schema={{ type: 'QUIZ_SINGLE', choices: [
      { id: 'a', content: { en: 'Alpha', vi: 'An-pha' } },
      { id: 'b', content: { en: 'Beta', vi: 'Bê-ta' } },
    ] }} onSubmit={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Choose one answer');
    expect(screen.getAllByRole('radio')).toHaveLength(2);
  });

  it('renders multiple choice and submits selected stable choice IDs', () => {
    const submit = vi.fn();
    render(<ResponseForm schema={{ type: 'QUIZ_MULTIPLE', choices: [
      { id: 'a', content: { en: 'Alpha', vi: 'An-pha' } },
      { id: 'b', content: { en: 'Beta', vi: 'Bê-ta' } },
    ] }} onSubmit={submit} />);
    fireEvent.click(screen.getByRole('checkbox', { name: 'Beta' }));
    fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }));
    expect(submit).toHaveBeenCalledWith({ type: 'QUIZ_MULTIPLE', choice_ids: ['b'] });
  });

  it('shows numeric unit and tolerance guidance without losing malformed input', () => {
    render(<ResponseForm schema={{ type: 'NUMERIC_ANSWER', unit: 'ms', absolute_tolerance: '0.01' }} onSubmit={vi.fn()} />);
    const input = screen.getByRole('textbox', { name: 'Numeric answer' });
    fireEvent.change(input, { target: { value: 'not-a-number' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit answer' }));
    expect(input).toHaveValue('not-a-number');
    expect(screen.getByText('Answer in ms. Accepted tolerance: ±0.01.')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('Enter a finite number');
  });

  it('bounds short answers and provides visible required guidance', () => {
    render(<ResponseForm schema={{ type: 'SHORT_ANSWER' }} onSubmit={vi.fn()} />);
    expect(screen.getByRole('textbox', { name: 'Short answer' })).toHaveAttribute('maxlength', '4000');
  });

  it('shows published Python function context without deferred execution controls', () => {
    render(<ResponseForm schema={{ type: 'CODE_FUNCTION', language: 'PYTHON', signature: 'def solve(x):', starter_code: 'def solve(x):\n    pass', public_tests: [{ id: 'one', invocation: 'solve(1)', expected: '1' }] }} onSubmit={vi.fn()} />);
    expect(screen.getByRole('textbox', { name: 'Python code' })).toHaveValue('def solve(x):\n    pass');
    expect(screen.getByText('def solve(x):')).toBeInTheDocument();
    expect(screen.getByText('solve(1) → 1')).toBeInTheDocument();
    expect(screen.queryByText(/GPU|hosted notebook|distributed/i)).not.toBeInTheDocument();
  });
});
