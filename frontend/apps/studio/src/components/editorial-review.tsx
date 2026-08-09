'use client';

import { useEffect, useRef, useState } from 'react';

import {
  ApiError,
  type AuthorDraft,
  type EditorialAction,
  type EditorialCommandRequest,
  type EditorialHistory,
} from '@ioai/api-client';

import { studioApi } from '../api';

type Transition = (
  revisionId: string,
  action: EditorialAction,
  request: EditorialCommandRequest,
) => Promise<AuthorDraft>;

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
}: {
  draft: AuthorDraft;
  dirty?: boolean;
  onDraftChange: (draft: AuthorDraft) => void;
  transition?: Transition;
  loadHistory?: (revisionId: string) => Promise<EditorialHistory>;
}) {
  const [history, setHistory] = useState<EditorialHistory | null>(null);
  const [note, setNote] = useState('');
  const [pending, setPending] = useState<EditorialAction | null>(null);
  const [error, setError] = useState('');
  const noteRef = useRef<HTMLTextAreaElement>(null);

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
      await refreshHistory();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'The editorial decision could not be saved.');
      window.setTimeout(() => noteRef.current?.focus(), 0);
    } finally {
      setPending(null);
    }
  };

  const actions = actionsFor(draft.editorial_status);
  return <section aria-labelledby="review-publish-heading" className="editorial-review" id="review-publish">
    <h2 id="review-publish-heading">Review &amp; publish</h2>
    <p>Editorial status: <strong className="editorial-status">{statusLabel(draft.editorial_status)}</strong></p>
    {dirty && <p role="status">Save current changes before an editorial decision.</p>}
    {actions.length > 0 && <div className="editorial-decision">
      <label htmlFor="editorial-note">Editorial note</label>
      <textarea
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
    {draft.editorial_status === 'APPROVED' && <p>Approved. Publication remains a separate confirmed action.</p>}
    {error && <p role="alert">{error}</p>}
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
