'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { studioApi } from '../api';

export function NewDraft() {
  const router = useRouter();
  const [state, setState] = useState<'idle' | 'creating' | 'failed'>('idle');

  const create = async () => {
    setState('creating');
    try {
      const draft = await studioApi.createAuthorDraft();
      router.replace(`/author/problems/${draft.problem_id}`);
    } catch {
      setState('failed');
    }
  };

  return (
    <section className="studio-page narrow-page">
      <p className="eyebrow">New structured problem</p>
      <h1>Create a draft</h1>
      <p>This creates private problem and revision identities. It does not create a public URL.</p>
      <button disabled={state === 'creating'} onClick={() => void create()} type="button">
        {state === 'creating' ? 'Creating...' : 'Initialize draft'}
      </button>
      {state === 'failed' && <p role="alert">Draft creation failed. Try again.</p>}
    </section>
  );
}
