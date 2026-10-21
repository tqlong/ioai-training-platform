import type { AuthorDraft, EditorialHistory } from '@ioai/api-client';
import { ApiError } from '@ioai/api-client';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { EditorialReviewWorkspace } from '../src/components/editorial-review';

const draft: AuthorDraft = {
  problem_id: 'problem-1', revision_id: 'revision-1', version: 2,
  editorial_status: 'IN_REVIEW', slug: 'metrics', content: null,
  metadata: null, response: null, scoring: null,
};

const history: EditorialHistory = {
  items: [{
    source_status: 'DRAFT', target_status: 'IN_REVIEW',
    note: 'Ready for review.', actor_context: 'local-author',
    occurred_at: '2026-08-09T00:00:00Z', operation_id: 'submit-1',
  }],
};

describe('editorial review workspace', () => {
  it('shows text status, immutable history, and state-sensitive actions', async () => {
    render(<EditorialReviewWorkspace draft={draft} loadHistory={async () => history} onDraftChange={() => undefined} transition={vi.fn()} />);

    expect(screen.getByText('In review', { exact: true })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Request changes' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Approve' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Submit for review' })).toBeNull();
    expect(await screen.findByText('Ready for review.')).toBeTruthy();
    expect(screen.getByText(/Draft → In review/)).toBeTruthy();
  });

  it('requires a note and keeps it after a recoverable conflict', async () => {
    const transition = vi.fn(async () => {
      throw new ApiError('REVISION_CONFLICT', 'A newer revision exists.', 409);
    });
    render(<EditorialReviewWorkspace draft={draft} loadHistory={async () => history} onDraftChange={() => undefined} transition={transition} />);
    const approve = screen.getByRole('button', { name: 'Approve' });

    expect((approve as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(screen.getByRole('textbox', { name: 'Editorial note' }), { target: { value: 'Scoring and content checked.' } });
    fireEvent.click(approve);

    expect((await screen.findByRole('alert')).textContent).toContain('A newer revision exists.');
    expect((screen.getByRole('textbox', { name: 'Editorial note' }) as HTMLTextAreaElement).value).toBe('Scoring and content checked.');
    expect(document.activeElement).toBe(screen.getByRole('textbox', { name: 'Editorial note' }));
  });

  it('refreshes version and history after a successful decision', async () => {
    const approved = { ...draft, version: 3, editorial_status: 'APPROVED' };
    const onDraftChange = vi.fn();
    const transition = vi.fn(async () => approved);
    render(<EditorialReviewWorkspace draft={draft} loadHistory={async () => history} onDraftChange={onDraftChange} transition={transition} />);

    fireEvent.change(screen.getByRole('textbox', { name: 'Editorial note' }), { target: { value: 'Approved.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Approve' }));

    await waitFor(() => expect(onDraftChange).toHaveBeenCalledWith(approved));
    expect(transition).toHaveBeenCalledWith('revision-1', 'approve', expect.objectContaining({ expected_version: 2, note: 'Approved.' }));
  });

  it('does not block the next decision on a stalled history refresh', async () => {
    const draftStart = { ...draft, editorial_status: 'DRAFT' };
    const inReview = { ...draftStart, version: 3, editorial_status: 'IN_REVIEW' };
    const onDraftChange = vi.fn();
    const transition = vi.fn(async () => inReview);
    const loadHistory = vi.fn()
      .mockResolvedValueOnce(history)
      .mockImplementation(() => new Promise(() => undefined));
    const { rerender } = render(<EditorialReviewWorkspace
      draft={draftStart}
      loadHistory={loadHistory}
      onDraftChange={onDraftChange}
      transition={transition}
    />);

    fireEvent.change(screen.getByRole('textbox', { name: 'Editorial note' }), {
      target: { value: 'Ready.' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Submit for review' }));
    await waitFor(() => expect(onDraftChange).toHaveBeenCalledWith(inReview));
    rerender(<EditorialReviewWorkspace
      draft={inReview}
      loadHistory={loadHistory}
      onDraftChange={onDraftChange}
      transition={transition}
    />);
    fireEvent.change(screen.getByRole('textbox', { name: 'Editorial note' }), {
      target: { value: 'Approved.' },
    });

    await waitFor(() => expect(
      (screen.getByRole('button', { name: 'Approve' }) as HTMLButtonElement).disabled,
    ).toBe(false));
  });

  it('prevents a second note from being entered while a decision is pending', async () => {
    const transition = vi.fn(() => new Promise<AuthorDraft>(() => undefined));
    render(<EditorialReviewWorkspace
      draft={draft}
      loadHistory={async () => history}
      onDraftChange={() => undefined}
      transition={transition}
    />);
    const note = screen.getByRole('textbox', { name: 'Editorial note' }) as HTMLTextAreaElement;

    fireEvent.change(note, { target: { value: 'Approval in progress.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Approve' }));

    await waitFor(() => expect(transition).toHaveBeenCalledOnce());
    expect(note.disabled).toBe(true);
  });

  it('confirms publication with permanent URL and returns focus on Escape', async () => {
    const approved = { ...draft, editorial_status: 'APPROVED', slug: 'metrics-basics' };
    render(<EditorialReviewWorkspace draft={approved} loadHistory={async () => history} onDraftChange={() => undefined} publish={vi.fn()} transition={vi.fn()} />);
    const trigger = screen.getByRole('button', { name: 'Publish' });
    fireEvent.click(trigger);

    const dialog = screen.getByRole('dialog', { name: 'Publish approved revision' });
    expect(dialog.textContent).toContain('/problems/metrics-basics');
    expect(dialog.textContent).toContain('This is different from Draft preview');
    fireEvent.keyDown(window, { key: 'Escape' });

    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Publish approved revision' })).toBeNull());
    expect(document.activeElement).toBe(trigger);
  });

  it('renders backdrop overlay, locks body scroll, and traps focus in publish dialog', async () => {
    const approved = { ...draft, editorial_status: 'APPROVED', slug: 'metrics-basics' };
    render(<EditorialReviewWorkspace draft={approved} loadHistory={async () => history} onDraftChange={() => undefined} publish={vi.fn()} transition={vi.fn()} />);
    const trigger = screen.getByRole('button', { name: 'Publish' });
    fireEvent.click(trigger);

    // Backdrop overlay is rendered
    expect(screen.getByTestId('modal-backdrop')).toBeTruthy();
    expect(document.body.style.overflow).toBe('hidden');

    const note = screen.getByRole('textbox', { name: 'Publication note' });
    const cancelBtn = screen.getByRole('button', { name: 'Cancel' });

    // Focus starts on note
    expect(document.activeElement).toBe(note);

    // Shift+Tab on first element wraps to cancelBtn (last focusable when confirm is disabled)
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(cancelBtn);

    // Tab on last element wraps back to note
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: false });
    expect(document.activeElement).toBe(note);

    // Close via cancel button restores body overflow and trigger focus
    fireEvent.click(cancelBtn);
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(document.body.style.overflow).not.toBe('hidden');
    expect(document.activeElement).toBe(trigger);
  });
});
