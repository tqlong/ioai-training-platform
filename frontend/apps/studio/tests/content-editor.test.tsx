import { fireEvent, render, screen } from '@testing-library/react';

import { ContentEditor, emptyContentDraft } from '../src/components/content-editor';

describe('bilingual structured content editor', () => {
  it('switches languages without losing either translation', () => {
    let value = emptyContentDraft();
    const { rerender } = render(
      <ContentEditor onChange={(next) => { value = next; }} value={value} />,
    );

    fireEvent.change(screen.getByRole('textbox', { name: 'English title' }), {
      target: { value: 'Confusion matrix' },
    });
    rerender(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    fireEvent.click(screen.getByRole('button', { name: 'Edit Vietnamese' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Vietnamese title' }), {
      target: { value: 'Ma trận nhầm lẫn' },
    });
    rerender(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    fireEvent.click(screen.getByRole('button', { name: 'Edit English' }));

    expect(screen.getByRole('textbox', { name: 'English title' }).getAttribute('value'))
      .toBe('Confusion matrix');
    expect(value.title.vi).toBe('Ma trận nhầm lẫn');
  });

  it('marks a missing translation pending and exposes structured fields', () => {
    let value = emptyContentDraft();
    render(<ContentEditor onChange={(next) => { value = next; }} value={value} />);

    expect(screen.getByRole('textbox', { name: 'English learning objective' })).toBeTruthy();
    expect(screen.getByRole('textbox', { name: 'English problem statement' })).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Edit Vietnamese' }));

    expect(value.title.vi_state).toBe('PENDING');
    expect(screen.getByRole('checkbox', { name: 'Vietnamese translation pending' })).toBeTruthy();
    expect(screen.getByRole('status').textContent).toContain('translation is pending');
    expect(screen.getByText('Use your system Vietnamese keyboard')).toBeTruthy();
  });
});
