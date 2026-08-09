'use client';

import type { PublicProblemDetail } from '@ioai/api-client';
import { useState, type FormEvent } from 'react';

export type LearnerResponse =
  | { type: 'QUIZ_SINGLE'; choice_id: string }
  | { type: 'QUIZ_MULTIPLE'; choice_ids: string[] }
  | { type: 'NUMERIC_ANSWER'; value: string }
  | { type: 'SHORT_ANSWER'; text: string }
  | { type: 'CODE_FUNCTION'; code: string };

type Schema = PublicProblemDetail['response_schema'];
type Props = { schema: Schema; onSubmit: (response: LearnerResponse) => void };

export function ResponseForm({ schema, onSubmit }: Props) {
  const [single, setSingle] = useState('');
  const [multiple, setMultiple] = useState<string[]>([]);
  const [text, setText] = useState(schema.starter_code ?? '');
  const [error, setError] = useState('');
  const choices = (schema.choices ?? []).map(choice);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    let response: LearnerResponse | undefined;
    if (schema.type === 'QUIZ_SINGLE') {
      if (!single) return setError('Choose one answer.');
      response = { type: schema.type, choice_id: single };
    } else if (schema.type === 'QUIZ_MULTIPLE') {
      if (!multiple.length) return setError('Choose at least one answer.');
      response = { type: schema.type, choice_ids: multiple };
    } else if (schema.type === 'NUMERIC_ANSWER') {
      if (!text.trim() || !Number.isFinite(Number(text))) return setError('Enter a finite number.');
      response = { type: schema.type, value: text.trim() };
    } else if (schema.type === 'SHORT_ANSWER') {
      if (!text.trim()) return setError('Enter your answer.');
      response = { type: schema.type, text: text.trim() };
    } else if (schema.type === 'CODE_FUNCTION') {
      if (!text.trim()) return setError('Enter Python code.');
      response = { type: schema.type, code: text };
    } else return setError('This response type is unavailable.');
    setError('');
    onSubmit(response);
  };

  return <form className="response-form" onSubmit={submit} noValidate>
    {schema.type === 'QUIZ_SINGLE' || schema.type === 'QUIZ_MULTIPLE' ? <fieldset>
      <legend>{schema.type === 'QUIZ_SINGLE' ? 'Choose one answer' : 'Choose all that apply'}</legend>
      {choices.map((item) => <label key={item.id}><input type={schema.type === 'QUIZ_SINGLE' ? 'radio' : 'checkbox'} name="choice" value={item.id} checked={schema.type === 'QUIZ_SINGLE' ? single === item.id : multiple.includes(item.id)} onChange={() => schema.type === 'QUIZ_SINGLE' ? setSingle(item.id) : setMultiple(current => current.includes(item.id) ? current.filter(id => id !== item.id) : [...current, item.id])} /> <span>{item.label}</span></label>)}
    </fieldset> : null}
    {schema.type === 'NUMERIC_ANSWER' ? <label><span>Numeric answer</span><input aria-label="Numeric answer" inputMode="decimal" value={text} onChange={event => setText(event.target.value)} /><small>Answer{schema.unit ? ` in ${schema.unit}` : ''}. Accepted tolerance: ±{schema.absolute_tolerance ?? '0'}.</small></label> : null}
    {schema.type === 'SHORT_ANSWER' ? <label><span>Short answer</span><textarea aria-label="Short answer" maxLength={4000} value={text} onChange={event => setText(event.target.value)} /></label> : null}
    {schema.type === 'CODE_FUNCTION' ? <div className="code-response"><p>Language: {schema.language === 'PYTHON' ? 'Python' : schema.language}</p><pre>{schema.signature}</pre><label><span>Python code</span><textarea aria-label="Python code" maxLength={20000} spellCheck={false} value={text} onChange={event => setText(event.target.value)} /></label><h3>Public examples</h3><ul>{(schema.public_tests ?? []).map(test => { const item = publicTest(test); return <li key={item.id}><code>{item.invocation} → {item.expected}</code></li>; })}</ul></div> : null}
    {error ? <p className="field-error" role="alert">{error}</p> : null}
    <button type="submit">Submit answer</button>
  </form>;
}

const choice = (value: Record<string, unknown>) => {
  const content = value.content as Record<string, unknown> | undefined;
  return { id: String(value.id ?? ''), label: String(content?.en ?? value.id ?? '') };
};
const publicTest = (value: Record<string, unknown>) => ({
  id: String(value.id ?? ''), invocation: String(value.invocation ?? ''), expected: String(value.expected ?? ''),
});
