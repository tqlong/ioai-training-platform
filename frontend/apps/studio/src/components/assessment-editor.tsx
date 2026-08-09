'use client';

export const responseTypes = ['QUIZ_SINGLE', 'QUIZ_MULTIPLE', 'NUMERIC_ANSWER', 'SHORT_ANSWER', 'CODE_FUNCTION'] as const;
export type ResponseType = typeof responseTypes[number];
type TranslationState = 'COMPLETE' | 'PENDING';
type Localized = { en: string; vi: string; en_state: TranslationState; vi_state: TranslationState };
type Choice = { id: string; content: Localized };
type TestCase = { id: string; invocation: string; expected: string };
type ResponseDraft = Record<string, unknown> & { type: ResponseType; choices?: Choice[] };
type ScoringComponent = { method: string; weight: string; configuration: string | null };
export type AssessmentDraft = { response: ResponseDraft; scoring: { response_type: ResponseType; components: ScoringComponent[] }; scoringValid: boolean };

const localized = (): Localized => ({ en: '', vi: '', en_state: 'PENDING', vi_state: 'PENDING' });
const updateLocalized = (value: Localized, language: 'en' | 'vi', text: string): Localized => ({
  ...value,
  [language]: text,
  [`${language}_state`]: text.trim() ? 'COMPLETE' : 'PENDING',
});
const translationIssue = (value: Localized, language: 'en' | 'vi', label: string) => {
  const hasText = Boolean(value[language].trim());
  const pending = value[`${language}_state`] === 'PENDING';
  if (hasText && pending) return `${label} has text but is marked pending. Edit the field to repair its translation state.`;
  if (!hasText && !pending) return `${label} is empty but is marked complete. Edit the field to repair its translation state.`;
  return null;
};
const choice = (number: number): Choice => ({ id: `choice-${number}`, content: localized() });
const testCase = (number: number): TestCase => ({ id: `test-${number}`, invocation: '', expected: '' });

const emptyResponse = (type: ResponseType): ResponseDraft => {
  if (type === 'QUIZ_SINGLE') return { type, choices: [choice(1), choice(2)], correct_choice_id: '' };
  if (type === 'QUIZ_MULTIPLE') return { type, choices: [choice(1), choice(2)], correct_choice_ids: [] };
  if (type === 'NUMERIC_ANSWER') return { type, expected: '', absolute_tolerance: '0', unit: null };
  if (type === 'SHORT_ANSWER') return { type, reference_answer: localized(), accepted_keywords: [], rubric_guidance: '' };
  return { type, language: 'PYTHON', signature: '', starter_code: '', public_tests: [testCase(1)], hidden_tests: [], rubric_guidance: '' };
};

const defaultMethod = (type: ResponseType) => type === 'CODE_FUNCTION' ? 'UNIT_TESTS' : 'EXACT_MATCH';
export const emptyAssessmentDraft = (type: ResponseType): AssessmentDraft => ({
  response: emptyResponse(type),
  scoring: { response_type: type, components: [{ method: defaultMethod(type), weight: '1.0', configuration: null }] },
  scoringValid: true,
});

const decimalTotal = (weights: string[]): string => {
  const scale = Math.max(0, ...weights.map((weight) => weight.split('.')[1]?.length ?? 0));
  const factor = 10n ** BigInt(scale);
  const total = weights.reduce((sum, weight) => {
    if (!/^\d+(?:\.\d+)?$/.test(weight)) return sum;
    const [whole, fraction = ''] = weight.split('.');
    return sum + BigInt(whole) * factor + BigInt(fraction.padEnd(scale, '0'));
  }, 0n);
  const whole = total / factor;
  const fraction = scale ? String(total % factor).padStart(scale, '0').replace(/0+$/, '') : '';
  return fraction ? `${whole}.${fraction}` : `${whole}.0`;
};

export function AssessmentEditor({ value, onChange }: { value: AssessmentDraft; onChange: (value: AssessmentDraft) => void }) {
  const updateResponse = (patch: Record<string, unknown>) => onChange({ ...value, response: { ...value.response, ...patch } });
  const changeType = (type: ResponseType) => onChange(emptyAssessmentDraft(type));
  const components = value.scoring.components;
  const total = decimalTotal(components.map((item) => item.weight));
  const valid = total === '1.0' && components.every((item) => /^\d+(?:\.\d+)?$/.test(item.weight) && Number(item.weight) > 0);
  const updateComponents = (next: ScoringComponent[]) => onChange({
    ...value,
    scoring: { ...value.scoring, components: next },
    scoringValid: decimalTotal(next.map((item) => item.weight)) === '1.0' && next.every(
      (item) => /^\d+(?:\.\d+)?$/.test(item.weight) && Number(item.weight) > 0,
    ),
  });

  return <section aria-labelledby="assessment-heading" className="editor-section" id="response-scoring">
    <h2 id="assessment-heading">Response &amp; scoring</h2>
    <label><span>Response type</span><select aria-label="Response type" id="field-response-response-type" onChange={(event) => changeType(event.target.value as ResponseType)} value={value.response.type}>{responseTypes.map((type) => <option key={type} value={type}>{type.replaceAll('_', ' ')}</option>)}</select></label>
    {(value.response.type === 'QUIZ_SINGLE' || value.response.type === 'QUIZ_MULTIPLE') && <QuizFields response={value.response} update={updateResponse} />}
    {value.response.type === 'NUMERIC_ANSWER' && <div className="field-grid"><label><span>Expected value</span><input aria-label="Expected value" onChange={(event) => updateResponse({ expected: event.target.value })} step="any" type="number" value={String(value.response.expected)} /></label><label><span>Absolute tolerance</span><input aria-label="Absolute tolerance" min="0" onChange={(event) => updateResponse({ absolute_tolerance: event.target.value })} step="any" type="number" value={String(value.response.absolute_tolerance)} /></label><label><span>Unit (optional)</span><input onChange={(event) => updateResponse({ unit: event.target.value || null })} value={String(value.response.unit ?? '')} /></label></div>}
    {value.response.type === 'SHORT_ANSWER' && <ShortAnswerFields response={value.response} update={updateResponse} />}
    {value.response.type === 'CODE_FUNCTION' && <CodeFields response={value.response} update={updateResponse} />}
    <fieldset><legend>Scoring components</legend>{components.map((component, index) => <div className="repeated-row" key={index}><label><span>Method {index + 1}</span><select aria-label={`Scoring method ${index + 1}`} onChange={(event) => updateComponents(components.map((item, itemIndex) => itemIndex === index ? { ...item, method: event.target.value } : item))} value={component.method}>{(value.response.type === 'CODE_FUNCTION' ? ['UNIT_TESTS', 'PARTIAL_TESTS', 'RUBRIC_HUMAN'] : ['EXACT_MATCH', 'RUBRIC_HUMAN']).map((method) => <option key={method}>{method}</option>)}</select></label><label><span>Weight {index + 1}</span><input aria-label={`Scoring weight ${index + 1}`} inputMode="decimal" onChange={(event) => updateComponents(components.map((item, itemIndex) => itemIndex === index ? { ...item, weight: event.target.value } : item))} value={component.weight} /></label><label><span>Configuration {index + 1} (optional)</span><input aria-label={`Scoring configuration ${index + 1}`} onChange={(event) => updateComponents(components.map((item, itemIndex) => itemIndex === index ? { ...item, configuration: event.target.value || null } : item))} value={component.configuration ?? ''} /></label>{components.length > 1 && <button aria-label={`Remove scoring component ${index + 1}`} onClick={() => updateComponents(components.filter((_, itemIndex) => itemIndex !== index))} type="button">Remove</button>}</div>)}<button onClick={() => updateComponents([...components, { method: defaultMethod(value.response.type), weight: '', configuration: null }])} type="button">Add scoring component</button><p>Exact total: {total}</p>{!valid && <p role="alert">Scoring weights must be positive decimals and must total exactly 1.0.</p>}</fieldset>
  </section>;
}

function QuizFields({ response, update }: { response: ResponseDraft; update: (patch: Record<string, unknown>) => void }) {
  const choices = response.choices as Choice[];
  const multiple = response.type === 'QUIZ_MULTIPLE';
  const correctIds = new Set(multiple ? response.correct_choice_ids as string[] : [response.correct_choice_id as string]);
  const setCorrect = (id: string, checked: boolean) => update(multiple ? {
    correct_choice_ids: checked ? [...correctIds, id] : [...correctIds].filter((item) => item !== id),
  } : { correct_choice_id: id });
  return <fieldset><legend>Choices and answer key</legend>{choices.map((item, index) => {
    const enIssue = translationIssue(item.content, 'en', `Choice ${index + 1} English`);
    const viIssue = translationIssue(item.content, 'vi', `Choice ${index + 1} Vietnamese`);
    return <fieldset aria-label={`Choice ${index + 1}`} key={item.id}><legend>Choice {index + 1}</legend><label><span>Stable ID</span><input onChange={(event) => update({ choices: choices.map((choiceItem, itemIndex) => itemIndex === index ? { ...choiceItem, id: event.target.value } : choiceItem) })} value={item.id} /></label><label><span>English</span><input aria-describedby={enIssue ? `choice-${index}-en-error` : undefined} aria-invalid={Boolean(enIssue)} id={`field-response-choices-${index}-content-en`} onChange={(event) => update({ choices: choices.map((choiceItem, itemIndex) => itemIndex === index ? { ...choiceItem, content: updateLocalized(choiceItem.content, 'en', event.target.value) } : choiceItem) })} value={item.content.en} /></label>{enIssue && <p className="field-error" id={`choice-${index}-en-error`} role="alert">{enIssue}</p>}<label><span>Vietnamese</span><input aria-describedby={viIssue ? `choice-${index}-vi-error` : undefined} aria-invalid={Boolean(viIssue)} id={`field-response-choices-${index}-content-vi`} onChange={(event) => update({ choices: choices.map((choiceItem, itemIndex) => itemIndex === index ? { ...choiceItem, content: updateLocalized(choiceItem.content, 'vi', event.target.value) } : choiceItem) })} value={item.content.vi} /></label>{viIssue && <p className="field-error" id={`choice-${index}-vi-error`} role="alert">{viIssue}</p>}<label className="choice-row"><input checked={correctIds.has(item.id)} name={multiple ? undefined : 'correct-choice'} onChange={(event) => setCorrect(item.id, event.target.checked)} type={multiple ? 'checkbox' : 'radio'} /><span>Correct answer</span></label><button aria-label={`Remove choice ${index + 1}`} disabled={choices.length <= 2} onClick={() => update({ choices: choices.filter((_, itemIndex) => itemIndex !== index) })} type="button">Remove</button></fieldset>;
  })}<button onClick={() => update({ choices: [...choices, choice(choices.length + 1)] })} type="button">Add choice</button></fieldset>;
}

function ShortAnswerFields({ response, update }: { response: ResponseDraft; update: (patch: Record<string, unknown>) => void }) {
  const reference = response.reference_answer as Localized;
  const enIssue = translationIssue(reference, 'en', 'Reference answer English');
  const viIssue = translationIssue(reference, 'vi', 'Reference answer Vietnamese');
  return <div className="field-grid"><label><span>Reference answer (English)</span><textarea aria-describedby={enIssue ? 'reference-answer-en-error' : undefined} aria-invalid={Boolean(enIssue)} id="field-response-reference-answer-en" onChange={(event) => update({ reference_answer: updateLocalized(reference, 'en', event.target.value) })} value={reference.en} /></label>{enIssue && <p className="field-error" id="reference-answer-en-error" role="alert">{enIssue}</p>}<label><span>Reference answer (Vietnamese)</span><textarea aria-describedby={viIssue ? 'reference-answer-vi-error' : undefined} aria-invalid={Boolean(viIssue)} id="field-response-reference-answer-vi" onChange={(event) => update({ reference_answer: updateLocalized(reference, 'vi', event.target.value) })} value={reference.vi} /></label>{viIssue && <p className="field-error" id="reference-answer-vi-error" role="alert">{viIssue}</p>}<label><span>Accepted keywords (one per line)</span><textarea onChange={(event) => update({ accepted_keywords: event.target.value.split('\n').map((word) => word.trim()).filter(Boolean) })} value={(response.accepted_keywords as string[]).join('\n')} /></label><label><span>Rubric guidance</span><textarea onChange={(event) => update({ rubric_guidance: event.target.value })} value={String(response.rubric_guidance)} /></label></div>;
}

function CodeFields({ response, update }: { response: ResponseDraft; update: (patch: Record<string, unknown>) => void }) {
  return <div><label><span>Function signature</span><input aria-label="Function signature" onChange={(event) => update({ signature: event.target.value })} value={String(response.signature)} /></label><label><span>Starter code</span><textarea onChange={(event) => update({ starter_code: event.target.value })} value={String(response.starter_code)} /></label><TestFields kind="Public" minimum={0} tests={response.public_tests as TestCase[]} update={(tests) => update({ public_tests: tests })} /><TestFields kind="Hidden" minimum={0} tests={response.hidden_tests as TestCase[]} update={(tests) => update({ hidden_tests: tests })} /><p>At least one public or hidden test is required for validation.</p><label><span>Rubric guidance</span><textarea onChange={(event) => update({ rubric_guidance: event.target.value })} value={String(response.rubric_guidance)} /></label></div>;
}

function TestFields({ kind, tests, update, minimum }: { kind: 'Public' | 'Hidden'; tests: TestCase[]; update: (tests: TestCase[]) => void; minimum: number }) {
  return <fieldset><legend>{kind} tests</legend>{tests.map((test, index) => <fieldset aria-label={`${kind} test ${index + 1}`} key={`${test.id}-${index}`}><legend>Test {index + 1}</legend><label><span>Stable ID</span><input onChange={(event) => update(tests.map((item, itemIndex) => itemIndex === index ? { ...item, id: event.target.value } : item))} value={test.id} /></label><label><span>Invocation</span><input aria-label={`${kind} test invocation ${index + 1}`} onChange={(event) => update(tests.map((item, itemIndex) => itemIndex === index ? { ...item, invocation: event.target.value } : item))} value={test.invocation} /></label><label><span>Expected result</span><input aria-label={`${kind} test expected ${index + 1}`} onChange={(event) => update(tests.map((item, itemIndex) => itemIndex === index ? { ...item, expected: event.target.value } : item))} value={test.expected} /></label><button aria-label={`Remove ${kind.toLowerCase()} test ${index + 1}`} disabled={tests.length <= minimum} onClick={() => update(tests.filter((_, itemIndex) => itemIndex !== index))} type="button">Remove</button></fieldset>)}<button onClick={() => update([...tests, testCase(tests.length + 1)])} type="button">Add {kind.toLowerCase()} test</button></fieldset>;
}
