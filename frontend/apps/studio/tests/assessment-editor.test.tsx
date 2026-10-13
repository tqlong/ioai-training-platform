import { fireEvent, render, screen } from '@testing-library/react';

import { AssessmentEditor, emptyAssessmentDraft, type AssessmentDraft } from '../src/components/assessment-editor';

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

  it('prompts before switching response type when custom response data exists, and preserves data on cancel', () => {
    let value = emptyAssessmentDraft('NUMERIC_ANSWER');
    value.response.expected = '42';
    const { rerender } = render(
      <AssessmentEditor
        onChange={(next) => { value = next; }}
        value={value}
      />,
    );

    fireEvent.change(screen.getByRole('combobox', { name: 'Response type' }), { target: { value: 'CODE_FUNCTION' } });
    expect(screen.getByRole('dialog', { name: 'Change response type' })).toBeTruthy();
    expect(screen.getByTestId('modal-warning-icon')).toBeTruthy();
    expect(screen.getByTestId('modal-backdrop')).toBeTruthy();
    expect(screen.getByText(/discard your current response configuration/i)).toBeTruthy();
    const cancelBtn = screen.getByRole('button', { name: 'Cancel' });
    const confirmBtn = screen.getByRole('button', { name: 'Confirm change' });
    const modalDialog = screen.getByRole('dialog', { name: 'Change response type' });
    expect(document.activeElement).toBe(cancelBtn);

    // Focus trap: Tab on Cancel wraps to Confirm
    fireEvent.keyDown(cancelBtn, { key: 'Tab' });
    expect(document.activeElement).toBe(confirmBtn);

    // Focus trap: Shift+Tab on Confirm wraps back to Cancel
    fireEvent.keyDown(confirmBtn, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(cancelBtn);

    // Escape closes modal and restores scroll
    fireEvent.keyDown(modalDialog, { key: 'Escape' });
    expect(screen.queryByRole('dialog', { name: 'Change response type' })).toBeNull();
    expect(document.body.style.overflow).toBe('');
    expect(value.response.type).toBe('NUMERIC_ANSWER');
    expect(value.response.expected).toBe('42');

    // Trigger dialog again and confirm
    fireEvent.change(screen.getByRole('combobox', { name: 'Response type' }), { target: { value: 'CODE_FUNCTION' } });
    expect(screen.getByRole('dialog', { name: 'Change response type' })).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Confirm change' }));

    expect(screen.queryByRole('dialog', { name: 'Change response type' })).toBeNull();
    expect(value.response.type).toBe('CODE_FUNCTION');
    expect(value.response).not.toHaveProperty('expected');
    rerender(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    expect(screen.getByRole('textbox', { name: 'Function signature' })).toBeTruthy();
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

  it('completes populated translations and highlights inconsistent recovered fields', () => {
    let value = emptyAssessmentDraft('QUIZ_SINGLE');
    const { rerender } = render(<AssessmentEditor onChange={(next) => { value = next; }} value={value} />);
    const english = screen.getAllByRole('textbox', { name: 'English' })[0]!;
    fireEvent.change(english, { target: { value: 'Choice A' } });
    expect((value.response.choices as Array<{ content: { en_state: string } }>)[0]?.content.en_state)
      .toBe('COMPLETE');

    const inconsistent = {
      ...value,
      response: {
        ...value.response,
        choices: [{
          id: 'A',
          content: { en: 'Recovered answer', vi: '', en_state: 'PENDING', vi_state: 'PENDING' },
        }, (value.response.choices as unknown[])[1]],
      },
    } as AssessmentDraft;
    rerender(<AssessmentEditor onChange={() => undefined} value={inconsistent} />);

    expect(screen.getAllByRole('textbox', { name: 'English' })[0]?.getAttribute('aria-invalid'))
      .toBe('true');
    expect(screen.getByRole('alert').textContent)
      .toContain('Choice 1 English has text but is marked pending');
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

  it('requires structured point levels for human scoring and exposes the threshold', () => {
    let value = emptyAssessmentDraft('SHORT_ANSWER');
    const { rerender } = render(<AssessmentEditor onChange={next => { value = next; }} value={value} />);
    fireEvent.change(screen.getByRole('combobox', { name: 'Scoring method 1' }), { target: { value: 'RUBRIC_HUMAN' } });
    rerender(<AssessmentEditor onChange={next => { value = next; }} value={value} />);

    expect(screen.getByRole('group', { name: 'Human assessment rubric' })).toBeTruthy();
    expect(screen.getByRole('spinbutton', { name: 'Pass threshold' })).toHaveProperty('value', '1.0');
    expect(screen.getAllByRole('group', { name: /Performance level/ })).toHaveLength(2);
    expect(value.scoring.components[0]?.configuration).toMatchObject({
      criteria: [{ maximum_points: '1', levels: [{ points: '0' }, { points: '1' }] }],
    });
  });
});
