'use client';

import type { PublicProblemDetail } from '@ioai/api-client';
import { useState } from 'react';

import { ResponseForm } from './response-form';

export function ResponseEntry({ schema }: { schema: PublicProblemDetail['response_schema'] }) {
  const [ready, setReady] = useState(false);
  return <section className="response-placeholder" aria-label="Your response">
    <h2>Your response</h2>
    <ResponseForm schema={schema} onSubmit={() => setReady(true)} />
    {ready ? <p role="status">Answer validated and ready.</p> : null}
  </section>;
}
