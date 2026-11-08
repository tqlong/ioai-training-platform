import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import EditProblemPage from '../app/author/problems/[id]/page';
import { studioApi } from '../src/api';

vi.mock('../src/api', () => ({
  studioApi: {
    getAuthorDraft: vi.fn(),
    getAuthorRevision: vi.fn(),
  },
}));

vi.mock('../src/components/draft-editor', () => ({
  DraftEditor: ({ initialDraft }: { initialDraft: { problem_id: string; revision_id: string } }) => (
    <div data-testid="draft-editor">
      Editor for {initialDraft.problem_id} (rev: {initialDraft.revision_id})
    </div>
  ),
}));

describe('EditProblemPage route handler', () => {
  it('loads problem draft by problem_id when no revision searchParam is provided', async () => {
    vi.mocked(studioApi.getAuthorDraft).mockResolvedValueOnce({
      problem_id: 'prob-123',
      revision_id: 'rev-latest',
      version: 2,
      editorial_status: 'DRAFT',
      slug: null,
      content: null,
      metadata: null,
      response: null,
      scoring: null,
    });

    const jsx = await EditProblemPage({ params: { id: 'prob-123' } });
    render(jsx);

    expect(studioApi.getAuthorDraft).toHaveBeenCalledWith('prob-123');
    expect(screen.getByText('Editor for prob-123 (rev: rev-latest)')).toBeTruthy();
  });

  it('loads specific revision snapshot when searchParams.revision is provided', async () => {
    vi.mocked(studioApi.getAuthorRevision).mockResolvedValueOnce({
      problem_id: 'prob-123',
      revision_id: 'rev-snapshot-1',
      version: 1,
      editorial_status: 'PUBLISHED',
      slug: null,
      content: null,
      metadata: null,
      response: null,
      scoring: null,
    });

    const jsx = await EditProblemPage({
      params: { id: 'prob-123' },
      searchParams: { revision: 'rev-snapshot-1' },
    });
    render(jsx);

    expect(studioApi.getAuthorRevision).toHaveBeenCalledWith('rev-snapshot-1');
    expect(screen.getByText('Editor for prob-123 (rev: rev-snapshot-1)')).toBeTruthy();
  });
});
