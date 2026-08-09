'use client';

import type {
  ApiClient,
  PublicFeedbackRequest,
  PublicFeedbackReceipt,
  PublicProblemDetail,
  PublicProblemRecommendation,
  PublicSubmissionRequest,
  PublicSubmissionResult,
} from '@ioai/api-client';
import { ApiError } from '@ioai/api-client';
import { useEffect, useRef, useState, type KeyboardEvent } from 'react';

import { learnApi } from '../api';
import { browserProgressAdapter } from '../learner-progress';
import { ResponseEntry } from './response-entry';

type Props = {
  slug: string; title: string; stage: string;
  schema: PublicProblemDetail['response_schema'];
  submitAssessment?: (slug: string, request: PublicSubmissionRequest) => Promise<PublicSubmissionResult>;
  submitFeedback?: (slug: string, request: PublicFeedbackRequest) => Promise<PublicFeedbackReceipt>;
  getRecommendation?: ApiClient['getPublicRecommendation'];
  assessmentKeyGenerator?: () => string;
  feedbackKeyGenerator?: () => string;
};

export function LearnerActions({
  slug, title, stage, schema,
  submitAssessment,
  submitFeedback = (problemSlug, request) => learnApi.submitPublicFeedback(problemSlug, request),
  getRecommendation = (problemSlug, query) => learnApi.getPublicRecommendation(problemSlug, query),
  assessmentKeyGenerator,
  feedbackKeyGenerator = () => crypto.randomUUID(),
}: Props) {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [recommendation, setRecommendation] = useState<PublicProblemRecommendation | null>();
  const openButton = useRef<HTMLButtonElement>(null);

  const assessed = async (result: PublicSubmissionResult) => {
    if (result.outcome !== 'ACCEPTED_RESULT' || !result.passed) return;
    const progress = browserProgressAdapter()?.read().state;
    const next = await getRecommendation(slug, {
      stage,
      completed: progress?.recentCompleted.map(item => item.slug) ?? [slug],
    }).catch(() => null);
    setRecommendation(next);
  };

  return <>
    <ResponseEntry
      slug={slug} title={title} schema={schema}
      submit={submitAssessment} keyGenerator={assessmentKeyGenerator}
      onResult={result => void assessed(result)}
    />
    <section className="learner-continuation" aria-label="Continue learning">
      {recommendation ? <article><p className="eyebrow">{recommendation.label}</p><h2>{recommendation.title.en}</h2><p>{recommendation.reason}</p><a onClick={() => browserProgressAdapter()?.recordTransition(slug, recommendation.slug)} href={`${recommendation.permanent_url}?return_to=${encodeURIComponent(`/problems?stage=${stage}`)}`}>Continue to {recommendation.title.en}</a></article> : null}
      <button ref={openButton} type="button" onClick={() => setFeedbackOpen(true)}>Report a problem</button>
    </section>
    {feedbackOpen ? <FeedbackDialog
      slug={slug} submit={submitFeedback} keyGenerator={feedbackKeyGenerator}
      onClose={() => { setFeedbackOpen(false); queueMicrotask(() => openButton.current?.focus()); }}
    /> : null}
  </>;
}

function FeedbackDialog({ slug, submit, keyGenerator, onClose }: {
  slug: string;
  submit: NonNullable<Props['submitFeedback']>;
  keyGenerator: () => string;
  onClose: () => void;
}) {
  const [category, setCategory] = useState<PublicFeedbackRequest['category']>('CONTENT_ISSUE');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [receipt, setReceipt] = useState<PublicFeedbackReceipt>();
  const [pending, setPending] = useState(false);
  const key = useRef<string>();
  const categoryRef = useRef<HTMLSelectElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  useEffect(() => { categoryRef.current?.focus(); }, []);
  const send = async () => {
    if (!message.trim() || pending) return;
    key.current ??= keyGenerator();
    setPending(true); setError('');
    try { setReceipt(await submit(slug, { feedback_key: key.current, category, message: message.trim() })); }
    catch (caught) {
      setError(caught instanceof ApiError && caught.code === 'FEEDBACK_RATE_LIMITED'
        ? 'Too many feedback reports. Please try again later.'
        : 'Feedback could not be sent. Your message remains editable.');
    }
    finally { setPending(false); }
  };
  return <div className="dialog-backdrop" onKeyDown={event => {
    if (event.key === 'Escape') onClose();
    if (event.key === 'Tab') trapFocus(event, dialogRef.current);
  }}>
    <section ref={dialogRef} className="feedback-dialog" role="dialog" aria-modal="true" aria-labelledby="feedback-title">
      <h2 id="feedback-title">Report a problem</h2>
      <label><span>Category</span><select ref={categoryRef} value={category} onChange={event => setCategory(event.target.value as PublicFeedbackRequest['category'])}><option value="CONTENT_ISSUE">Content issue</option><option value="TYPO">Typo</option><option value="SCORING_ISSUE">Scoring issue</option><option value="ACCESSIBILITY">Accessibility</option><option value="OTHER">Other</option></select></label>
      <label><span>Message</span><textarea maxLength={2000} value={message} onChange={event => setMessage(event.target.value)} /></label>
      {pending ? <p role="status">Sending feedback…</p> : null}
      {error ? <div role="alert"><p>{error}</p><button type="button" onClick={() => void send()}>Try feedback again</button></div> : null}
      {receipt ? <p role="status">{receipt.message}</p> : null}
      <div className="dialog-actions"><button type="button" onClick={() => void send()} disabled={!message.trim() || pending}>Send feedback</button><button type="button" onClick={onClose}>Close feedback</button></div>
    </section>
  </div>;
}

const trapFocus = (event: KeyboardEvent, container: HTMLElement | null) => {
  if (!container) return;
  const controls = Array.from(container.querySelectorAll<HTMLElement>('button:not(:disabled), select, textarea'));
  if (!controls.length) return;
  const first = controls[0]!;
  const last = controls.at(-1)!;
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
};
