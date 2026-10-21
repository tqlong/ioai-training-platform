import type { AuthorDraft, PreviewResponse } from '@ioai/api-client';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { LearnerPreview } from '../src/components/learner-preview';

const draft: AuthorDraft = {
  problem_id: 'problem-1', revision_id: 'revision-1', version: 2,
  editorial_status: 'DRAFT', slug: 'precision-basics', content: null,
  metadata: null, response: null, scoring: null,
};

const preview: PreviewResponse = {
  marker: 'Draft preview - not public',
  learner_problem: {
    slug: 'precision-basics', title: { en: 'Precision basics', vi: '' },
    summary: { en: 'Calculate precision.', vi: '' },
    objectives: [{ en: 'Calculate precision.', vi: '' }], blocks: [],
    stage: { vocabulary_type: 'PATHWAY_STAGE', code: 'AI_1_FOUNDATIONS' },
    difficulty: { vocabulary_type: 'DIFFICULTY', code: 'EASY' },
    topics: [], prerequisites: [], task_type: { code: 'QUIZ_SINGLE' },
    expected_minutes: 10, resources: null, response_schema: { type: 'QUIZ_SINGLE' },
  },
  author_issues: [{
    code: 'TRANSLATION_PENDING', section: 'CONTENT',
    field_path: 'content.title.vi', message: 'Translation is explicitly pending.',
    severity: 'WARNING',
  }],
};

describe('isolated learner preview', () => {
  it('renders the learner structure with persistent warning and no public links', async () => {
    const previewDraft = vi.fn(async () => preview);
    render(<LearnerPreview initialDraft={draft} previewDraft={previewDraft} />);

    expect(await screen.findByRole('heading', { name: 'Precision basics' })).toBeTruthy();
    expect(screen.getByText('Draft preview - not public')).toBeTruthy();
    expect(screen.getByRole('alert').textContent).toContain('Translation is explicitly pending.');
    expect(screen.getByRole('button', { name: 'Open public problem' }).getAttribute('aria-disabled')).toBe('true');
    expect(screen.getByRole('button', { name: 'Continue to next problem' }).getAttribute('aria-disabled')).toBe('true');
    expect(screen.queryByRole('link', { name: 'Open public problem' })).toBeNull();
  });

  it('switches deterministic desktop and mobile preview widths', async () => {
    render(<LearnerPreview initialDraft={draft} previewDraft={async () => preview} />);
    await screen.findByRole('heading', { name: 'Precision basics' });
    const frame = screen.getByTestId('preview-frame');
    expect(frame.getAttribute('data-viewport')).toBe('desktop');
    fireEvent.click(screen.getByRole('button', { name: 'Mobile width' }));
    expect(frame.getAttribute('data-viewport')).toBe('mobile');
  });

  it('uses matching unsaved editor state from session storage', async () => {
    sessionStorage.setItem('ioai:studio:preview:revision-1', JSON.stringify({
      expected_version: 2,
      unsaved_state: { problem_id: 'problem-1', slug: 'unsaved-preview' },
    }));
    const previewDraft = vi.fn(async () => preview);
    render(<LearnerPreview initialDraft={draft} previewDraft={previewDraft} />);

    await waitFor(() => expect(previewDraft).toHaveBeenCalledWith(
      'revision-1', expect.objectContaining({ unsaved_state: expect.objectContaining({ slug: 'unsaved-preview' }) }),
    ));
  });

  it('renders author warnings with synced issue style, count badges, and collapsibility in preview group', async () => {
    const previewWithMultipleIssues: PreviewResponse = {
      ...preview,
      author_issues: [
        {
          code: 'REQUIRED_FIELD_MISSING',
          section: 'CONTENT',
          field_path: 'content.title.en',
          message: 'English title is required.',
          severity: 'ERROR',
        },
        {
          code: 'TRANSLATION_PENDING',
          section: 'CONTENT',
          field_path: 'content.title.vi',
          message: 'Translation is explicitly pending.',
          severity: 'WARNING',
        },
      ],
    };

    render(<LearnerPreview initialDraft={draft} previewDraft={async () => previewWithMultipleIssues} />);
    await screen.findByRole('heading', { name: 'Precision basics' });

    // Header maintains style: Author warnings ✖ 1 ⚠ 1
    const warningsHeading = screen.getByRole('heading', { name: /Author warnings/i });
    expect(warningsHeading.textContent).toContain('Author warnings');
    expect(warningsHeading.textContent).toContain('✖ 1');
    expect(warningsHeading.textContent).toContain('⚠ 1');

    // Issues list has synced inner styles
    const errorItem = screen.getByText('English title is required.').closest('li');
    expect(errorItem?.getAttribute('data-severity')).toBe('ERROR');
    expect(errorItem?.querySelector('.validation-path')?.textContent).toBe('(content.title.en)');

    const warningItem = screen.getByText('Translation is explicitly pending.').closest('li');
    expect(warningItem?.getAttribute('data-severity')).toBe('WARNING');
    expect(warningItem?.querySelector('.validation-path')?.textContent).toBe('(content.title.vi)');

    // Warnings and preview body share the same viewport container
    const warningsAside = screen.getByRole('alert');
    const previewGroup = warningsAside.closest('.preview-viewport-group');
    expect(previewGroup).toBeTruthy();
    expect(previewGroup?.querySelector('[data-testid="preview-frame"]')).toBeTruthy();

    // Collapsible behavior
    const toggleBtn = screen.getByRole('button', { name: 'Collapse' });
    expect(toggleBtn.getAttribute('aria-expanded')).toBe('true');
    expect(screen.getByText('English title is required.')).toBeTruthy();

    // Click to collapse
    fireEvent.click(toggleBtn);
    expect(screen.getByRole('button', { name: 'Expand' }).getAttribute('aria-expanded')).toBe('false');
    // Inner issues list is hidden when collapsed
    expect(screen.queryByText('English title is required.')).toBeNull();
    // Header title and counts are maintained even when collapsed
    expect(warningsHeading.textContent).toContain('Author warnings');
    expect(warningsHeading.textContent).toContain('✖ 1');
    expect(warningsHeading.textContent).toContain('⚠ 1');

    // Click to expand again
    fireEvent.click(screen.getByRole('button', { name: 'Expand' }));
    expect(screen.getByText('English title is required.')).toBeTruthy();
  });

  it('aggregates repetitive warnings with the same code and message into smart grouped item', async () => {
    const previewWithAggregated: PreviewResponse = {
      ...preview,
      author_issues: [
        { code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.title.vi', message: 'Translation is explicitly pending.', severity: 'WARNING' },
        { code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.summary.vi', message: 'Translation is explicitly pending.', severity: 'WARNING' },
        { code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.blocks.0.content.vi', message: 'Translation is explicitly pending.', severity: 'WARNING' },
      ],
    };

    render(<LearnerPreview initialDraft={draft} previewDraft={async () => previewWithAggregated} />);
    await screen.findByRole('heading', { name: 'Precision basics' });

    // Displays aggregate count
    expect(screen.getByText('(3 fields)')).toBeTruthy();
    expect(screen.getByText('(content.title.vi)')).toBeTruthy();
    expect(screen.getByText('(content.summary.vi)')).toBeTruthy();
    expect(screen.getByText('(content.blocks.0.content.vi)')).toBeTruthy();
  });
});
