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
});
