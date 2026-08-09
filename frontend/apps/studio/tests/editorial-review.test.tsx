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

  it('confirms publication with permanent URL and returns focus on Escape', async () => {
    const approved = { ...draft, editorial_status: 'APPROVED', slug: 'metrics-basics' };
    render(<EditorialReviewWorkspace draft={approved} loadHistory={async () => history} onDraftChange={() => undefined} publish={vi.fn()} transition={vi.fn()} />);
    const trigger = screen.getByRole('button', { name: 'Publish' });
    fireEvent.click(trigger);

    const dialog = screen.getByRole('dialog', { name: 'Publish approved revision' });
    expect(dialog.textContent).toContain('/problems/metrics-basics');
    expect(dialog.textContent).toContain('This is different from Draft preview');
    fireEvent.keyDown(dialog, { key: 'Escape' });

    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Publish approved revision' })).toBeNull());
    expect(document.activeElement).toBe(trigger);
  });
});
