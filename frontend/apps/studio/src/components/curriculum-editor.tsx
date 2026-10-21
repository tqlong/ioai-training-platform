'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

import type { AuthorVocabularyRecord } from '@ioai/api-client';

import { studioApi } from '../api';

export type CanonicalIdentity = [string, string];
export type PrerequisiteDraft = {
  relationship: string;
  target_type: string;
  target_identity: CanonicalIdentity | null;
  target_id: string | null;
  minimum_evidence: string | null;
};
export type CurriculumDraft = {
  stage: CanonicalIdentity | null;
  difficulty: CanonicalIdentity | null;
  primary_competency: CanonicalIdentity | null;
  secondary_competencies: CanonicalIdentity[];
  task_type: CanonicalIdentity | null;
  topics: CanonicalIdentity[];
  prerequisites: PrerequisiteDraft[];
};

export const emptyCurriculumDraft = (): CurriculumDraft => ({
  stage: null,
  difficulty: null,
  primary_competency: null,
  secondary_competencies: [],
  task_type: null,
  topics: [],
  prerequisites: [],
});

export function CurriculumEditorLoader({
  value,
  onChange,
}: {
  value: CurriculumDraft;
  onChange: (value: CurriculumDraft) => void;
}) {
  const [records, setRecords] = useState<AuthorVocabularyRecord[]>([]);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all(
      ['PATHWAY_STAGE', 'DIFFICULTY', 'TASK_TYPE', 'COMPETENCY', 'TOPIC'].map(
        (vocabularyType) => studioApi.listAuthorVocabulary({
          vocabularyType,
          includeDescendants: vocabularyType === 'TOPIC',
          limit: 500,
        }),
      ),
    ).then((responses) => {
      if (active) setRecords(responses.flatMap((response) => response.items));
    }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, []);
  if (error) return <p role="alert">Canonical curriculum values could not be loaded.</p>;
  if (records.length === 0) return <p aria-live="polite">Loading curriculum values...</p>;
  return <CurriculumEditor onChange={onChange} value={value} vocabulary={records} />;
}

export function CurriculumEditor({
  value,
  onChange,
  vocabulary,
}: {
  value: CurriculumDraft;
  onChange: (value: CurriculumDraft) => void;
  vocabulary: AuthorVocabularyRecord[];
}) {
  const [topicSearch, setTopicSearch] = useState('');
  const [prerequisiteType, setPrerequisiteType] = useState('TOPIC');
  const [prerequisiteTarget, setPrerequisiteTarget] = useState('');
  const [prerequisiteRelationship, setPrerequisiteRelationship] = useState('RECOMMENDED');
  const [minimumEvidence, setMinimumEvidence] = useState('');
  const byType = (type: string) => vocabulary.filter(
    (item) => item.identity.vocabulary_type === type,
  );
  const available = (type: string) => byType(type).filter(
    (item) => item.availability.is_available,
  );
  const topics = useMemo(() => byType('TOPIC').filter((item) => {
    const needle = topicSearch.trim().toLocaleLowerCase();
    return !needle || [item.labels.en, item.labels.vi, ...item.aliases]
      .some((term) => term.toLocaleLowerCase().includes(needle));
  }), [topicSearch, vocabulary]);

  const identity = (type: string, code: string): CanonicalIdentity | null => (
    code ? [type, code] : null
  );
  const select = (
    label: string,
    type: string,
    selected: CanonicalIdentity | null,
    update: (next: CanonicalIdentity | null) => void,
    required = true,
  ) => (
    <label>
      <span>{label}{required && <span aria-hidden="true" className="required-star"> *</span>}</span>
      <select
        aria-label={label}
        id={`field-metadata-${label.toLowerCase().replaceAll(' ', '-')}`}
        onChange={(event) => update(identity(type, event.target.value))}
        value={selected?.[1] ?? ''}
      >
        <option value="">Select {label.toLowerCase()}</option>
        {byType(type).map((item) => (
          <option disabled={!item.availability.is_available} key={item.identity.code} value={item.identity.code}>
            [{type}] {item.labels.en}{item.availability.is_available ? '' : ' — unavailable'}
          </option>
        ))}
      </select>
    </label>
  );

  const toggleSecondary = (record: AuthorVocabularyRecord, checked: boolean) => {
    const next: CanonicalIdentity = ['COMPETENCY', record.identity.code];
    onChange({
      ...value,
      secondary_competencies: checked
        ? [...value.secondary_competencies, next].slice(0, 3)
        : value.secondary_competencies.filter((item) => item[1] !== record.identity.code),
    });
  };
  const toggleTopic = (record: AuthorVocabularyRecord, checked: boolean) => {
    const next: CanonicalIdentity = ['TOPIC', record.identity.code];
    onChange({
      ...value,
      topics: checked
        ? [...value.topics, next]
        : value.topics.filter((item) => item[1] !== record.identity.code),
    });
  };
  const prerequisiteOptions = byType(prerequisiteType);
  const canonicalPrerequisite = prerequisiteType === 'TOPIC' || prerequisiteType === 'COMPETENCY';
  const intermediateTopics = new Set(
    byType('TOPIC').flatMap((item) => item.parent_identity ? [item.parent_identity.code] : []),
  );
  const selectedIntermediateTopic = value.topics.some((topic) => intermediateTopics.has(topic[1]));
  const unavailableSelection = (
    [
      ['Pathway stage', value.stage],
      ['Task type', value.task_type],
    ] as const
  ).map(([label, selected]) => ({
    label,
    record: selected
      ? vocabulary.find((item) => item.identity.vocabulary_type === selected[0] && item.identity.code === selected[1])
      : undefined,
  })).find((item) => item.record && !item.record.availability.is_available);

  return (
    <section aria-labelledby="curriculum-heading" className="editor-section" id="curriculum">
      <h2 id="curriculum-heading">Curriculum metadata</h2>
      <p>Selections store the composite canonical identity, never the display label.</p>
      <div className="field-grid">
        {select('Pathway stage', 'PATHWAY_STAGE', value.stage, (stage) => onChange({ ...value, stage }))}
        {select('Difficulty', 'DIFFICULTY', value.difficulty, (difficulty) => onChange({ ...value, difficulty }))}
        {select('Task type', 'TASK_TYPE', value.task_type, (task_type) => onChange({ ...value, task_type }))}
        {select('Primary competency', 'COMPETENCY', value.primary_competency, (primary_competency) => onChange({ ...value, primary_competency }))}
      </div>
      {unavailableSelection?.record && <p role="alert">{unavailableSelection.record.availability.message} Select an available Release 0 {unavailableSelection.label.toLowerCase()}.</p>}

      <fieldset>
        <legend>Secondary competencies (up to three)</legend>
        <div className="selection-list secondary-competencies-list">
          {available('COMPETENCY').map((item) => {
          const checked = value.secondary_competencies.some((selected) => selected[1] === item.identity.code);
          return (
            <label className="choice-row" key={item.identity.code}>
              <input
                checked={checked}
                disabled={!checked && value.secondary_competencies.length >= 3}
                onChange={(event) => toggleSecondary(item, event.target.checked)}
                type="checkbox"
              />
              <span>[COMPETENCY] {item.labels.en} · {item.labels.vi}</span>
            </label>
          );
        })}
        </div>
        {value.secondary_competencies.length === 3 && <p>Maximum three secondary competencies selected.</p>}
      </fieldset>

      <fieldset>
        <legend>Topics</legend>
        <label><span>Search canonical topics</span><input onChange={(event) => setTopicSearch(event.target.value)} type="search" value={topicSearch} /></label>
        <div className="selection-list">
          {topics.map((item) => (
            <label className="choice-row" key={item.identity.code}>
              <input
                checked={value.topics.some((selected) => selected[1] === item.identity.code)}
                onChange={(event) => toggleTopic(item, event.target.checked)}
                type="checkbox"
              />
              <span>[TOPIC] {item.labels.en}{item.labels.vi ? ` · ${item.labels.vi}` : ''}<small>{item.breadcrumbs.map((part) => part.code).join(' / ')}</small></span>
            </label>
          ))}
        </div>
        {selectedIntermediateTopic && (
          <p className="field-guidance" role="status">A selected topic has more specific descendants. Prefer a leaf topic when it describes the problem accurately.</p>
        )}
      </fieldset>

      <fieldset>
        <legend>Typed prerequisites</legend>
        <div className="field-grid">
          <label><span>Relationship</span><select aria-label="Prerequisite relationship" onChange={(event) => setPrerequisiteRelationship(event.target.value)} value={prerequisiteRelationship}><option value="RECOMMENDED">Recommended</option><option value="REQUIRED">Required</option><option value="CO_REQUISITE">Co-requisite</option></select></label>
          <label><span>Target type</span><select aria-label="Prerequisite target type" onChange={(event) => { setPrerequisiteType(event.target.value); setPrerequisiteTarget(''); }} value={prerequisiteType}><option value="TOPIC">Topic</option><option value="COMPETENCY">Competency</option><option value="TASK">Task</option><option value="LEARNING_UNIT">Learning unit</option></select></label>
          {canonicalPrerequisite ? (
            <label><span>Target</span><select aria-label="Prerequisite target" onChange={(event) => setPrerequisiteTarget(event.target.value)} value={prerequisiteTarget}><option value="">Select canonical target</option>{prerequisiteOptions.map((item) => <option disabled={!item.availability.is_available} key={item.identity.code} value={item.identity.code}>[{prerequisiteType}] {item.labels.en}</option>)}</select></label>
          ) : (
            <label><span>Stable target ID</span><input aria-label="Prerequisite target ID" onChange={(event) => setPrerequisiteTarget(event.target.value)} value={prerequisiteTarget} /></label>
          )}
          <label><span>Minimum evidence</span><select aria-label="Minimum learning evidence" onChange={(event) => setMinimumEvidence(event.target.value)} value={minimumEvidence}><option value="">None</option><option value="INTRODUCED">Introduced</option><option value="PRACTICED">Practiced</option><option value="APPLIED">Applied</option><option value="PROFICIENT">Proficient</option></select></label>
        </div>
        <button
          disabled={!prerequisiteTarget}
          onClick={() => onChange({
            ...value,
            prerequisites: [...value.prerequisites, {
              relationship: prerequisiteRelationship,
              target_type: prerequisiteType,
              target_identity: canonicalPrerequisite ? [prerequisiteType, prerequisiteTarget] : null,
              target_id: canonicalPrerequisite ? null : prerequisiteTarget,
              minimum_evidence: minimumEvidence || null,
            }],
          })}
          type="button"
        >Add prerequisite</button>
      </fieldset>

      <Link href="/author/vocabulary/proposals">Can&apos;t find the right value?</Link>
    </section>
  );
}
