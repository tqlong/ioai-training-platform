'use client';

import { useEffect, useState } from 'react';

import { readSubmissionHistory, type LocalSubmission } from '../submission-history';

export function SubmissionHistory() {
  const [items, setItems] = useState<LocalSubmission[]>([]);
  useEffect(() => setItems(readSubmissionHistory()), []);
  return <main className="submission-page"><p className="eyebrow">IOAI Learn</p><h1>My submissions</h1>
    <p>Stored privately on this device. Clearing browser data removes these links.</p>
    {items.length ? <ul>{items.map(item => <li key={item.attemptId}>
      <a href={`/submissions/${encodeURIComponent(item.attemptId)}`}>{item.title}</a>
      <span>{item.status === 'PENDING_ASSESSMENT' ? 'Pending assessment' : 'Assessed'}</span>
      <time dateTime={item.submittedAt}>{new Date(item.submittedAt).toLocaleString()}</time>
    </li>)}</ul> : <p>No submissions are stored on this device yet.</p>}
  </main>;
}
