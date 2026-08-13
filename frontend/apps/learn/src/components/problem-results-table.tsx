'use client';

import type { PublicProblemList } from '@ioai/api-client';
import Link from 'next/link';
import type { KeyboardEvent, MouseEvent } from 'react';


type ProblemItem = PublicProblemList['items'][number];
export type ProblemProgressDisplay = {
  status: 'NOT_STARTED' | 'ATTEMPTED' | 'COMPLETED';
  evidence?: 'INTRODUCED' | 'PRACTICED' | 'APPLIED' | 'PROFICIENT';
};

type ProblemResultsTableProps = {
  items: ProblemItem[];
  labels: Record<string, string>;
  returnUrl: string;
  progress?: Record<string, ProblemProgressDisplay>;
};

const STATUS_LABELS: Record<ProblemProgressDisplay['status'], string> = {
  NOT_STARTED: 'Not started',
  ATTEMPTED: 'Attempted',
  COMPLETED: 'Completed',
};

const EVIDENCE_LABELS: Record<NonNullable<ProblemProgressDisplay['evidence']>, string> = {
  INTRODUCED: 'Introduced',
  PRACTICED: 'Practiced',
  APPLIED: 'Applied',
  PROFICIENT: 'Proficient',
};

export function ProblemResultsTable({
  items,
  labels,
  returnUrl,
  progress = {},
}: ProblemResultsTableProps) {
  return (
    <>
    <div className="problem-table-wrap">
      <table className="problem-table" aria-label="Published problems">
        <thead>
          <tr>
            <th scope="col">Status</th>
            <th className="intermediate-secondary" scope="col">Evidence</th>
            <th scope="col">Problem</th>
            <th scope="col">Stage · Difficulty</th>
            <th className="intermediate-secondary" scope="col">Primary competency</th>
            <th scope="col">Topics</th>
            <th scope="col">Type</th>
            <th scope="col">Time</th>
            <th scope="col">Compute</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const href = problemHref(item.slug, returnUrl);
            const itemProgress = progress[item.slug] ?? { status: 'NOT_STARTED' };
            return (
              <tr
                key={item.slug}
                tabIndex={0}
                data-href={href}
                onClick={navigateRow}
                onKeyDown={navigateRowWithKeyboard}
                aria-label={`${item.title.en}, ${STATUS_LABELS[itemProgress.status]}`}
              >
                <td>
                  <span className={`status status-${itemProgress.status.toLowerCase()}`}>
                    <span aria-hidden="true">{statusIcon(itemProgress.status)}</span>
                    {STATUS_LABELS[itemProgress.status]}
                  </span>
                </td>
                <td className="intermediate-secondary">
                  {itemProgress.evidence ? (
                    <span className="evidence">{EVIDENCE_LABELS[itemProgress.evidence]}</span>
                  ) : (
                    <span aria-label="No learning evidence">—</span>
                  )}
                </td>
                <td className="problem-cell">
                  <Link data-problem-link href={href} prefetch>{item.title.en}</Link>
                  <span className="short-id">{item.public_short_id}</span>
                  <span>{item.objective.en}</span>
                </td>
                <td>{label(labels, item.stage_code)} · {label(labels, item.difficulty_code)}</td>
                <td className="intermediate-secondary">{label(labels, item.primary_competency_code)}</td>
                <td>
                  <div className="topic-list">
                    {item.topic_codes.map((code) => (
                      <span className="topic-chip" key={code}>{label(labels, code)}</span>
                    ))}
                    {item.remaining_topic_count ? (
                      <details className="topic-remainder">
                        <summary role="button" aria-label={`Show ${item.remaining_topic_count} more topic${item.remaining_topic_count === 1 ? '' : 's'}`}>
                          +{item.remaining_topic_count}
                        </summary>
                        <span>{item.remaining_topic_count} additional topic{item.remaining_topic_count === 1 ? '' : 's'}</span>
                      </details>
                    ) : null}
                  </div>
                </td>
                <td>{label(labels, item.task_type_code)}</td>
                <td>{item.expected_minutes} min</td>
                <td>
                  {label(labels, item.compute_tier_code)}
                  <details className="intermediate-details">
                    <summary role="button" aria-label="Show competency and evidence">Details</summary>
                    <span><strong>Competency:</strong> {label(labels, item.primary_competency_code)}</span>
                    <span><strong>Evidence:</strong> {itemProgress.evidence
                      ? EVIDENCE_LABELS[itemProgress.evidence]
                      : 'No learning evidence'}</span>
                  </details>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
    <ul className="problem-cards" aria-label="Published problem cards">
      {items.map((item) => {
        const href = problemHref(item.slug, returnUrl);
        const itemProgress = progress[item.slug] ?? { status: 'NOT_STARTED' };
        return (
          <li className="problem-card" key={item.slug}>
            <div className="problem-card-heading">
              <Link data-problem-link href={href} prefetch>{item.title.en}</Link>
              <span className={`status status-${itemProgress.status.toLowerCase()}`}>
                <span aria-hidden="true">{statusIcon(itemProgress.status)}</span>
                {STATUS_LABELS[itemProgress.status]}
              </span>
            </div>
            <p>{label(labels, item.stage_code)} · {label(labels, item.difficulty_code)}</p>
            <dl>
              <div><dt>Primary topic</dt><dd>{label(labels, item.topic_codes[0] ?? '')}</dd></div>
              <div><dt>Type</dt><dd>{label(labels, item.task_type_code)}</dd></div>
              <div><dt>Time</dt><dd>{item.expected_minutes} min</dd></div>
            </dl>
          </li>
        );
      })}
    </ul>
    </>
  );
}

const label = (labels: Record<string, string>, code: string): string =>
  labels[code] ?? code;

const problemHref = (slug: string, returnUrl: string): string =>
  `/problems/${encodeURIComponent(slug)}?return_to=${encodeURIComponent(returnUrl)}`;

const isInteractive = (target: EventTarget | null): boolean =>
  target instanceof Element && Boolean(target.closest('a, button, summary, details'));

const navigateRow = (event: MouseEvent<HTMLTableRowElement>): void => {
  if (isInteractive(event.target)) return;
  activateProblemLink(event.currentTarget);
};

const navigateRowWithKeyboard = (event: KeyboardEvent<HTMLTableRowElement>): void => {
  if (event.key !== 'Enter' || isInteractive(event.target)) return;
  activateProblemLink(event.currentTarget);
};

const activateProblemLink = (row: HTMLTableRowElement): void => {
  row.querySelector<HTMLAnchorElement>('a[data-problem-link]')?.click();
};

const statusIcon = (status: ProblemProgressDisplay['status']): string => ({
  NOT_STARTED: '○', ATTEMPTED: '◐', COMPLETED: '✓',
})[status];
