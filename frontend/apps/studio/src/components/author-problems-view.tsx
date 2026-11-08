'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';

import type { ArchiveProblemRequest, ArchiveProblemResult, AuthorDraft, AuthorDraftList, StartRevisionRequest } from '@ioai/api-client';
import { ApiError } from '@ioai/api-client';

import { studioApi } from '../api';
import { RevisionHistoryModal } from './revision-history-modal';

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
  const [archived, setArchived] = useState<Map<string, number>>(new Map());
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [activeHistoryProblemId, setActiveHistoryProblemId] = useState<string | null>(null);
  const [archiveTarget, setArchiveTarget] = useState<AuthorDraftList['items'][number] | null>(null);
  const [archiveNote, setArchiveNote] = useState('');
  const [archiving, setArchiving] = useState(false);
  const archiveTrigger = useRef<HTMLElement | null>(null);
  const archiveNoteInput = useRef<HTMLTextAreaElement>(null);
  const archiveDialogRef = useRef<HTMLDivElement>(null);
  const historyDrawerRef = useRef<HTMLElement | null>(null);
  const historyTriggerRef = useRef<HTMLElement | null>(null);

  const items = useMemo(() => result.items.map((item) => {
    const archivedVersion = archived.get(item.revision_id);
    return archivedVersion === undefined
      ? item
      : { ...item, editorial_status: 'ARCHIVED', version: archivedVersion };
  }), [archived, result.items]);

  const groups = useMemo(() => {
    const byProblem = new Map<string, typeof items>();
    items.forEach((item) => {
      const revisions = byProblem.get(item.problem_id) ?? [];
      revisions.push(item);
      byProblem.set(item.problem_id, revisions);
    });
    return Array.from(byProblem, ([problemId, revisions]) => ({
      problemId,
      revisions: revisions.sort((left, right) => (
        Date.parse(right.last_saved_at) - Date.parse(left.last_saved_at)
        || right.revision_id.localeCompare(left.revision_id)
      )),
    })).sort((left, right) => (
      Date.parse(right.revisions[0]!.last_saved_at) - Date.parse(left.revisions[0]!.last_saved_at)
      || left.problemId.localeCompare(right.problemId)
    ));
  }, [items]);

  const filtered = useMemo(() => groups.filter((group) => {
    const needle = search.trim().toLocaleLowerCase();
    const latest = group.revisions[0]!;
    const titleText = getLocalizedText(latest.title).toLowerCase();
    const slugText = (latest.slug ?? '').toLowerCase();
    const matchesSearch = !needle || group.problemId.toLocaleLowerCase().includes(needle)
      || group.revisions.some((revision) => revision.revision_id.toLocaleLowerCase().includes(needle))
      || titleText.includes(needle)
      || slugText.includes(needle);
    return matchesSearch && (status === 'ALL' || latest.editorial_status === status);
  }), [groups, search, status]);

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
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : 'A new draft revision could not be started. Reload the list and try again.');
    } finally {
      setStarting(null);
    }
  };

  const openHistoryDrawer = (problemId: string, triggerEl?: HTMLElement | null) => {
    if (triggerEl) historyTriggerRef.current = triggerEl;
    setActiveHistoryProblemId(problemId);
  };

  const closeHistoryDrawer = () => {
    setActiveHistoryProblemId(null);
    historyTriggerRef.current?.focus();
  };

  const closeArchive = () => {
    if (archiving) return;
    setArchiveTarget(null); setArchiveNote('');
    archiveTrigger.current?.focus();
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
      setArchived((current) => new Map(current).set(
        archiveTarget.revision_id,
        archiveTarget.version + 1,
      ));
      setArchiveTarget(null); setArchiveNote('');
      archiveTrigger.current?.focus();
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : 'The published problem could not be archived. Reload and try again.');
      window.setTimeout(() => archiveNoteInput.current?.focus(), 0);
    } finally { setArchiving(false); }
  };

  // Close 3-dot dropdown menu on click outside or Escape
  useEffect(() => {
    if (!openMenuId) return;
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.row-actions-menu-container')) {
        setOpenMenuId(null);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpenMenuId(null);
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [openMenuId]);

  // Handle Focus Trap, Escape and body scroll for History Drawer
  useEffect(() => {
    if (!activeHistoryProblemId) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const focusableSelector = 'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const focusTimer = window.setTimeout(() => {
      const drawer = historyDrawerRef.current;
      if (drawer) {
        const firstFocusable = drawer.querySelector<HTMLElement>(focusableSelector);
        firstFocusable?.focus();
      }
    }, 0);

    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeHistoryDrawer();
        return;
      }
      if (event.key !== 'Tab') return;

      const drawer = historyDrawerRef.current;
      if (!drawer) return;
      const focusable = Array.from(drawer.querySelectorAll<HTMLElement>(focusableSelector));
      if (focusable.length === 0) return;
      const first = focusable[0]!;
      const last = focusable[focusable.length - 1]!;

      if (event.shiftKey) {
        if (document.activeElement === first || !drawer.contains(document.activeElement)) {
          event.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last || !drawer.contains(document.activeElement)) {
          event.preventDefault();
          first.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [activeHistoryProblemId]);

  // Handle Archive Modal keyboard & focus trap
  useEffect(() => {
    if (!archiveTarget) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    archiveNoteInput.current?.focus();

    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (!archiving) {
          event.preventDefault();
          closeArchive();
        }
        return;
      }
      if (event.key !== 'Tab') return;
      const dialog = archiveDialogRef.current;
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
  }, [archiveTarget, archiving]);

  const activeHistoryGroup = useMemo(
    () => groups.find((g) => g.problemId === activeHistoryProblemId) ?? null,
    [groups, activeHistoryProblemId],
  );

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

      <div className="author-filter-bar">
        <label className="author-filter-field search-field">
          <span>Search author problems</span>
          <input
            name="search"
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search problem or revision ID"
            type="search"
            value={search}
          />
        </label>

        <div className="author-filter-field status-field">
          <span id="status-tabs-label">Editorial status</span>
          <div aria-labelledby="status-tabs-label" className="status-tabs" role="group">
            <button aria-pressed={status === 'ALL'} onClick={() => setStatusFilter('ALL')} type="button">All ({groups.length})</button>
            <button aria-pressed={status === 'DRAFT'} onClick={() => setStatusFilter('DRAFT')} type="button">Draft</button>
            <button aria-pressed={status === 'IN_REVIEW'} onClick={() => setStatusFilter('IN_REVIEW')} type="button">In review</button>
            <button aria-pressed={status === 'PUBLISHED'} onClick={() => setStatusFilter('PUBLISHED')} type="button">Published</button>
            <button aria-pressed={status === 'CHANGES_REQUESTED'} onClick={() => setStatusFilter('CHANGES_REQUESTED')} type="button">Changes requested</button>
          </div>
        </div>

        <label className="author-filter-field status-select-field">
          <span>Editorial status</span>
          <select name="status" onChange={(event) => setStatusFilter(event.target.value)} value={status}>
            <option value="ALL">All statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="IN_REVIEW">In review</option>
            <option value="PUBLISHED">Published</option>
            <option value="CHANGES_REQUESTED">Changes requested</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </label>

        {(search.trim() !== '' || status !== 'ALL') && (
          <button
            className="author-filter-clear-btn"
            onClick={() => { setSearch(''); setStatusFilter('ALL'); }}
            type="button"
          >
            Clear filters
          </button>
        )}
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
                <th scope="col">Status</th>
                <th scope="col">Problem</th>
                <th scope="col">Identities</th>
                <th scope="col">Validation</th>
                <th scope="col">Updated</th>
                <th scope="col" className="col-actions"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            {filtered.map((group) => {
              const latest = group.revisions[0]!;
              const title = getLocalizedText(latest.title) || `Problem #${formatShortId(latest.problem_id)}`;
              const slug = latest.slug ?? '';
              const summary = getLocalizedText(latest.summary);
              return (
                <tbody key={group.problemId}>
                  <tr key={latest.revision_id}>
                    <td>
                      <span className="card-col-label">Status</span>
                      <span className="status-label" data-status={latest.editorial_status.toLowerCase()}>{formatStatus(latest.editorial_status)}</span>
                    </td>
                    <td>
                      <span className="card-col-label">Problem</span>
                      <div className="problem-cell">
                        <Link
                          className="problem-title-link"
                          href={latest.editorial_status === 'DRAFT'
                            ? `/author/problems/${latest.problem_id}`
                            : `/author/problems/${latest.problem_id}?revision=${latest.revision_id}`}
                        >
                          {title}
                        </Link>
                        {slug ? (
                          <span className="problem-slug-text">{slug}</span>
                        ) : (
                          <span className="problem-slug-text placeholder">no-slug-set</span>
                        )}
                        {summary && (
                          <span className="problem-summary-text" title={summary}>
                            {summary}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="card-col-label">Identities</span>
                      <div className="identities-group">
                        <div className="id-badge">
                          <span className="id-badge-label">PID:</span>
                          <code title={latest.problem_id}>{formatShortId(latest.problem_id)}</code>
                          <span className="sr-only">{latest.problem_id}</span>
                          <CopyButton label="Copy problem ID" text={latest.problem_id} />
                        </div>
                        <div className="id-badge revision-sub-badge">
                          <span className="id-badge-label">REV:</span>
                          <code title={latest.revision_id}>{formatShortId(latest.revision_id)}</code>
                          <span className="sr-only">{latest.revision_id}</span>
                          <CopyButton label="Copy revision ID" text={latest.revision_id} />
                          {group.revisions.length > 1 ? (
                            <button
                              aria-haspopup="dialog"
                              className="version-chip version-chip-btn"
                              onClick={(e) => openHistoryDrawer(group.problemId, e.currentTarget)}
                              title="View revision history"
                              type="button"
                            >
                              v{latest.version} ({group.revisions.length} revs)
                            </button>
                          ) : (
                            <span className="version-chip">v{latest.version}</span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="card-col-label">Validation</span>
                      {formatValidation(latest.validation_summary)}
                    </td>
                    <td>
                      <span className="card-col-label">Last saved</span>
                      <time
                        className="updated-time"
                        dateTime={latest.last_saved_at}
                        title={formatExactDateTime(latest.last_saved_at)}
                      >
                        {formatRelativeTime(latest.last_saved_at)}
                      </time>
                    </td>
                    <td className="col-actions-cell">
                      <span className="card-col-label">Actions</span>
                      <div className="row-actions">
                        <Link
                          className="action-btn-preview"
                          href={`/author/problems/${latest.problem_id}/preview`}
                          title="Preview as learner"
                        >
                          Preview
                        </Link>

                        <div className="row-actions-menu-container">
                          <button
                            aria-expanded={openMenuId === latest.revision_id}
                            aria-haspopup="menu"
                            aria-label="More actions"
                            className="action-menu-trigger-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(openMenuId === latest.revision_id ? null : latest.revision_id);
                            }}
                            title="More actions"
                            type="button"
                          >
                            •••
                          </button>

                          {openMenuId === latest.revision_id && (
                            <div aria-label="Problem actions" className="action-dropdown-menu" role="menu">
                              {latest.editorial_status === 'DRAFT' ? (
                                <Link
                                  className="action-menu-item"
                                  href={`/author/problems/${latest.problem_id}`}
                                  onClick={() => setOpenMenuId(null)}
                                  role="menuitem"
                                >
                                  Resume editing
                                </Link>
                              ) : (
                                <Link
                                  className="action-menu-item"
                                  href={`/author/problems/${latest.problem_id}?revision=${latest.revision_id}`}
                                  onClick={() => setOpenMenuId(null)}
                                  role="menuitem"
                                >
                                  View problem
                                </Link>
                              )}

                              {['PUBLISHED', 'ARCHIVED', 'CHANGES_REQUESTED'].includes(latest.editorial_status) && (
                                <button
                                  className="action-menu-item"
                                  disabled={starting !== null}
                                  onClick={() => {
                                    setOpenMenuId(null);
                                    void beginRevision(latest);
                                  }}
                                  role="menuitem"
                                  type="button"
                                >
                                  {starting === latest.revision_id
                                    ? 'Starting draft…'
                                    : latest.editorial_status === 'PUBLISHED'
                                    ? 'Edit as new draft'
                                    : latest.editorial_status === 'ARCHIVED'
                                    ? 'Create new draft'
                                    : 'Address changes'}
                                </button>
                              )}

                              {group.revisions.length > 1 && (
                                <button
                                  className="action-menu-item"
                                  onClick={(e) => {
                                    setOpenMenuId(null);
                                    openHistoryDrawer(group.problemId, e.currentTarget);
                                  }}
                                  role="menuitem"
                                  type="button"
                                >
                                  Show all {group.revisions.length} revisions
                                </button>
                              )}

                              {latest.editorial_status === 'PUBLISHED' && (
                                <button
                                  className="action-menu-item action-menu-danger"
                                  onClick={(event) => {
                                    archiveTrigger.current = event.currentTarget;
                                    setArchiveTarget(latest);
                                    setOpenMenuId(null);
                                  }}
                                  role="menuitem"
                                  type="button"
                                >
                                  Archive
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              );
            })}
          </table>
        </div>
      )}

      {/* Revision History Popup Modal */}
      {activeHistoryGroup && (
        <RevisionHistoryModal
          isOpen={Boolean(activeHistoryGroup)}
          onClose={closeHistoryDrawer}
          problemId={activeHistoryGroup.problemId}
          revisions={activeHistoryGroup.revisions}
          triggerRef={historyTriggerRef}
        />
      )}

      {/* Archive Problem Modal Dialog */}
      {archiveTarget && <>
        <div className="modal-backdrop" data-testid="archive-backdrop" onClick={closeArchive} />
        <div
          aria-labelledby="archive-dialog-title"
          aria-modal="true"
          className="modal-dialog"
          ref={archiveDialogRef}
          role="dialog"
        >
          <h2 id="archive-dialog-title">Archive published problem</h2>
          <p>This removes <code>/problems/{archiveTarget.problem_id}</code> from public eligibility. Historical snapshots remain auditable.</p>
          <label htmlFor="archive-note">Archive note</label>
          <textarea id="archive-note" maxLength={2000} onChange={(event) => setArchiveNote(event.target.value)} ref={archiveNoteInput} value={archiveNote} />
          <div className="editorial-actions"><button disabled={!archiveNote.trim() || archiving} onClick={() => { void confirmArchive(); }} type="button">{archiving ? 'Archiving…' : 'Confirm archive'}</button><button disabled={archiving} onClick={closeArchive} type="button">Cancel</button></div>
        </div>
      </>}
    </section>
  );
}

const formatStatus = (status: string) => status.toLowerCase().replaceAll('_', ' ');

const getLocalizedText = (value: unknown): string => {
  if (typeof value === 'string') return value;
  if (typeof value === 'object' && value !== null) {
    const record = value as Record<string, unknown>;
    if (typeof record.en === 'string' && record.en.trim()) return record.en.trim();
    if (typeof record.vi === 'string' && record.vi.trim()) return record.vi.trim();
  }
  return '';
};

const formatDate = (value: string) => new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'UTC',
}).format(new Date(value));

const formatRelativeTime = (value: string) => {
  const date = new Date(value);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (Number.isNaN(diffInSeconds) || diffInSeconds < 0) return formatDate(value);
  if (diffInSeconds < 60) return 'Just now';
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) return `${diffInDays}d ago`;
  return formatDate(value);
};

const formatExactDateTime = (value: string) => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short',
    }).format(new Date(value));
  } catch {
    return value;
  }
};

const formatValidation = (summary: Record<string, unknown> | null) => {
  if (!summary) return 'Not validated';
  if (summary.publication_eligible === true) return 'Eligible';
  return `${String(summary.error_count ?? 0)} blockers`;
};

const formatShortId = (id: string) => {
  if (id.includes('-')) {
    const firstSegment = id.split('-')[0];
    if (firstSegment && firstSegment.length >= 6) {
      return firstSegment;
    }
  }
  return id.length > 8 ? id.slice(0, 8) : id;
};

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard) {
        await navigator.clipboard.writeText(text);
      }
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // fallback
    }
  };

  return (
    <button
      aria-label={copied ? 'Copied' : label}
      className={`copy-btn ${copied ? 'copied' : ''}`}
      onClick={copy}
      title={copied ? 'Copied!' : label}
      type="button"
    >
      {copied ? (
        <svg aria-hidden="true" fill="none" height="12" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" viewBox="0 0 24 24" width="12">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : (
        <svg aria-hidden="true" fill="none" height="12" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="12">
          <rect height="13" rx="2" ry="2" width="13" x="9" y="9" />
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      )}
    </button>
  );
}
