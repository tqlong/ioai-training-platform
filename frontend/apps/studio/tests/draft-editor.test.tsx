import type { AuthorDraft } from '@ioai/api-client';
import { ApiError } from '@ioai/api-client';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

import { DraftEditor } from '../src/components/draft-editor';

const draft: AuthorDraft = {
  problem_id: 'problem-1',
  revision_id: 'revision-1',
  version: 1,
  editorial_status: 'DRAFT',
  slug: null,
  content: null,
  metadata: null,
  response: null,
  scoring: null,
};

describe('draft editor coordinator', () => {
  afterEach(() => { localStorage.clear(); vi.useRealTimers(); });
  it('owns draft identity and keeps editorial actions distinct', () => {
    render(<DraftEditor initialDraft={draft} />);

    expect(screen.getByRole('heading', { name: 'Edit problem' })).toBeTruthy();
    expect(screen.getByText('revision-1', { exact: false })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Save draft' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Validate draft' })).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Preview as learner' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Publish' })).toBeNull();
  });

  it('tracks dirty fields and saves against the current version', async () => {
    const calls: Array<{ revisionId: string; version: number; slug: string | null }> = [];
    render(
      <DraftEditor
        initialDraft={draft}
        saveDraft={async (revisionId, request) => {
          calls.push({
            revisionId,
            version: request.expected_version,
            slug: request.slug ?? null,
          });
          return { ...draft, version: 2, slug: request.slug ?? null };
        }}
      />,
    );

    fireEvent.change(screen.getByRole('textbox', { name: 'URL slug' }), {
      target: { value: 'metrics-basics' },
    });
    expect(screen.getByText('Unsaved changes')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Save draft' }));

    await waitFor(() => expect(screen.getByText('Saved')).toBeTruthy());
    expect(calls).toEqual([
      { revisionId: 'revision-1', version: 1, slug: 'metrics-basics' },
    ]);
    expect(screen.getByText('Version 2')).toBeTruthy();
  });

  it('coalesces idle changes and keeps a versioned recovery copy on failure', async () => {
    vi.useFakeTimers();
    const saveDraft = vi.fn(async () => { throw new Error('offline'); });
    render(<DraftEditor autosaveDelay={800} initialDraft={draft} saveDraft={saveDraft} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'URL slug' }), { target: { value: 'first' } });
    fireEvent.change(screen.getByRole('textbox', { name: 'URL slug' }), { target: { value: 'second' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });
    expect(saveDraft).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Save failed')).toBeTruthy();
    expect(JSON.parse(localStorage.getItem('ioai:studio:recovery:revision-1') ?? '{}')).toMatchObject({ schemaVersion: 1, slug: 'second', serverVersion: 1 });
  });

  it('requires an explicit choice after a revision conflict', async () => {
    render(<DraftEditor initialDraft={draft} saveDraft={async () => { throw new ApiError('REVISION_CONFLICT', 'Newer version', 409); }} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'URL slug' }), { target: { value: 'mine' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save draft' }));
    await waitFor(() => expect(screen.getByRole('dialog', { name: 'Resolve draft conflict' })).toBeTruthy());
    expect(screen.getByRole('button', { name: 'Keep local changes and retry' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Use server version' })).toBeTruthy();
  });

  it('ignores corrupt local recovery data without making the editor unusable', () => {
    localStorage.setItem('ioai:studio:recovery:revision-1', '{broken');
    render(<DraftEditor initialDraft={draft} />);
    expect(screen.queryByRole('dialog', { name: 'Recover unsaved draft' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Save draft' })).toBeTruthy();
  });

  it('remains editable when browser storage is unavailable', async () => {
    const storage = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('blocked'); });
    render(<DraftEditor initialDraft={draft} saveDraft={async () => { throw new Error('offline'); }} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'URL slug' }), { target: { value: 'still-here' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save draft' }));
    await waitFor(() => expect(screen.getByText('Save failed')).toBeTruthy());
    expect((screen.getByRole('textbox', { name: 'URL slug' }) as HTMLInputElement).value).toBe('still-here');
    storage.mockRestore();
  });
});
