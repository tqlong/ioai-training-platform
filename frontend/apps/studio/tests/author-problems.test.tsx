import type { AuthorDraftList } from '@ioai/api-client';
import { ApiError } from '@ioai/api-client';
import { act, fireEvent, render, screen, within } from '@testing-library/react';
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
  it('shows author-only revision context and resume action inside compact actions menu', () => {
    render(<AuthorProblemsView result={result} />);

    expect(screen.getByRole('heading', { name: 'Author problems' })).toBeTruthy();
    expect(screen.getByText('revision-1', { exact: false })).toBeTruthy();
    expect(screen.getByText('draft')).toBeTruthy();

    // Open More actions menu
    fireEvent.click(screen.getByRole('button', { name: 'More actions' }));
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
    expect(screen.queryByText(/problem-1/)).toBeNull();
    expect(screen.getByText(/problem-review/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /^Draft$/ }));
    expect(screen.getByText('No matching author problems')).toBeTruthy();
  });

  it('collapses each problem to its latest revision and expands history via modal popup dialog', () => {
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

    // Click revision history button
    const historyBtn = screen.getByRole('button', { name: /2 revs/ });
    expect(historyBtn).toBeTruthy();
    fireEvent.click(historyBtn);

    // Slide-over drawer opens showing all revisions
    expect(screen.getByRole('dialog', { name: /Revision history/ })).toBeTruthy();
    expect(screen.getByText('revision-older', { exact: false })).toBeTruthy();

    // Close drawer
    fireEvent.click(screen.getByRole('button', { name: 'Close revision history' }));
    expect(screen.queryByRole('dialog', { name: /Revision history/ })).toBeNull();
  });

  it('traps focus and handles keyboard cycling inside revision history modal dialog', async () => {
    const revisions: AuthorDraftList = {
      count: 2,
      items: [
        { ...result.items[0]!, problem_id: 'problem-1', revision_id: 'rev-latest', version: 2 },
        { ...result.items[0]!, problem_id: 'problem-1', revision_id: 'rev-older', version: 1 },
      ],
    };
    render(<AuthorProblemsView result={revisions} />);

    const historyBtn = screen.getByRole('button', { name: /2 revs/ });
    fireEvent.click(historyBtn);

    const dialog = screen.getByRole('dialog', { name: /Revision history/ });
    expect(dialog).toBeTruthy();
    expect(document.body.style.overflow).toBe('hidden');

    const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(
      'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ));
    expect(focusable.length).toBeGreaterThan(1);
    const first = focusable[0]!;
    const last = focusable[focusable.length - 1]!;

    first.focus();
    expect(document.activeElement).toBe(first);

    // Shift+Tab from first wraps to last
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(last);

    // Tab from last wraps back to first
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: false });
    expect(document.activeElement).toBe(first);

    // Escape closes drawer and restores focus to trigger button
    fireEvent.keyDown(window, { key: 'Escape' });
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(document.body.style.overflow).not.toBe('hidden');
    expect(document.activeElement).toBe(historyBtn);
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

    fireEvent.click(screen.getByRole('button', { name: 'More actions' }));
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

    fireEvent.click(screen.getByRole('button', { name: 'More actions' }));
    fireEvent.click(screen.getByRole('button', { name: 'Archive' }));
    const confirm = screen.getByRole('button', { name: 'Confirm archive' }) as HTMLButtonElement;
    expect(confirm.disabled).toBe(true);
    fireEvent.change(screen.getByRole('textbox', { name: 'Archive note' }), { target: { value: 'Outdated.' } });
    fireEvent.click(confirm);

    await waitFor(() => expect(archiveProblem).toHaveBeenCalledWith(
      'problem-1', expect.objectContaining({ expected_version: 4, note: 'Outdated.' }),
    ));
    expect(await screen.findByText('archived')).toBeTruthy();

    fireEvent.click(screen.getByRole('button', { name: 'More actions' }));
    fireEvent.click(screen.getByRole('button', { name: 'Create new draft' }));
    await waitFor(() => expect(startRevision).toHaveBeenCalledWith(
      'problem-1', expect.objectContaining({ expected_version: 5 }),
    ));
  });

  it('renders backdrop overlay, locks body scroll, and traps focus in archive dialog', async () => {
    const published = { ...result.items[0]!, editorial_status: 'PUBLISHED', version: 4 };
    render(<AuthorProblemsView
      archiveProblem={vi.fn()}
      onOpen={() => undefined}
      result={{ count: 1, items: [published] }}
      startRevision={vi.fn()}
    />);

    fireEvent.click(screen.getByRole('button', { name: 'More actions' }));
    const trigger = screen.getByRole('button', { name: 'Archive' });
    fireEvent.click(trigger);

    // Backdrop is present and body scroll locked
    expect(screen.getByTestId('archive-backdrop')).toBeTruthy();
    expect(document.body.style.overflow).toBe('hidden');

    const note = screen.getByRole('textbox', { name: 'Archive note' });
    const cancelBtn = screen.getByRole('button', { name: 'Cancel' });

    expect(document.activeElement).toBe(note);

    // Shift+Tab from note wraps to cancelBtn
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(cancelBtn);

    // Tab from cancelBtn wraps back to note
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: false });
    expect(document.activeElement).toBe(note);

    // Escape closes dialog and restores focus
    fireEvent.keyDown(window, { key: 'Escape' });
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(document.body.style.overflow).not.toBe('hidden');
    expect(document.activeElement).toBe(trigger);
  });

  it('displays specific server error message when startRevision fails with ApiError', async () => {
    const published = { ...result.items[0]!, editorial_status: 'PUBLISHED', version: 4 };
    const startRevision = vi.fn(async () => {
      throw new ApiError('ACTIVE_DRAFT_EXISTS', 'An active draft revision already exists for this problem.', 409);
    });
    render(<AuthorProblemsView
      archiveProblem={vi.fn()}
      onOpen={() => undefined}
      result={{ count: 1, items: [published] }}
      startRevision={startRevision}
    />);

    fireEvent.click(screen.getByRole('button', { name: 'More actions' }));
    fireEvent.click(screen.getByRole('button', { name: 'Edit as new draft' }));
    await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy());
    expect(screen.getByRole('alert').textContent).toContain('An active draft revision already exists for this problem.');
  });

  it('provides GitHub-style copy buttons for problem and revision IDs', async () => {
    const writeText = vi.fn();
    Object.assign(navigator, {
      clipboard: {
        writeText,
      },
    });

    render(<AuthorProblemsView result={result} />);

    const copyProblemBtn = screen.getByRole('button', { name: 'Copy problem ID' });
    const copyRevisionBtn = screen.getByRole('button', { name: 'Copy revision ID' });
    expect(copyProblemBtn).toBeTruthy();
    expect(copyRevisionBtn).toBeTruthy();

    act(() => {
      fireEvent.click(copyProblemBtn);
    });
    expect(writeText).toHaveBeenCalledWith('problem-1');

    act(() => {
      fireEvent.click(copyRevisionBtn);
    });
    expect(writeText).toHaveBeenCalledWith('revision-1');
  });

  it('renders exact datetime tooltip on Updated time cell for hover', () => {
    render(<AuthorProblemsView result={result} />);
    const timeEl = screen.getByText('Aug 9, 2026', { exact: false });
    expect(timeEl.tagName.toLowerCase()).toBe('time');
    expect(timeEl.getAttribute('title')).toBeTruthy();
    expect(timeEl.getAttribute('title')).toContain('2026');
  });

  it('renders problem title link and direct preview link in actions', () => {
    render(<AuthorProblemsView result={result} />);
    const titleLink = screen.getByRole('link', { name: /Problem #problem-1/i });
    expect(titleLink.getAttribute('href')).toBe('/author/problems/problem-1');

    const previewLink = screen.getByRole('link', { name: 'Preview' });
    expect(previewLink.getAttribute('href')).toBe('/author/problems/problem-1/preview');
  });

  it('renders title, slug, and summary in Problem column and IDs in Identities column', () => {
    const listWithTitleAndSlug: AuthorDraftList = {
      count: 1,
      items: [
        {
          problem_id: 'problem-numeric-123',
          revision_id: 'rev-numeric-456',
          version: 1,
          editorial_status: 'DRAFT',
          last_saved_at: '2026-08-09T00:00:00Z',
          validation_summary: null,
          title: { en: 'Learner e2e NUMERIC_ANSWER' },
          slug: 'learner-e2e-numeric-answer',
          summary: { en: 'Calculate the correct response.' },
        },
      ],
    };
    render(<AuthorProblemsView result={listWithTitleAndSlug} />);

    expect(screen.getByRole('link', { name: 'Learner e2e NUMERIC_ANSWER' })).toBeTruthy();
    expect(screen.getByText('learner-e2e-numeric-answer')).toBeTruthy();
    expect(screen.getByText('Calculate the correct response.')).toBeTruthy();
    expect(screen.getByText('PID:')).toBeTruthy();
    expect(screen.getByText('REV:')).toBeTruthy();
  });

  it('filters by Published tab correctly', () => {
    const listWithPublished: AuthorDraftList = {
      count: 2,
      items: [
        result.items[0]!,
        { ...result.items[0]!, problem_id: 'problem-pub', revision_id: 'rev-pub', editorial_status: 'PUBLISHED' },
      ],
    };
    render(<AuthorProblemsView result={listWithPublished} />);
    fireEvent.click(screen.getByRole('button', { name: 'Published' }));
    expect(screen.queryByText(/Problem #problem-1/i)).toBeNull();
    expect(screen.getByText(/Problem #problem-pub/i)).toBeTruthy();
  });

  it('displays column names in card format for mobile/responsive view', () => {
    render(<AuthorProblemsView result={result} />);

    const rows = screen.getAllByRole('row');
    const card = rows[1]!;

    expect(within(card).getByText('Problem').className).toContain('card-col-label');
    expect(within(card).getByText('Status').className).toContain('card-col-label');
    expect(within(card).getByText('Identities').className).toContain('card-col-label');
    expect(within(card).getByText('Last saved').className).toContain('card-col-label');
    expect(within(card).getByText('Validation').className).toContain('card-col-label');
    expect(within(card).getByText('Actions').className).toContain('card-col-label');
  });
});
