import { fireEvent, render, screen } from '@testing-library/react';

import { AssessmentEditor, emptyAssessmentDraft } from '../src/components/assessment-editor';

describe('response and scoring editor', () => {
  it('renders only the selected response fields and clears stale configuration', () => {
    let value = emptyAssessmentDraft('NUMERIC_ANSWER');
    const { rerender } = render(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    expect(screen.getByRole('spinbutton', { name: 'Expected value' })).toBeTruthy();
    expect(screen.queryByRole('textbox', { name: 'Function signature' })).toBeNull();

    fireEvent.change(screen.getByRole('combobox', { name: 'Response type' }), { target: { value: 'CODE_FUNCTION' } });
    rerender(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);

    expect(screen.queryByRole('spinbutton', { name: 'Expected value' })).toBeNull();
    expect(screen.getByRole('textbox', { name: 'Function signature' })).toBeTruthy();
    expect(value.response).toMatchObject({ type: 'CODE_FUNCTION', language: 'PYTHON' });
    expect(value.response).not.toHaveProperty('expected');
  });

  it('supports keyboard-safe repeated quiz choices', () => {
    let value = emptyAssessmentDraft('QUIZ_SINGLE');
    const { rerender } = render(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    fireEvent.click(screen.getByRole('button', { name: 'Add choice' }));
    rerender(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    expect(screen.getAllByRole('group', { name: /^Choice \d+$/ })).toHaveLength(3);
    fireEvent.click(screen.getByRole('button', { name: 'Remove choice 3' }));
    expect(value.response).toMatchObject({ type: 'QUIZ_SINGLE' });
    expect(value.response.choices).toHaveLength(2);
  });

  it('displays the exact decimal total and blocks validation until 1.0', () => {
    let value = emptyAssessmentDraft('SHORT_ANSWER');
    const { rerender } = render(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'Scoring weight 1' }), { target: { value: '0.3' } });
    rerender(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    expect(screen.getByText('Exact total: 0.3')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('must total exactly 1.0');
    expect(value.scoringValid).toBe(false);
  });
});
