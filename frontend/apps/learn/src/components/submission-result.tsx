'use client';

import type { PublicSubmissionResult } from '@ioai/api-client';
import { useEffect, useState } from 'react';

import { learnApi } from '../api';
import { browserProgressAdapter } from '../learner-progress';
import { readSubmissionHistory, updateSubmissionStatus } from '../submission-history';

export function SubmissionResult({ attemptId }: { attemptId: string }) {
  const [result, setResult] = useState<PublicSubmissionResult>();
  const [missing, setMissing] = useState(false);
  useEffect(() => {
    const local = readSubmissionHistory().find(item => item.attemptId === attemptId);
    if (!local) { setMissing(true); return; }
    void learnApi.getPublicSubmission(attemptId, local.receipt).then(value => {
      setResult(value); updateSubmissionStatus(attemptId, value.outcome, value.passed ?? undefined);
      const hasPassedAttempt = readSubmissionHistory().some(item => item.slug === local.slug && item.passed);
      browserProgressAdapter()?.reconcile({ slug: local.slug, title: local.title,
        status: hasPassedAttempt ? 'COMPLETED' : 'ATTEMPTED' });
    }).catch(() => setMissing(true));
  }, [attemptId]);
  if (missing) return <main className="submission-page"><h1>Submission unavailable</h1><p>This device does not have the private receipt, or the submission no longer exists.</p></main>;
  if (!result) return <main className="submission-page"><h1>Submission result</h1><p role="status">Loading submission…</p></main>;
  return <main className="submission-page"><a href="/submissions">← My submissions</a><h1>Submission result</h1>
    <p>{result.outcome === 'PENDING_ASSESSMENT' ? 'Pending assessment' : result.passed ? 'Passed' : 'Assessed — not yet passed'}</p>
    {result.score ? <p>Score: {result.score}</p> : null}
    {result.submitted_response ? <section><h2>Your answer</h2><pre>{JSON.stringify(result.submitted_response, null, 2)}</pre></section> : null}
    {result.criteria?.length ? <section><h2>Rubric result</h2><ul>{result.criteria.map(item => <li key={`${item.component_index}-${item.criterion_id}`}><strong>{String(item.title?.en ?? item.criterion_id)}</strong>: {String(item.level_label?.en ?? item.level_id)} — {item.points}/{item.maximum_points}{item.feedback ? <p>{item.feedback}</p> : null}</li>)}</ul></section> : null}
    {result.overall_feedback ? <section><h2>Reviewer feedback</h2><p>{result.overall_feedback}</p></section> : null}
  </main>;
}
