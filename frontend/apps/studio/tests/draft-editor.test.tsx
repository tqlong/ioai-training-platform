import type { AuthorDraft, ValidationReport } from '@ioai/api-client';
import { ApiError } from '@ioai/api-client';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

import { DraftEditor } from '../src/components/draft-editor';
import { studioApi } from '../src/api';

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
  afterEach(() => { localStorage.clear(); sessionStorage.clear(); vi.useRealTimers(); });
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

  it('generates a slug from the English title until the author edits it', () => {
    render(<DraftEditor initialDraft={draft} />);
    const title = screen.getByRole('textbox', { name: 'English title' });
    const slug = screen.getByRole('textbox', { name: 'URL slug' }) as HTMLInputElement;

    fireEvent.change(title, { target: { value: 'Hello, AI World!' } });
    expect(slug.value).toBe('hello-ai-world');

    fireEvent.change(slug, { target: { value: 'my-first-problem' } });
    fireEvent.change(title, { target: { value: 'A Different Title' } });
    expect(slug.value).toBe('my-first-problem');

    // Deleting the slug restores automatic generation for new titles
    fireEvent.change(slug, { target: { value: '' } });
    fireEvent.change(title, { target: { value: 'Brand New Title' } });
    expect(slug.value).toBe('brand-new-title');
  });

  it('displays recovery banner when local copy exists and allows restoring or discarding', () => {
    localStorage.setItem('ioai:studio:recovery:revision-1', JSON.stringify({
      schemaVersion: 1,
      problemId: 'problem-1',
      revisionId: 'revision-1',
      serverVersion: 1,
      slug: 'recovered-slug',
      content: {
        title: { en: 'Recovered Title', vi: 'Tiêu đề phục hồi', en_state: 'COMPLETE', vi_state: 'COMPLETE' },
        summary: { en: 'Recovered Summary', vi: 'Tóm tắt phục hồi', en_state: 'COMPLETE', vi_state: 'COMPLETE' },
        objectives: [{ en: 'Recovered Objective', vi: 'Mục tiêu phục hồi', en_state: 'COMPLETE', vi_state: 'COMPLETE' }],
        blocks: [],
      },
      curriculum: { stage: null, difficulty: null, task_type: null, primary_competency: null, secondary_competencies: [], topics: [], prerequisites: [] },
      assessment: { response: { type: 'QUIZ_SINGLE', choices: [] }, scoring: { response_type: 'QUIZ_SINGLE', pass_threshold: '1.0', components: [] }, scoringValid: true },
      resources: { expected_minutes: null, modalities: [], network: 'DENIED', compute_tier: null, runtime_class: null },
    }));

    render(<DraftEditor initialDraft={draft} />);

    expect(screen.getByRole('region', { name: 'Recover unsaved draft' })).toBeTruthy();
    const restoreBtn = screen.getByRole('button', { name: 'Restore local copy' });
    fireEvent.click(restoreBtn);

    expect((screen.getByRole('textbox', { name: 'URL slug' }) as HTMLInputElement).value).toBe('recovered-slug');
    expect((screen.getByRole('textbox', { name: 'English title' }) as HTMLInputElement).value).toBe('Recovered Title');
    expect(screen.queryByRole('region', { name: 'Recover unsaved draft' })).toBeNull();
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

  it('keeps unsaved preview state stable instead of racing the autosave timer', async () => {
    vi.useFakeTimers();
    const saveDraft = vi.fn();
    render(<DraftEditor autosaveDelay={800} initialDraft={draft} saveDraft={saveDraft} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'English title' }), {
      target: { value: 'Unsaved preview title' },
    });

    const previewLink = screen.getByRole('link', { name: 'Preview as learner' });
    previewLink.addEventListener('click', (event) => event.preventDefault());
    fireEvent.click(previewLink);
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });

    expect(saveDraft).not.toHaveBeenCalled();
    expect(JSON.parse(sessionStorage.getItem('ioai:studio:preview:revision-1') ?? '{}'))
      .toMatchObject({
        expected_version: 1,
        unsaved_state: { content: { title: { en: 'Unsaved preview title' } } },
      });
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

  it('updates form fields with server version when choosing "Use server version"', async () => {
    const serverDraft: AuthorDraft = {
      ...draft,
      version: 2,
      slug: 'server-slug',
      content: {
        title: { en: 'Server Title', vi: 'Tiêu đề server', en_state: 'COMPLETE', vi_state: 'COMPLETE' },
        summary: { en: 'Server Summary', vi: 'Tóm tắt server', en_state: 'COMPLETE', vi_state: 'COMPLETE' },
        blocks: [],
        objectives: [{ en: 'Server Objective', vi: 'Mục tiêu server', en_state: 'COMPLETE', vi_state: 'COMPLETE' }],
      },
    };
    render(
      <DraftEditor
        initialDraft={draft}
        saveDraft={async () => { throw new ApiError('REVISION_CONFLICT', 'Newer version', 409); }}
        reloadDraft={async () => serverDraft}
      />,
    );
    fireEvent.change(screen.getByRole('textbox', { name: 'URL slug' }), { target: { value: 'local-slug' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save draft' }));
    await waitFor(() => expect(screen.getByRole('dialog', { name: 'Resolve draft conflict' })).toBeTruthy());

    fireEvent.click(screen.getByRole('button', { name: 'Use server version' }));
    await waitFor(() => expect(screen.queryByRole('dialog', { name: 'Resolve draft conflict' })).toBeNull());

    expect((screen.getByRole('textbox', { name: 'URL slug' }) as HTMLInputElement).value).toBe('server-slug');
    expect((screen.getByRole('textbox', { name: 'English title' }) as HTMLInputElement).value).toBe('Server Title');
  });

  it('hides validation report immediately when a subsequent edit is made', async () => {
    const mockReport: ValidationReport = {
      revision_id: 'revision-1',
      revision_version: 1,
      publication_eligible: false,
      errors: [{ section: 'CONTENT', field_path: 'content.title.en', code: 'REQUIRED', message: 'Title is required.', severity: 'ERROR' }],
      warnings: [],
    };
    render(
      <DraftEditor
        initialDraft={draft}
        validateDraft={async () => mockReport}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Validate draft' }));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Draft validation' })).toBeTruthy());

    fireEvent.change(screen.getByRole('textbox', { name: 'English title' }), { target: { value: 'New title' } });

    expect(screen.queryByRole('heading', { name: 'Draft validation' })).toBeNull();
  });

  it('prompts confirmation when task type changes and response data exists, protecting custom data on cancel', async () => {
    vi.spyOn(studioApi, 'listAuthorVocabulary').mockImplementation(async ({ vocabularyType }) => {
      if (vocabularyType === 'TASK_TYPE') {
        return {
          items: [
            {
              identity: { vocabulary_type: 'TASK_TYPE', code: 'NUMERIC_ANSWER' },
              labels: { en: 'Numeric Answer', vi: 'Câu trả lời dạng số' },
              aliases: [],
              status: 'ACTIVE',
              parent_identity: null,
              breadcrumbs: [],
              availability: { is_available: true, reason_code: 'AVAILABLE', message: 'Available' },
            },
            {
              identity: { vocabulary_type: 'TASK_TYPE', code: 'CODE_FUNCTION' },
              labels: { en: 'Function Implementation', vi: 'Cài đặt hàm' },
              aliases: [],
              status: 'ACTIVE',
              parent_identity: null,
              breadcrumbs: [],
              availability: { is_available: true, reason_code: 'AVAILABLE', message: 'Available' },
            },
          ],
          count: 2,
        };
      }
      return { items: [], count: 0 };
    });

    const initialWithData: AuthorDraft = {
      ...draft,
      metadata: { task_type: ['TASK_TYPE', 'NUMERIC_ANSWER'], stage: ['PATHWAY_STAGE', 'AI_1_FOUNDATIONS'] },
      response: { type: 'NUMERIC_ANSWER', expected: '42' },
      scoring: { response_type: 'NUMERIC_ANSWER', pass_threshold: '1.0', components: [{ method: 'EXACT_MATCH', weight: '1.0', configuration: null }] },
    };
    render(<DraftEditor initialDraft={initialWithData} />);

    // Wait for curriculum loader
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Task type' })).toBeTruthy());

    fireEvent.change(screen.getByRole('combobox', { name: 'Task type' }), { target: { value: 'CODE_FUNCTION' } });

    // Should trigger the response type confirmation modal
    expect(await screen.findByRole('dialog', { name: 'Change response type' })).toBeTruthy();
    expect(screen.getByText(/discard your current response configuration/i)).toBeTruthy();

    // Cancel preserves numeric response
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(screen.queryByRole('dialog', { name: 'Change response type' })).toBeNull();
    expect(screen.getByRole('spinbutton', { name: 'Expected value' })).toBeTruthy();
    expect((screen.getByRole('combobox', { name: 'Response type' }) as HTMLSelectElement).value).toBe('NUMERIC_ANSWER');
  });
});

