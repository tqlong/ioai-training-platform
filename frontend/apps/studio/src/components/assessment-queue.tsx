'use client';

import type { AssessmentDetail, AssessmentList } from '@ioai/api-client';
import { useEffect, useState } from 'react';

import { studioApi } from '../api';

export function AssessmentQueue() {
  const [status, setStatus] = useState<'PENDING' | 'ASSESSED'>('PENDING');
  const [problem, setProblem] = useState('');
  const [list, setList] = useState<AssessmentList>();
  useEffect(() => {
    let current = true;
    void studioApi.listAuthorAssessments({ status, problem: problem || undefined })
      .then(value => { if (current) setList(value); });
    return () => { current = false; };
  }, [status, problem]);
  return <section><p className="eyebrow">Manual assessment</p><h1>Assessment queue</h1><label><span>Status</span><select value={status} onChange={event => setStatus(event.target.value as typeof status)}><option value="PENDING">Pending</option><option value="ASSESSED">Assessed history</option></select></label>
    <label><span>Problem slug</span><input value={problem} onChange={event => setProblem(event.target.value)} /></label>
    {!list ? <p role="status">Loading assessments…</p> : list.items.length ? <table><thead><tr><th>Problem</th><th>Status</th><th>Submitted</th><th>Score</th></tr></thead><tbody>{list.items.map(item => <tr key={item.attempt_id}><td><a href={`/author/assessments/${item.attempt_id}`}>{String(item.title.en ?? item.slug)}</a></td><td>{item.status}</td><td>{new Date(item.submitted_at).toLocaleString()}</td><td>{item.score ?? '—'}</td></tr>)}</tbody></table> : <p>No {status.toLowerCase()} assessments.</p>}
  </section>;
}

type Criterion = { componentIndex: number; id: string; title: string; levels: Array<{ id: string; label: string; points: string }> };

export function AssessmentForm({ attemptId }: { attemptId: string }) {
  const [detail, setDetail] = useState<AssessmentDetail>();
  const [selections, setSelections] = useState<Record<string, string>>({});
  const [criterionFeedback, setCriterionFeedback] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState('');
  const [reason, setReason] = useState('');
  const [message, setMessage] = useState('');
  useEffect(() => { void studioApi.getAuthorAssessment(attemptId).then(setDetail); }, [attemptId]);
  if (!detail) return <p role="status">Loading assessment…</p>;
  const criteria = rubricCriteria(detail);
  const save = async () => {
    if (!window.confirm(detail.latest_decision ? 'Save this assessment correction?' : 'Complete this assessment?')) return;
    try {
      const next = await studioApi.decideAuthorAssessment(attemptId, {
        selections: criteria.map(item => ({ component_index: item.componentIndex, criterion_id: item.id, level_id: selections[`${item.componentIndex}:${item.id}`]!, feedback: criterionFeedback[`${item.componentIndex}:${item.id}`] || null })),
        overall_feedback: feedback || null,
        expected_decision_id: detail.latest_decision ? String(detail.latest_decision.decision_id) : null,
        correction_reason: detail.latest_decision ? reason : null,
      });
      setDetail(next); setMessage('Assessment saved.');
    } catch { setMessage('Assessment could not be saved. Refresh and try again.'); }
  };
  return <section><a href="/author/assessments">← Assessment queue</a><h1>{String(detail.title.en ?? detail.slug)}</h1><p>Status: {detail.status}</p><section><h2>Learner answer</h2><pre>{JSON.stringify(detail.submitted_response, null, 2)}</pre></section>{detail.decision_history?.length ? <section><h2>Decision history</h2><ol>{(detail.decision_history ?? []).map(item => <li key={String(item.decision_id)}>Version {String(item.version)} — score {String((item.result as Record<string, unknown>).score ?? '—')}{item.correction_reason ? <p>Correction: {String(item.correction_reason)}</p> : null}</li>)}</ol></section> : null}<form onSubmit={event => { event.preventDefault(); void save(); }}><h2>Published rubric</h2>{criteria.map(item => { const key = `${item.componentIndex}:${item.id}`; return <fieldset key={key}><legend>{item.title}</legend>{item.levels.map(level => <label key={level.id}><input checked={selections[key] === level.id} name={key} onChange={() => setSelections({ ...selections, [key]: level.id })} required type="radio" /><span>{level.label} — {level.points} points</span></label>)}<label><span>Criterion feedback (optional)</span><textarea maxLength={2000} value={criterionFeedback[key] ?? ''} onChange={event => setCriterionFeedback({ ...criterionFeedback, [key]: event.target.value })} /></label></fieldset>; })}<label><span>Overall learner feedback (optional)</span><textarea maxLength={2000} value={feedback} onChange={event => setFeedback(event.target.value)} /></label>{detail.latest_decision ? <label><span>Correction reason</span><textarea required maxLength={2000} value={reason} onChange={event => setReason(event.target.value)} /></label> : null}<button disabled={criteria.some(item => !selections[`${item.componentIndex}:${item.id}`])} type="submit">{detail.latest_decision ? 'Save correction' : 'Complete assessment'}</button>{message ? <p role="status">{message}</p> : null}</form></section>;
}

const rubricCriteria = (detail: AssessmentDetail): Criterion[] => {
  const components = Array.isArray(detail.scoring.components) ? detail.scoring.components : [];
  return components.flatMap((raw, componentIndex) => {
    const component = raw as { method?: string; configuration?: { criteria?: Array<Record<string, unknown>> } };
    if (component.method !== 'RUBRIC_HUMAN') return [];
    return (component.configuration?.criteria ?? []).map(criterion => ({ componentIndex, id: String(criterion.id), title: String((criterion.title as Record<string, unknown>)?.en ?? criterion.id), levels: ((criterion.levels as Array<Record<string, unknown>>) ?? []).map(level => ({ id: String(level.id), label: String((level.label as Record<string, unknown>)?.en ?? level.id), points: String(level.points) })) }));
  });
};
