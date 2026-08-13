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

  it('collapses each problem to its latest revision and expands its history', () => {
    const revisions: AuthorDraftList = {
      count: 3,
      items: [
        {
          ...result.items[0]!,
          revision_id: 'revision-latest',
          version: 5,
          editorial_status: 'ARCHIVED',
          last_saved_at: '2026-08-09T06:45:53Z',
        },
        {
          ...result.items[0]!,
          revision_id: 'revision-older',
          version: 4,
          editorial_status: 'CHANGES_REQUESTED',
          last_saved_at: '2026-08-09T06:45:35Z',
        },
        {
          ...result.items[0]!,
          problem_id: 'problem-2',
          revision_id: 'revision-other',
          last_saved_at: '2026-08-09T06:46:00Z',
        },
      ],
    };
    render(<AuthorProblemsView result={revisions} />);

    expect(screen.getByText('revision-latest', { exact: false })).toBeTruthy();
    expect(screen.queryByText('revision-older', { exact: false })).toBeNull();
    expect(screen.getByText('revision-other', { exact: false })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Show all 2 revisions' })
      .getAttribute('aria-expanded')).toBe('false');

    fireEvent.click(screen.getByRole('button', { name: 'Show all 2 revisions' }));

    expect(screen.getByText('revision-older', { exact: false })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Hide revision history' })
      .getAttribute('aria-expanded')).toBe('true');

    fireEvent.click(screen.getByRole('button', { name: 'Hide revision history' }));
    expect(screen.queryByText('revision-older', { exact: false })).toBeNull();
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

  it('requires confirmation and a note before archiving', async () => {
    const published = { ...result.items[0]!, editorial_status: 'PUBLISHED', version: 4 };
    const archiveProblem = vi.fn(async () => ({
      problem_id: 'problem-1', slug: 'metrics', archived_at: '2026-08-09T00:00:00Z',
    }));
    const startRevision = vi.fn(async () => ({
      problem_id: 'problem-1', revision_id: 'revision-2', version: 1,
      editorial_status: 'DRAFT', slug: null, content: null, metadata: null,
      response: null, scoring: null,
    }));
    render(<AuthorProblemsView
      archiveProblem={archiveProblem}
      onOpen={() => undefined}
      result={{ count: 1, items: [published] }}
      startRevision={startRevision}
    />);

    fireEvent.click(screen.getByRole('button', { name: 'Archive' }));
    const confirm = screen.getByRole('button', { name: 'Confirm archive' }) as HTMLButtonElement;
    expect(confirm.disabled).toBe(true);
    fireEvent.change(screen.getByRole('textbox', { name: 'Archive note' }), { target: { value: 'Outdated.' } });
    fireEvent.click(confirm);

    await waitFor(() => expect(archiveProblem).toHaveBeenCalledWith(
      'problem-1', expect.objectContaining({ expected_version: 4, note: 'Outdated.' }),
    ));
    expect(await screen.findByText('archived')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Create new draft' }));
    await waitFor(() => expect(startRevision).toHaveBeenCalledWith(
      'problem-1', expect.objectContaining({ expected_version: 5 }),
    ));
  });
});
