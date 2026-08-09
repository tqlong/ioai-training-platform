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

  it('adds, reorders, and removes repeated content blocks with named controls', () => {
    let value = emptyContentDraft();
    const { rerender } = render(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    fireEvent.change(screen.getByRole('combobox', { name: 'New block type' }), { target: { value: 'EXAMPLE' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add content block' }));
    rerender(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    expect(value.blocks.filter((block) => block.kind === 'EXAMPLE')).toHaveLength(2);
    fireEvent.click(screen.getByRole('button', { name: 'Move block 8 up' }));
    rerender(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    expect(value.blocks[6]?.kind).toBe('EXAMPLE');
    fireEvent.click(screen.getByRole('button', { name: 'Remove block 7' }));
    expect(value.blocks).toHaveLength(7);
    expect(value.blocks.map((block) => block.order)).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });

  it('links observable-objective guidance to the objective field', () => {
    let value = emptyContentDraft();
    const { rerender } = render(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'English learning objective' }), { target: { value: 'Understand confusion matrices' } });
    rerender(<ContentEditor onChange={(next) => { value = next; }} value={value} />);
    const objective = screen.getByRole('textbox', { name: 'English learning objective' });
    expect(objective.getAttribute('aria-describedby')).toBe('objective-guidance objective-warning');
    expect(screen.getByRole('alert').textContent).toContain('observable verb');
  });
});
