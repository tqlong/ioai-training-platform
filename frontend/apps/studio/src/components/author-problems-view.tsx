'use client';

import { useMemo, useRef, useState } from 'react';
import type { KeyboardEvent } from 'react';
import Link from 'next/link';

import type { ArchiveProblemRequest, ArchiveProblemResult, AuthorDraft, AuthorDraftList, StartRevisionRequest } from '@ioai/api-client';

import { studioApi } from '../api';

export function AuthorProblemsView({
  result,
  startRevision = studioApi.startAuthorRevision,
  onOpen = (problemId: string) => { window.location.assign(`/author/problems/${problemId}`); },
  archiveProblem = studioApi.archiveAuthorProblem,
}: {
  result: AuthorDraftList;
  startRevision?: (problemId: string, request: StartRevisionRequest) => Promise<AuthorDraft>;
  onOpen?: (problemId: string) => void;
  archiveProblem?: (problemId: string, request: ArchiveProblemRequest) => Promise<ArchiveProblemResult>;
}) {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('ALL');
  const [starting, setStarting] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');
  const [archived, setArchived] = useState<Set<string>>(new Set());
  const [archiveTarget, setArchiveTarget] = useState<AuthorDraftList['items'][number] | null>(null);
  const [archiveNote, setArchiveNote] = useState('');
  const [archiving, setArchiving] = useState(false);
  const archiveTrigger = useRef<HTMLButtonElement | null>(null);
  const archiveNoteInput = useRef<HTMLTextAreaElement>(null);
  const items = useMemo(() => result.items.map((item) => archived.has(item.problem_id) ? { ...item, editorial_status: 'ARCHIVED' } : item), [archived, result.items]);
  const filtered = useMemo(() => items.filter((draft) => {
    const needle = search.trim().toLocaleLowerCase();
    const matchesSearch = !needle || draft.problem_id.toLocaleLowerCase().includes(needle) || draft.revision_id.toLocaleLowerCase().includes(needle);
    return matchesSearch && (status === 'ALL' || draft.editorial_status === status);
  }), [items, search, status]);
  const setStatusFilter = (next: string) => setStatus(next);
  const beginRevision = async (item: AuthorDraftList['items'][number]) => {
    setStarting(item.revision_id);
    setActionError('');
    try {
      await startRevision(item.problem_id, {
        source_revision_id: item.revision_id,
        expected_version: item.version,
        operation_id: globalThis.crypto?.randomUUID?.() ?? `revise-${item.version}`,
      });
      onOpen(item.problem_id);
    } catch {
      setActionError('A new draft revision could not be started. Reload the list and try again.');
    } finally {
      setStarting(null);
    }
  };
  const closeArchive = () => {
    if (archiving) return;
    setArchiveTarget(null); setArchiveNote('');
    window.setTimeout(() => archiveTrigger.current?.focus(), 0);
  };
  const confirmArchive = async () => {
    if (!archiveTarget) return;
    setArchiving(true); setActionError('');
    try {
      await archiveProblem(archiveTarget.problem_id, {
        expected_version: archiveTarget.version,
        note: archiveNote,
        actor_context: 'local-reviewer',
        operation_id: globalThis.crypto?.randomUUID?.() ?? `archive-${archiveTarget.version}`,
      });
      setArchived((current) => new Set(current).add(archiveTarget.problem_id));
      setArchiveTarget(null); setArchiveNote('');
    } catch {
      setActionError('The published problem could not be archived. Reload and try again.');
      window.setTimeout(() => archiveNoteInput.current?.focus(), 0);
    } finally { setArchiving(false); }
  };
  const archiveKeys = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') { event.preventDefault(); closeArchive(); }
    if (event.key !== 'Tab') return;
    const focusable = Array.from(event.currentTarget.querySelectorAll<HTMLElement>('textarea, button:not([disabled])'));
    const first = focusable[0]; const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
  };
  return (
    <section aria-labelledby="author-problems-title" className="studio-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Editorial workspace</p>
          <h1 id="author-problems-title">Author problems</h1>
          <p>Create, validate, preview, and prepare structured problems for review.</p>
        </div>
        <Link className="primary-action" href="/author/problems/new">
          Create problem
        </Link>
      </div>

      <div aria-label="Problem status" className="status-tabs" role="group">
        <button aria-pressed={status === 'ALL'} onClick={() => setStatusFilter('ALL')} type="button">All ({result.count})</button>
        <button aria-pressed={status === 'DRAFT'} onClick={() => setStatusFilter('DRAFT')} type="button">Draft</button>
        <button aria-pressed={status === 'IN_REVIEW'} onClick={() => setStatusFilter('IN_REVIEW')} type="button">In review</button>
        <button aria-pressed={status === 'CHANGES_REQUESTED'} onClick={() => setStatusFilter('CHANGES_REQUESTED')} type="button">Changes requested</button>
      </div>

      <div className="list-tools">
        <label>
          <span>Search author problems</span>
          <input name="search" onChange={(event) => setSearch(event.target.value)} placeholder="Search problem or revision ID" type="search" value={search} />
        </label>
        <label>
          <span>Editorial status</span>
          <select name="status" onChange={(event) => setStatusFilter(event.target.value)} value={status}>
            <option value="ALL">All statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="IN_REVIEW">In review</option>
          </select>
        </label>
      </div>
      {actionError && <p role="alert">{actionError}</p>}

      {result.count === 0 ? (
        <div className="empty-state">
          <h2>No author problems yet</h2>
          <p>Start the first structured draft. Nothing is public until publication.</p>
          <Link href="/author/problems/new">Create the first problem</Link>
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state"><h2>No matching author problems</h2><p>Adjust the search or editorial status.</p><button onClick={() => { setSearch(''); setStatusFilter('ALL'); }} type="button">Clear filters</button></div>
      ) : (
        <div className="draft-table-wrap">
          <table>
            <caption className="sr-only">Author problem revisions</caption>
            <thead>
              <tr>
                <th scope="col">Problem</th>
                <th scope="col">Status</th>
                <th scope="col">Revision</th>
                <th scope="col">Last saved</th>
                <th scope="col">Validation</th>
                <th scope="col"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((draft) => (
                <tr key={draft.revision_id}>
                  <td><code>{draft.problem_id}</code></td>
                  <td><span className="status-label">{formatStatus(draft.editorial_status)}</span></td>
                  <td><code>{draft.revision_id}</code> · v{draft.version}</td>
                  <td><time dateTime={draft.last_saved_at}>{formatDate(draft.last_saved_at)}</time></td>
                  <td>{formatValidation(draft.validation_summary)}</td>
                  <td><div className="row-actions">{['PUBLISHED', 'ARCHIVED', 'CHANGES_REQUESTED'].includes(draft.editorial_status)
                    ? <button disabled={starting !== null} onClick={() => { void beginRevision(draft); }} type="button">{starting === draft.revision_id ? 'Starting draft…' : draft.editorial_status === 'PUBLISHED' ? 'Edit as new draft' : draft.editorial_status === 'ARCHIVED' ? 'Create new draft' : 'Address changes'}</button>
                    : <Link href={`/author/problems/${draft.problem_id}`}>Resume editing</Link>}
                    {draft.editorial_status === 'PUBLISHED' && <button onClick={(event) => { archiveTrigger.current = event.currentTarget; setArchiveTarget(draft); window.setTimeout(() => archiveNoteInput.current?.focus(), 0); }} type="button">Archive</button>}</div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {archiveTarget && <div aria-labelledby="archive-dialog-title" aria-modal="true" className="modal-dialog" onKeyDown={archiveKeys} role="dialog">
        <h2 id="archive-dialog-title">Archive published problem</h2>
        <p>This removes <code>/problems/{archiveTarget.problem_id}</code> from public eligibility. Historical snapshots remain auditable.</p>
        <label htmlFor="archive-note">Archive note</label>
        <textarea id="archive-note" maxLength={2000} onChange={(event) => setArchiveNote(event.target.value)} ref={archiveNoteInput} value={archiveNote} />
        <div className="editorial-actions"><button disabled={!archiveNote.trim() || archiving} onClick={() => { void confirmArchive(); }} type="button">{archiving ? 'Archiving…' : 'Confirm archive'}</button><button disabled={archiving} onClick={closeArchive} type="button">Cancel</button></div>
      </div>}
    </section>
  );
}

const formatStatus = (status: string) => status.toLowerCase().replaceAll('_', ' ');
const formatDate = (value: string) => new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'UTC',
}).format(new Date(value));

const formatValidation = (summary: Record<string, unknown> | null) => {
  if (!summary) return 'Not validated';
  if (summary.publication_eligible === true) return 'Eligible';
  return `${String(summary.error_count ?? 0)} blockers`;
};
