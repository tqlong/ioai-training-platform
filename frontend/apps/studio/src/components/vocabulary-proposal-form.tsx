'use client';

import { useState } from 'react';
import type { FormEvent } from 'react';
import Link from 'next/link';

import { studioApi } from '../api';

const proposalTypes = ['PATHWAY_STAGE', 'DIFFICULTY', 'TASK_TYPE', 'COMPETENCY', 'TOPIC'];

export function VocabularyProposalForm() {
  const [vocabularyType, setVocabularyType] = useState('TOPIC');
  const [note, setNote] = useState('');
  const [state, setState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState('saving');
    try {
      await studioApi.recordVocabularyProposal({ vocabulary_type: vocabularyType, note });
      setState('saved');
      setNote('');
    } catch {
      setState('failed');
    }
  }

  return (
    <main className="studio-shell">
      <Link href="/author/problems">Back to problems</Link>
      <h1>Propose a vocabulary value</h1>
      <p>Proposals enter editorial review and cannot be selected as problem metadata.</p>
      <form className="editor-section" onSubmit={submit}>
        <label><span>Vocabulary type</span><select onChange={(event) => setVocabularyType(event.target.value)} value={vocabularyType}>{proposalTypes.map((type) => <option key={type} value={type}>{type.replaceAll('_', ' ')}</option>)}</select></label>
        <label><span>Proposal and rationale</span><textarea onChange={(event) => setNote(event.target.value)} required rows={6} value={note} /></label>
        <button disabled={state === 'saving'} type="submit">{state === 'saving' ? 'Submitting…' : 'Submit for review'}</button>
        {state === 'saved' && <p role="status">Proposal submitted for separate editorial review.</p>}
        {state === 'failed' && <p role="alert">Proposal could not be submitted. Keep your text and try again.</p>}
      </form>
    </main>
  );
}
