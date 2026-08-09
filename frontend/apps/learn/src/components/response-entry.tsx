'use client';

import type { PublicProblemDetail, PublicSubmissionRequest, PublicSubmissionResult } from '@ioai/api-client';
import { useRef, useState } from 'react';

import { learnApi } from '../api';
import { ResponseForm, type LearnerResponse } from './response-form';

type Submit = (slug: string, request: PublicSubmissionRequest) => Promise<PublicSubmissionResult>;
type Props = {
  slug: string;
  schema: PublicProblemDetail['response_schema'];
  submit?: Submit;
  keyGenerator?: () => string;
};

export function ResponseEntry({
  slug,
  schema,
  submit = (problemSlug, request) => learnApi.submitPublicProblem(problemSlug, request),
  keyGenerator = () => crypto.randomUUID(),
}: Props) {
  const [result, setResult] = useState<PublicSubmissionResult>();
  const [error, setError] = useState(false);
  const [pending, setPending] = useState(false);
  const response = useRef<LearnerResponse>();
  const submissionKey = useRef<string>();

  const send = async (answer: LearnerResponse) => {
    if (pending) return;
    response.current = answer;
    submissionKey.current ??= keyGenerator();
    setPending(true);
    setError(false);
    try {
      setResult(await submit(slug, {
        submission_key: submissionKey.current,
        response: answer,
      }));
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
