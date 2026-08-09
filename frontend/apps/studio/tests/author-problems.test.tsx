import type { AuthorDraftList } from '@ioai/api-client';
import { render, screen } from '@testing-library/react';

import { AuthorProblemsView } from '../src/components/author-problems-view';

const result: AuthorDraftList = {
  count: 1,
  items: [{
    problem_id: 'problem-1',
    revision_id: 'revision-1',
    version: 2,
    editorial_status: 'DRAFT',
    last_saved_at: '2026-08-09T00:00:00Z',
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
});
