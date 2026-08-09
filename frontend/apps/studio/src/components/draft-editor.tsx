'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

import type { AuthorDraft, SaveDraftRequest } from '@ioai/api-client';

import { studioApi } from '../api';

type SaveFunction = (
  revisionId: string,
  request: SaveDraftRequest,
) => Promise<AuthorDraft>;

export function DraftEditor({
  initialDraft,
  saveDraft = studioApi.saveAuthorDraft,
}: {
  initialDraft: AuthorDraft;
  saveDraft?: SaveFunction;
}) {
  const [draft, setDraft] = useState(initialDraft);
  const [slug, setSlug] = useState(initialDraft.slug ?? '');
  const [dirtyFields, setDirtyFields] = useState<Set<string>>(new Set());
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');

  const isDirty = dirtyFields.size > 0;
  useEffect(() => {
    const protectUnsaved = (event: BeforeUnloadEvent) => {
      if (!isDirty) return;
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', protectUnsaved);
    return () => window.removeEventListener('beforeunload', protectUnsaved);
  }, [isDirty]);

  const request = useMemo<SaveDraftRequest>(() => ({
    problem_id: draft.problem_id,
    expected_version: draft.version,
    client_save_key: globalThis.crypto?.randomUUID?.() ?? `save-${draft.version}`,
    slug: slug || null,
    content: draft.content,
    metadata: draft.metadata,
    response: draft.response,
    scoring: draft.scoring,
  }), [draft, slug]);

  const save = async () => {
    setSaveState('saving');
    try {
      const saved = await saveDraft(draft.revision_id, request);
      setDraft(saved);
      setDirtyFields(new Set());
      setSaveState('saved');
    } catch {
      setSaveState('failed');
    }
  };

  return (
    <section aria-labelledby="editor-title" className="studio-page editor-page">
      <div className="editor-topbar">
        <div>
          <p className="eyebrow">Structured draft · {draft.editorial_status}</p>
          <h1 id="editor-title">Edit problem</h1>
          <p><code>{draft.revision_id}</code> · <span>Version {draft.version}</span></p>
        </div>
        <div aria-live="polite" className="save-status">
          {saveState === 'saving' && 'Saving...'}
          {saveState === 'saved' && 'Saved'}
          {saveState === 'failed' && 'Save failed'}
          {saveState === 'idle' && (isDirty ? 'Unsaved changes' : 'No unsaved changes')}
        </div>
      </div>

      <nav aria-label="Editor sections" className="editor-sections">
        {['Basics', 'Content', 'Curriculum', 'Response & scoring', 'Resources'].map((label) => (
          <a href={`#${label.toLowerCase().replaceAll(/[^a-z]+/g, '-')}`} key={label}>{label}</a>
        ))}
      </nav>

      <form onSubmit={(event) => { event.preventDefault(); void save(); }}>
        <section aria-labelledby="basics-heading" className="editor-section" id="basics">
          <h2 id="basics-heading">Basics</h2>
          <label>
            <span>Internal problem ID</span>
            <input readOnly value={draft.problem_id} />
          </label>
          <label>
            <span>URL slug</span>
            <input
              aria-label="URL slug"
              onChange={(event) => {
                setSlug(event.target.value);
                setDirtyFields((current) => new Set(current).add('slug'));
                setSaveState('idle');
              }}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              placeholder="generated-after-title"
              value={slug}
            />
          </label>
        </section>

        <div className="editor-actions">
          <button disabled={!isDirty || saveState === 'saving'} type="submit">Save draft</button>
          <button type="button">Validate draft</button>
          <Link href={`/author/problems/${draft.problem_id}/preview`}>Preview as learner</Link>
        </div>
      </form>
    </section>
  );
}
