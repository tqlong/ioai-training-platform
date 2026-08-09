'use client';

import { useEffect, useRef, useState } from 'react';

import type { AuthorDraft, PreviewDraftRequest, PreviewResponse } from '@ioai/api-client';

import { studioApi } from '../api';

type Viewport = 'desktop' | 'mobile';

const localized = (value: unknown, language: 'en' | 'vi' = 'en'): string => {
  if (typeof value !== 'object' || value === null) return '';
  const record = value as Record<string, unknown>;
  return typeof record[language] === 'string' ? record[language] as string : '';
};

const code = (value: unknown): string => {
  if (typeof value !== 'object' || value === null) return '';
  const candidate = (value as Record<string, unknown>).code;
  return typeof candidate === 'string' ? candidate : '';
};

export function LearnerPreview({
  initialDraft,
  previewDraft = studioApi.previewAuthorDraft,
}: {
  initialDraft: AuthorDraft;
  previewDraft?: (revisionId: string, request: PreviewDraftRequest) => Promise<PreviewResponse>;
}) {
  const [viewport, setViewport] = useState<Viewport>('desktop');
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [failed, setFailed] = useState(false);
  const requested = useRef(false);

  useEffect(() => {
    if (requested.current) return;
    requested.current = true;
    const key = `ioai:studio:preview:${initialDraft.revision_id}`;
    let request: PreviewDraftRequest = { expected_version: initialDraft.version };
    try {
      const stored = sessionStorage.getItem(key);
      if (stored) request = JSON.parse(stored) as PreviewDraftRequest;
      sessionStorage.removeItem(key);
    } catch {
      // A saved-version preview remains available when browser storage is blocked.
    }
    void previewDraft(initialDraft.revision_id, request)
      .then((result) => setPreview(result))
      .catch(() => setFailed(true));
  }, [initialDraft.revision_id, initialDraft.version, previewDraft]);

  const learner = preview?.learner_problem ?? {};
  const objectives = Array.isArray(learner.objectives) ? learner.objectives : [];
  const blocks = Array.isArray(learner.blocks) ? learner.blocks : [];

  return <section aria-labelledby="preview-page-heading" className="preview-page">
    <div className="draft-preview-banner" role="note">Draft preview - not public</div>
    <div className="preview-toolbar">
      <div>
        <p className="eyebrow">IOAI Studio · author preview</p>
        <h1 id="preview-page-heading">Learner-format preview</h1>
      </div>
      <div aria-label="Preview width" role="group">
        <button aria-pressed={viewport === 'desktop'} onClick={() => setViewport('desktop')} type="button">Desktop width</button>
        <button aria-pressed={viewport === 'mobile'} onClick={() => setViewport('mobile')} type="button">Mobile width</button>
      </div>
    </div>
    {failed && <p role="alert">Preview could not be loaded for this author revision.</p>}
    {!preview && !failed && <p role="status">Loading preview…</p>}
    {preview && <>
      {preview.author_issues.length > 0 && <aside aria-label="Author preview warnings" className="preview-warnings" role="alert">
        <h2>Author warnings</h2>
        <ul>{preview.author_issues.map((issue) => <li key={`${issue.code}-${issue.field_path}`}><strong>{issue.severity}:</strong> {issue.message} <code>{issue.field_path}</code></li>)}</ul>
      </aside>}
      <article className="learner-preview-frame" data-testid="preview-frame" data-viewport={viewport}>
        <header>
          <p>{code(learner.stage)} · {code(learner.difficulty)}</p>
          <h2>{localized(learner.title) || 'Untitled problem'}</h2>
          <p>{localized(learner.summary)}</p>
        </header>
        {objectives.length > 0 && <section aria-labelledby="preview-objectives"><h3 id="preview-objectives">Learning objectives</h3><ul>{objectives.map((item, index) => <li key={index}>{localized(item)}</li>)}</ul></section>}
        <section aria-labelledby="preview-problem"><h3 id="preview-problem">Problem</h3>{blocks.length === 0 ? <p>No learner content blocks yet.</p> : blocks.map((item, index) => <div key={index}>{localized(typeof item === 'object' && item !== null ? (item as Record<string, unknown>).content : null)}</div>)}</section>
        <section aria-labelledby="preview-answer"><h3 id="preview-answer">Your answer</h3><p>Response type: {code(learner.task_type) || 'Not configured'}</p><button type="button">Submit answer</button></section>
        <nav aria-label="Preview learner navigation" className="preview-navigation">
          <button aria-disabled="true" disabled type="button">Open public problem</button>
          <button aria-disabled="true" disabled type="button">Continue to next problem</button>
        </nav>
      </article>
    </>}
  </section>;
}
