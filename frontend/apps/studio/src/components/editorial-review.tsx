'use client';

import { useEffect, useRef, useState } from 'react';
import type { KeyboardEvent } from 'react';

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
    window.setTimeout(() => publishTriggerRef.current?.focus(), 0);
  };
  const openPublish = () => {
    setPublishKey(globalThis.crypto?.randomUUID?.() ?? `publish-${draft.version}`);
    setPublishOpen(true);
    window.setTimeout(() => publishNoteRef.current?.focus(), 0);
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
  const trapPublishKeys = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      closePublish();
      return;
    }
    if (event.key !== 'Tab') return;
    const focusable = Array.from(publishDialogRef.current?.querySelectorAll<HTMLElement>('textarea, button:not([disabled])') ?? []);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault(); last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first?.focus();
    }
  };
  return <section aria-labelledby="review-publish-heading" className="editorial-review" id="review-publish">
    <h2 id="review-publish-heading">Review &amp; publish</h2>
    <p>Editorial status: <strong className="editorial-status">{statusLabel(draft.editorial_status)}</strong></p>
    {dirty && <p role="status">Save current changes before an editorial decision.</p>}
    {actions.length > 0 && <div className="editorial-decision">
      <label htmlFor="editorial-note">Editorial note</label>
      <textarea
        disabled={pending !== null}
        id="editorial-note"
        maxLength={2000}
        onChange={(event) => setNote(event.target.value)}
        ref={noteRef}
        required
        value={note}
      />
      <div className="editorial-actions">
        {actions.map(({ action, label }) => <button
          disabled={dirty || !note.trim() || pending !== null}
          key={action}
          onClick={() => { void decide(action); }}
          type="button"
        >{pending === action ? `${label}…` : label}</button>)}
      </div>
    </div>}
    {draft.editorial_status === 'APPROVED' && <div>
      <p>Approved. Publication remains a separate confirmed action.</p>
      <button disabled={dirty} onClick={openPublish} ref={publishTriggerRef} type="button">Publish</button>
    </div>}
    {publication && <p role="status">Published at <a href={publication.public_url}>{publication.public_url}</a>.</p>}
    {error && <p role="alert">{error}</p>}
    {publishOpen && <div
      aria-labelledby="publish-dialog-title"
      aria-modal="true"
      className="modal-dialog"
      onKeyDown={trapPublishKeys}
      ref={publishDialogRef}
      role="dialog"
    >
      <h3 id="publish-dialog-title">Publish approved revision</h3>
      <p>This makes the approved snapshot externally visible at the permanent URL:</p>
      <p><code>/problems/{draft.slug}</code></p>
      <p>This is different from Draft preview, which is never public.</p>
      <label htmlFor="publish-note">Publication note</label>
      <textarea id="publish-note" maxLength={2000} onChange={(event) => setPublishNote(event.target.value)} ref={publishNoteRef} value={publishNote} />
      <div className="editorial-actions">
        <button disabled={!publishNote.trim() || publishing} onClick={() => { void confirmPublish(); }} type="button">{publishing ? 'Publishing…' : 'Confirm publish'}</button>
        <button disabled={publishing} onClick={closePublish} type="button">Cancel</button>
      </div>
    </div>}
    <section aria-labelledby="editorial-history-heading">
      <h3 id="editorial-history-heading">Editorial history</h3>
      {history === null ? <p>History is unavailable.</p> : history.items.length === 0 ? <p>No editorial decisions yet.</p> : <ol>
        {history.items.map((item) => <li key={item.operation_id}>
          <p><strong>{statusLabel(item.source_status)} → {statusLabel(item.target_status)}</strong></p>
          <p>{item.note}</p>
          <p>{item.actor_context} · <time dateTime={item.occurred_at}>{new Date(item.occurred_at).toLocaleString()}</time></p>
        </li>)}
      </ol>}
    </section>
  </section>;
}
