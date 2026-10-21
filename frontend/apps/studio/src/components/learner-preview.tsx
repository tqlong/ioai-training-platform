'use client';

import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

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
  const [warningsCollapsed, setWarningsCollapsed] = useState(false);
  const [portalTarget, setPortalTarget] = useState<HTMLElement | null>(null);
  const requested = useRef(false);

  useEffect(() => {
    setPortalTarget(document.getElementById('studio-header-actions'));
  }, []);

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
  const authorIssues = preview?.author_issues ?? [];
  const errorCount = authorIssues.filter((i) => i.severity === 'ERROR').length;
  const warningCount = authorIssues.filter((i) => i.severity === 'WARNING').length;

  const groupedIssues = authorIssues.reduce((acc, issue) => {
    const key = `${issue.code}:::${issue.message}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(issue);
    return acc;
  }, {} as Record<string, typeof authorIssues>);

  const widthControls = (
    <div aria-label="Preview width" className="preview-width-controls" role="group">
      <button aria-pressed={viewport === 'desktop'} onClick={() => setViewport('desktop')} type="button">Desktop width</button>
      <button aria-pressed={viewport === 'mobile'} onClick={() => setViewport('mobile')} type="button">Mobile width</button>
    </div>
  );

  return <section aria-labelledby="preview-page-heading" className="preview-page">
    <div className="draft-preview-banner" role="note">
      <span className="draft-preview-banner-text">Draft preview - not public</span>
      {!portalTarget && widthControls}
    </div>
    {portalTarget && createPortal(widthControls, portalTarget)}
    <h1 className="sr-only" id="preview-page-heading">Learner-format preview</h1>
    {failed && <p role="alert">Preview could not be loaded for this author revision.</p>}
    {!preview && !failed && <p role="status">Loading preview…</p>}
    {preview && (
      <div className="preview-viewport-group" data-viewport={viewport}>
        {authorIssues.length > 0 && (
          <aside aria-label="Author preview warnings" className="preview-warnings" role="alert">
            <div className="preview-warnings-header">
              <div className="preview-warnings-heading">
                <h2>
                  <span>Author warnings</span>{' '}
                  <span className="tab-badge error" data-testid="preview-badge-error">✖ {errorCount}</span>{' '}
                  <span className="tab-badge warning" data-testid="preview-badge-warning">⚠ {warningCount}</span>
                </h2>
              </div>
              <button
                aria-controls="preview-warnings-content"
                aria-expanded={!warningsCollapsed}
                className="preview-warnings-toggle"
                onClick={() => setWarningsCollapsed((prev) => !prev)}
                type="button"
              >
                {warningsCollapsed ? 'Expand' : 'Collapse'}
              </button>
            </div>
            {!warningsCollapsed && (
              <div className="preview-warnings-body validation-issue-group" id="preview-warnings-content">
                <ul>
                  {Object.entries(groupedIssues).map(([key, group]) => {
                    const firstItem = group[0];
                    const isError = firstItem.severity === 'ERROR';

                    if (group.length === 1) {
                      const issue = firstItem;
                      return (
                        <li data-severity={issue.severity} key={`${issue.code}-${issue.field_path}`}>
                          <span aria-hidden="true" className="severity-icon">{isError ? '✖' : '⚠'}</span>{' '}
                          <span className="severity-label">{isError ? 'Error:' : 'Warning:'}</span>{' '}
                          <span>{issue.message}</span>{' '}
                          <span className="validation-path">({issue.field_path})</span>
                        </li>
                      );
                    }

                    return (
                      <li className="validation-issue-aggregated" data-severity={firstItem.severity} key={key}>
                        <details className="validation-aggregated-details" open>
                          <summary className="validation-aggregated-summary">
                            <span aria-hidden="true" className="severity-icon">{isError ? '✖' : '⚠'}</span>{' '}
                            <span className="severity-label">{isError ? 'Error:' : 'Warning:'}</span>{' '}
                            <span className="aggregated-message">{firstItem.message}</span>{' '}
                            <span className="aggregated-count">({group.length} fields)</span>
                          </summary>
                          <ul className="aggregated-paths-list">
                            {group.map((item) => (
                              <li key={item.field_path}>
                                <span className="validation-path">({item.field_path})</span>
                              </li>
                            ))}
                          </ul>
                        </details>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
          </aside>
        )}
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
      </div>
    )}
  </section>;
}
