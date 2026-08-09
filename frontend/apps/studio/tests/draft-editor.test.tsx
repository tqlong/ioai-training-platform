import type { AuthorDraft } from '@ioai/api-client';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

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
});
