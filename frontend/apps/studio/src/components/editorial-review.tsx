'use client';

import { useEffect, useRef, useState } from 'react';

import {
  ApiError,
  type AuthorDraft,
  type EditorialAction,
  type EditorialCommandRequest,
  type EditorialHistory,
  type PublicationResult,
  type PublishRevisionRequest,
} from '@ioai/api-client';

import { studioApi } from '../api';

type Transition = (
  revisionId: string,
  action: EditorialAction,
  request: EditorialCommandRequest,
) => Promise<AuthorDraft>;
type Publish = (revisionId: string, request: PublishRevisionRequest) => Promise<PublicationResult>;

const statusLabel = (status: string) => status
  .toLowerCase()
  .replaceAll('_', ' ')
  .replace(/^./, (value) => value.toUpperCase());

const actionsFor = (status: string): Array<{ action: EditorialAction; label: string }> => {
  if (status === 'DRAFT') return [{ action: 'submit-review', label: 'Submit for review' }];
  if (status === 'IN_REVIEW') return [
    { action: 'request-changes', label: 'Request changes' },
    { action: 'approve', label: 'Approve' },
  ];
  return [];
};

export function EditorialReviewWorkspace({
  draft,
  dirty = false,
  onDraftChange,
  transition = studioApi.transitionAuthorRevision,
  loadHistory = studioApi.getEditorialHistory,
  publish = studioApi.publishAuthorRevision,
}: {
  draft: AuthorDraft;
  dirty?: boolean;
  onDraftChange: (draft: AuthorDraft) => void;
  transition?: Transition;
  loadHistory?: (revisionId: string) => Promise<EditorialHistory>;
  publish?: Publish;
}) {
  const [history, setHistory] = useState<EditorialHistory | null>(null);
  const [note, setNote] = useState('');
  const [pending, setPending] = useState<EditorialAction | null>(null);
  const [error, setError] = useState('');
  const noteRef = useRef<HTMLTextAreaElement>(null);
  const publishTriggerRef = useRef<HTMLButtonElement>(null);
  const publishDialogRef = useRef<HTMLDivElement>(null);
  const publishNoteRef = useRef<HTMLTextAreaElement>(null);
  const [publishOpen, setPublishOpen] = useState(false);
  const [publishNote, setPublishNote] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [publication, setPublication] = useState<PublicationResult | null>(null);
  const [publishKey, setPublishKey] = useState('');

  const refreshHistory = async () => {
    try {
      setHistory(await loadHistory(draft.revision_id));
    } catch {
      setHistory(null);
    }
  };
  useEffect(() => { void refreshHistory(); }, [draft.revision_id]);

  const decide = async (action: EditorialAction) => {
    setPending(action);
    setError('');
    try {
      const updated = await transition(draft.revision_id, action, {
        expected_version: draft.version,
        note,
        actor_context: action === 'submit-review' ? 'local-author' : 'local-reviewer',
        operation_id: globalThis.crypto?.randomUUID?.() ?? `${action}-${draft.version}`,
      });
      setNote('');
      onDraftChange(updated);
      void refreshHistory();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'The editorial decision could not be saved.');
      window.setTimeout(() => noteRef.current?.focus(), 0);
    } finally {
      setPending(null);
    }
  };

  const actions = actionsFor(draft.editorial_status);
  const closePublish = () => {
    if (publishing) return;
    setPublishOpen(false);
    publishTriggerRef.current?.focus();
  };
  const openPublish = () => {
    setPublishKey(globalThis.crypto?.randomUUID?.() ?? `publish-${draft.version}`);
    setPublishOpen(true);
  };
  const confirmPublish = async () => {
    setPublishing(true);
    setError('');
    try {
      const result = await publish(draft.revision_id, {
        expected_version: draft.version,
        note: publishNote,
        actor_context: 'local-reviewer',
        idempotency_key: publishKey,
      });
      setPublication(result);
      setPublishOpen(false);
      setPublishNote('');
      onDraftChange({ ...draft, version: draft.version + 1, editorial_status: 'PUBLISHED' });
      await refreshHistory();
      window.setTimeout(() => publishTriggerRef.current?.focus(), 0);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Publication could not be completed.');
      window.setTimeout(() => publishNoteRef.current?.focus(), 0);
    } finally {
      setPublishing(false);
    }
  };

  useEffect(() => {
    if (!publishOpen) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    publishNoteRef.current?.focus();

    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (!publishing) {
          event.preventDefault();
          closePublish();
        }
        return;
      }
      if (event.key !== 'Tab') return;
      const dialog = publishDialogRef.current;
      if (!dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>('textarea:not([disabled]), button:not([disabled])'));
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey) {
        if (document.activeElement === first || !dialog.contains(document.activeElement)) {
          event.preventDefault();
          last?.focus();
        }
      } else {
        if (document.activeElement === last || !dialog.contains(document.activeElement)) {
          event.preventDefault();
          first?.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [publishOpen, publishing]);

  return (
    <section aria-labelledby="review-publish-heading" className="editor-section editorial-review editorial-review-section" id="review-publish">
      <div className="section-panel-header">
        <h2 id="review-publish-heading">Review &amp; publish</h2>
        <p className="section-panel-desc">
          Inspect editorial workflow status, provide transition notes, and publish the approved problem.
        </p>
      </div>

      <div className="editorial-status-card">
        <div className="editorial-status-info">
          <span className="editorial-status-label">Editorial status:</span>
          <strong className="editorial-status meta-status-tag" data-status={draft.editorial_status.toLowerCase()}>
            {statusLabel(draft.editorial_status)}
          </strong>
        </div>
        <p className="editorial-status-hint">
          {draft.editorial_status === 'DRAFT' && 'Draft revision is editable. Complete all required fields and resolve validation errors before submitting for review.'}
          {draft.editorial_status === 'IN_REVIEW' && 'Revision is under review. Reviewers can request changes or approve for publication.'}
          {draft.editorial_status === 'CHANGES_REQUESTED' && 'Reviewer requested changes before approval. Address feedback to resubmit.'}
          {draft.editorial_status === 'APPROVED' && 'Revision is approved and ready for public snapshot release.'}
          {draft.editorial_status === 'PUBLISHED' && 'This snapshot is published at the permanent URL and visible to learners.'}
          {draft.editorial_status === 'ARCHIVED' && 'This problem is archived and no longer public.'}
        </p>
      </div>

      {(() => {
        const latestChangeRequest = history?.items.slice().reverse().find((item) => item.target_status === 'CHANGES_REQUESTED');
        if (latestChangeRequest) {
          return (
            <div aria-label="Reviewer change requests" className="reviewer-note-callout" role="region">
              <div className="reviewer-note-header">
                <h3 className="reviewer-note-title">Reviewer requests</h3>
                <span className="reviewer-note-meta">
                  {latestChangeRequest.actor_context} · <time dateTime={latestChangeRequest.occurred_at}>{new Date(latestChangeRequest.occurred_at).toLocaleString()}</time>
                </span>
              </div>
              <p className="reviewer-note-text">{latestChangeRequest.note}</p>
            </div>
          );
        }
        return null;
      })()}

      {dirty && (
        <p className="editorial-dirty-warning" role="status">
          Save current changes before an editorial decision.
        </p>
      )}

      {actions.length > 0 && (
        <div className="editor-field editorial-decision-field">
          <div className="field-label-row">
            <label htmlFor="editorial-note">Editorial note</label>
            <span aria-hidden="true" className="required-star"> *</span>
          </div>
          <textarea
            className="editorial-note-textarea"
            disabled={pending !== null}
            id="editorial-note"
            maxLength={2000}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Enter a note explaining this transition decision (required)..."
            ref={noteRef}
            required
            rows={3}
            value={note}
          />
          <p className="field-hint">
            Every status transition requires a descriptive note recorded in the permanent editorial audit trail.
          </p>
          <div className="editorial-actions">
            {actions.map(({ action, label }) => (
              <button
                className={`editorial-action-btn ${action === 'approve' || action === 'submit-review' ? 'primary' : 'secondary'}`}
                disabled={dirty || !note.trim() || pending !== null}
                key={action}
                onClick={() => { void decide(action); }}
                type="button"
              >
                {pending === action ? `${label}…` : label}
              </button>
            ))}
          </div>
        </div>
      )}

      {draft.editorial_status === 'APPROVED' && (
        <div className="editorial-publish-banner">
          <div className="editorial-publish-text">
            <strong className="publish-ready-title">Approved for publication</strong>
            <p className="publish-ready-desc">Approved. Publication remains a separate confirmed action.</p>
          </div>
          <button
            className="editorial-action-btn editorial-publish-btn primary"
            disabled={dirty}
            onClick={openPublish}
            ref={publishTriggerRef}
            type="button"
          >
            Publish
          </button>
        </div>
      )}

      {publication && (
        <p className="editorial-published-alert" role="status">
          Published at <a className="published-link" href={publication.public_url}>{publication.public_url}</a>.
        </p>
      )}

      {error && <p className="editorial-error-alert" role="alert">{error}</p>}

      {publishOpen && (
        <>
          <div className="modal-backdrop" data-testid="modal-backdrop" onClick={closePublish} />
          <div
            aria-labelledby="publish-dialog-title"
            aria-modal="true"
            className="modal-dialog publish-modal"
            ref={publishDialogRef}
            role="dialog"
          >
            <div className="modal-header">
              <h3 id="publish-dialog-title" className="modal-title">Publish approved revision</h3>
              <p className="modal-subtitle">
                This makes the approved snapshot externally visible at the permanent URL:
              </p>
              <div className="publish-url-box">
                <code>/problems/{draft.slug}</code>
              </div>
              <p className="modal-notice">This is different from Draft preview, which is never public.</p>
            </div>

            <div className="editor-field modal-field">
              <div className="field-label-row">
                <label htmlFor="publish-note">Publication note</label>
                <span aria-hidden="true" className="required-star"> *</span>
              </div>
              <textarea
                id="publish-note"
                maxLength={2000}
                onChange={(event) => setPublishNote(event.target.value)}
                placeholder="Enter release note or summary for this publication..."
                ref={publishNoteRef}
                rows={3}
                value={publishNote}
              />
            </div>

            <div className="modal-actions">
              <button
                className="modal-btn confirm primary"
                disabled={!publishNote.trim() || publishing}
                onClick={() => { void confirmPublish(); }}
                type="button"
              >
                {publishing ? 'Publishing…' : 'Confirm publish'}
              </button>
              <button
                className="modal-btn cancel secondary"
                disabled={publishing}
                onClick={closePublish}
                type="button"
              >
                Cancel
              </button>
            </div>
          </div>
        </>
      )}

      <section aria-labelledby="editorial-history-heading" className="editorial-history-wrap">
        <div className="history-section-header">
          <h3 id="editorial-history-heading">Editorial history</h3>
          {history && (
            <span className="history-count">
              {history.items.length} {history.items.length === 1 ? 'record' : 'records'}
            </span>
          )}
        </div>
        {history === null ? (
          <p className="history-empty">History is unavailable.</p>
        ) : history.items.length === 0 ? (
          <p className="history-empty">No editorial decisions yet.</p>
        ) : (
          <ol className="editorial-history-list">
            {history.items.map((item) => (
              <li className="editorial-history-item" key={item.operation_id}>
                <div className="history-item-top">
                  <strong className="history-transition-badge">
                    {statusLabel(item.source_status)} → {statusLabel(item.target_status)}
                  </strong>
                  <span className="history-item-meta">
                    {item.actor_context} · <time dateTime={item.occurred_at}>{new Date(item.occurred_at).toLocaleString()}</time>
                  </span>
                </div>
                <p className="history-item-note">{item.note}</p>
              </li>
            ))}
          </ol>
        )}
      </section>
    </section>
  );
}
