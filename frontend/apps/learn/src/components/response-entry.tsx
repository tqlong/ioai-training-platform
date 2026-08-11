'use client';

import type { PublicProblemDetail, PublicSubmissionRequest, PublicSubmissionResult } from '@ioai/api-client';
import { useRef, useState } from 'react';

import { learnApi } from '../api';
import { browserProgressAdapter } from '../learner-progress';
import { recordSubmission } from '../submission-history';
import { ResponseForm, type LearnerResponse } from './response-form';

type Submit = (slug: string, request: PublicSubmissionRequest) => Promise<PublicSubmissionResult>;
type Props = {
  slug: string;
  title: string;
  schema: PublicProblemDetail['response_schema'];
  submit?: Submit;
  keyGenerator?: () => string;
  onResult?: (result: PublicSubmissionResult) => void;
};

export function ResponseEntry({
  slug,
  title,
  schema,
  submit = (problemSlug, request) => learnApi.submitPublicProblem(problemSlug, request),
  keyGenerator = () => crypto.randomUUID(),
  onResult,
}: Props) {
  const [result, setResult] = useState<PublicSubmissionResult>();
  const [error, setError] = useState(false);
  const [pending, setPending] = useState(false);
  const response = useRef<LearnerResponse>();
  const submissionKey = useRef<string>();
  const receipt = useRef<string>();

  const send = async (answer: LearnerResponse) => {
    if (pending) return;
    response.current = answer;
    submissionKey.current ??= keyGenerator();
    receipt.current ??= keyGenerator();
    setPending(true);
    setError(false);
    try {
      const assessed = await submit(slug, {
        submission_key: submissionKey.current,
        receipt: receipt.current,
        response: answer,
      });
      setResult(assessed);
      onResult?.(assessed);
      recordSubmission(assessed, { receipt: receipt.current, slug, title });
      browserProgressAdapter()?.record({
        slug, title,
        status: assessed.outcome === 'ACCEPTED_RESULT' && assessed.passed
          ? 'COMPLETED'
          : 'ATTEMPTED',
      });
    } catch {
      setError(true);
    } finally {
      setPending(false);
    }
  };

  return <section className="response-placeholder" aria-label="Your response">
    <h2>Your response</h2>
    <ResponseForm schema={schema} onSubmit={send} />
    {pending ? <p role="status">Assessing your answer…</p> : null}
    {error ? <div className="submission-error" role="alert"><p>Your answer could not be assessed. It remains editable.</p><button type="button" onClick={() => response.current && void send(response.current)}>Try submission again</button></div> : null}
    {result ? <div className="assessment-result" role="status"><p>{result.message}</p>{result.score ? <p>Score: {result.score}</p> : null}{result.components?.length ? <ul>{result.components.map((item, index) => <li key={`${item.method}-${index}`}>{item.method.replaceAll('_', ' ').toLowerCase()}: {item.score}</li>)}</ul> : null}</div> : null}
  </section>;
}
