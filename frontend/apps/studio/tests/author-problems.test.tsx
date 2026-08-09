import type { AuthorDraftList } from '@ioai/api-client';
import { fireEvent, render, screen } from '@testing-library/react';
import { waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { AuthorProblemsView } from '../src/components/author-problems-view';

const result: AuthorDraftList = {
  count: 1,
  items: [{
    problem_id: 'problem-1',
    revision_id: 'revision-1',
    version: 2,
    editorial_status: 'DRAFT',
    last_saved_at: '2026-08-09T00:00:00Z',
    validation_summary: null,
  }],
};

describe('IOAI Studio author problem list', () => {
  it('shows author-only revision context and resume action', () => {
    render(<AuthorProblemsView result={result} />);

    expect(screen.getByRole('heading', { name: 'Author problems' })).toBeTruthy();
    expect(screen.getByText('revision-1', { exact: false })).toBeTruthy();
    expect(screen.getByText('draft')).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Resume editing' }).getAttribute('href'))
      .toBe('/author/problems/problem-1');
    expect(screen.queryByText('IOAI Learn')).toBeNull();
  });

  it('shows a useful empty state', () => {
    render(<AuthorProblemsView result={{ count: 0, items: [] }} />);

    expect(screen.getByRole('heading', { name: 'No author problems yet' })).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Create the first problem' })).toBeTruthy();
  });

  it('filters drafts by search and editorial status', () => {
    const twoDrafts: AuthorDraftList = { count: 2, items: [
      result.items[0]!,
      { ...result.items[0]!, problem_id: 'problem-review', revision_id: 'revision-review', editorial_status: 'IN_REVIEW' },
    ] };
    render(<AuthorProblemsView result={twoDrafts} />);
    fireEvent.change(screen.getByRole('searchbox', { name: 'Search author problems' }), { target: { value: 'review' } });
    expect(screen.queryByText('problem-1')).toBeNull();
    expect(screen.getByText('problem-review')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /Draft/ }));
    expect(screen.getByText('No matching author problems')).toBeTruthy();
  });

  it('starts a private successor before editing published content', async () => {
    const published = {
      ...result.items[0]!, editorial_status: 'PUBLISHED', version: 4,
    };
    const startRevision = vi.fn(async () => ({
      problem_id: 'problem-1', revision_id: 'revision-2', version: 1,
      editorial_status: 'DRAFT', slug: null, content: null, metadata: null,
      response: null, scoring: null,
    }));
    const onOpen = vi.fn();
    render(<AuthorProblemsView result={{ count: 1, items: [published] }} startRevision={startRevision} onOpen={onOpen} />);

    fireEvent.click(screen.getByRole('button', { name: 'Edit as new draft' }));

    await waitFor(() => expect(startRevision).toHaveBeenCalledWith(
      'problem-1',
      expect.objectContaining({ source_revision_id: 'revision-1', expected_version: 4 }),
    ));
    expect(onOpen).toHaveBeenCalledWith('problem-1');
  });
});
