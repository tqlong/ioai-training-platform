'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

export type RevisionHistoryItem = {
  problem_id: string;
  revision_id: string;
  version: number;
  editorial_status: string;
  last_saved_at: string;
  validation_summary?: unknown;
};

export type RevisionHistoryModalProps = {
  isOpen: boolean;
  onClose: () => void;
  problemId: string;
  revisions: RevisionHistoryItem[];
  currentRevisionId?: string;
  triggerRef?: React.RefObject<HTMLElement | null>;
  loading?: boolean;
  onSelectRevision?: (revision: RevisionHistoryItem) => void;
};

export function RevisionHistoryModal({
  isOpen,
  onClose,
  problemId,
  revisions,
  currentRevisionId,
  triggerRef,
  loading = false,
  onSelectRevision,
}: RevisionHistoryModalProps) {
  const dialogRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const focusableSelector =
      'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const focusTimer = window.setTimeout(() => {
      const dialog = dialogRef.current;
      if (dialog) {
        const firstFocusable = dialog.querySelector<HTMLElement>(focusableSelector);
        firstFocusable?.focus();
      }
    }, 0);

    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== 'Tab') return;

      const dialog = dialogRef.current;
      if (!dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(focusableSelector));
      if (focusable.length === 0) return;
      const first = focusable[0]!;
      const last = focusable[focusable.length - 1]!;

      if (event.shiftKey) {
        if (document.activeElement === first || !dialog.contains(document.activeElement)) {
          event.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last || !dialog.contains(document.activeElement)) {
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
      triggerRef?.current?.focus();
    };
  }, [isOpen, onClose, triggerRef]);

  if (!isOpen) return null;

  return (
    <>
      <div
        className="modal-backdrop"
        data-testid="history-drawer-backdrop"
        onClick={onClose}
      />
      <aside
        aria-labelledby="history-drawer-eyebrow history-drawer-title"
        aria-modal="true"
        className="history-modal history-drawer"
        ref={dialogRef}
        role="dialog"
      >
        <div className="history-modal-header history-drawer-header">
          <div>
            <p className="eyebrow" id="history-drawer-eyebrow">Revision history</p>
            <h2 id="history-drawer-title">Problem #{formatShortId(problemId)}</h2>
          </div>
          <button
            aria-label="Close revision history"
            className="close-modal-btn close-drawer-btn"
            onClick={onClose}
            type="button"
          >
            ✕
          </button>
        </div>
        <div className="history-modal-body history-drawer-body">
          {loading ? (
            <p style={{ textAlign: 'center', color: '#64748b', padding: '2rem 0' }}>
              Loading revisions…
            </p>
          ) : revisions.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#64748b', padding: '2rem 0' }}>
              No revisions found for this problem.
            </p>
          ) : (
            <ol className="history-timeline">
              {revisions.map((rev, revIdx) => (
                <li className="history-timeline-item" key={rev.revision_id}>
                  <div className="history-item-top">
                    <span className="history-version-badge">v{rev.version}</span>
                    <div className="history-badges-group">
                      <span className="status-label" data-status={rev.editorial_status.toLowerCase()}>
                        {formatStatus(rev.editorial_status)}
                      </span>
                      {currentRevisionId && rev.revision_id === currentRevisionId && (
                        <span className="current-viewing-badge">Viewing</span>
                      )}
                      {revIdx === 0 && <span className="current-badge">Latest</span>}
                    </div>
                  </div>
                  <div className="history-item-meta">
                    <span className="id-badge">
                      <code>{formatShortId(rev.revision_id)}</code>
                      <CopyButton label="Copy revision ID" text={rev.revision_id} />
                    </span>
                    <time dateTime={rev.last_saved_at} title={formatExactDateTime(rev.last_saved_at)}>
                      {formatRelativeTime(rev.last_saved_at)}
                    </time>
                    <span className="validation-inline">{formatValidation(rev.validation_summary)}</span>
                  </div>
                  <div className="history-item-actions">
                    {rev.editorial_status === 'DRAFT' ? (
                      <Link
                        className="history-btn primary"
                        href={`/author/problems/${rev.problem_id}`}
                        onClick={(event) => {
                          onClose();
                          if (onSelectRevision) {
                            event.preventDefault();
                            onSelectRevision(rev);
                          }
                        }}
                      >
                        {currentRevisionId && rev.revision_id === currentRevisionId
                          ? 'Current draft'
                          : 'Resume editing'}
                      </Link>
                    ) : (
                      <Link
                        className="history-btn"
                        href={`/author/problems/${rev.problem_id}?revision=${rev.revision_id}`}
                        onClick={(event) => {
                          onClose();
                          if (onSelectRevision) {
                            event.preventDefault();
                            onSelectRevision(rev);
                          }
                        }}
                      >
                        {currentRevisionId && rev.revision_id === currentRevisionId
                          ? 'Viewing snapshot'
                          : 'View snapshot'}
                      </Link>
                    )}
                    <Link
                      className="history-btn"
                      href={`/author/problems/${rev.problem_id}/preview`}
                      onClick={onClose}
                    >
                      Preview as Learner
                    </Link>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </div>
      </aside>
    </>
  );
}

const formatStatus = (status: string) => status.toLowerCase().replaceAll('_', ' ');

const formatDate = (value: string) =>
  new Intl.DateTimeFormat('en', {
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

const formatValidation = (summary: unknown) => {
  if (!summary || typeof summary !== 'object') return 'Not validated';
  const record = summary as Record<string, unknown>;
  if (record.publication_eligible === true) return 'Eligible';
  return `${String(record.error_count ?? 0)} blockers`;
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
