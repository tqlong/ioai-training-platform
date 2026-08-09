'use client';

import { useEffect, useState } from 'react';
import type { AuthorVocabularyRecord } from '@ioai/api-client';
import { studioApi } from '../api';
import type { CanonicalIdentity } from './curriculum-editor';

export type ResourceDraft = {
  modalities: CanonicalIdentity[];
  expected_minutes: number;
  compute_tier: CanonicalIdentity;
  runtime_class: CanonicalIdentity;
  cpu_cores: number;
  ram_mb: number;
  gpu_count: number;
  gpu_vram_mb: number;
  storage_mb: number;
  runtime_seconds: number;
  network_policy: 'DENIED' | 'ALLOWED';
};

export const emptyResourceDraft = (): ResourceDraft => ({
  modalities: [['DATA_MODALITY', 'NONE']], expected_minutes: 1,
  compute_tier: ['COMPUTE_TIER', 'NONE'], runtime_class: ['RUNTIME_CLASS', 'INSTANT'],
  cpu_cores: 0, ram_mb: 0, gpu_count: 0, gpu_vram_mb: 0, storage_mb: 0,
  runtime_seconds: 0, network_policy: 'DENIED',
});

export function ResourceEditorLoader({ value, onChange }: { value: ResourceDraft; onChange: (value: ResourceDraft) => void }) {
  const [vocabulary, setVocabulary] = useState<AuthorVocabularyRecord[]>([]);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all(['DATA_MODALITY', 'COMPUTE_TIER', 'RUNTIME_CLASS'].map((vocabularyType) => studioApi.listAuthorVocabulary({ vocabularyType, limit: 500 })))
      .then((responses) => { if (active) setVocabulary(responses.flatMap((response) => response.items)); })
      .catch(() => { if (active) setFailed(true); });
    return () => { active = false; };
  }, []);
  if (failed) return <p role="alert">Resource policy values could not be loaded.</p>;
  if (!vocabulary.length) return <p aria-live="polite">Loading resource policy…</p>;
  return <ResourceEditor onChange={onChange} value={value} vocabulary={vocabulary} />;
}

const duration = (minutes: number) => minutes <= 10 ? 'MICRO' : minutes <= 30 ? 'SHORT' : minutes <= 60 ? 'STANDARD' : minutes <= 180 ? 'EXTENDED' : minutes <= 480 ? 'LONG' : 'PROJECT';

export function ResourceEditor({ value, onChange, vocabulary }: { value: ResourceDraft; onChange: (value: ResourceDraft) => void; vocabulary: AuthorVocabularyRecord[] }) {
  const byType = (type: string) => vocabulary.filter((item) => item.identity.vocabulary_type === type);
  const selectedCompute = byType('COMPUTE_TIER').find((item) => item.identity.code === value.compute_tier[1]);
  const selectedRuntime = byType('RUNTIME_CLASS').find((item) => item.identity.code === value.runtime_class[1]);
  const toggleModality = (code: string, checked: boolean) => {
    const current = value.modalities.map((identity) => identity[1]);
    const next = checked
      ? code === 'NONE' ? ['NONE'] : [...current.filter((item) => item !== 'NONE'), code]
      : current.filter((item) => item !== code);
    onChange({ ...value, modalities: next.map((item) => ['DATA_MODALITY', item]) });
  };
  const numeric = (field: keyof ResourceDraft, raw: string) => onChange({ ...value, [field]: Number(raw) });
  return <section aria-labelledby="resources-heading" className="editor-section" id="resources">
    <h2 id="resources-heading">Resources &amp; Release 0 policy</h2>
    <label><span>Expected minutes</span><input aria-label="Expected minutes" min="1" onChange={(event) => numeric('expected_minutes', event.target.value)} required type="number" value={value.expected_minutes} /></label>
    <p>Derived duration: {duration(value.expected_minutes)}</p>
    <fieldset><legend>Data modalities</legend>{byType('DATA_MODALITY').map((item) => <label className="choice-row" key={item.identity.code}><input checked={value.modalities.some((selected) => selected[1] === item.identity.code)} disabled={!item.availability.is_available} onChange={(event) => toggleModality(item.identity.code, event.target.checked)} type="checkbox" /><span>{item.labels.en} [{item.identity.code}]</span></label>)}{!value.modalities.length && <p role="alert">Select at least one data modality.</p>}</fieldset>
    <div className="field-grid">
      <CanonicalSelect label="Compute tier" records={byType('COMPUTE_TIER')} selected={value.compute_tier} update={(compute_tier) => onChange({ ...value, compute_tier })} />
      <CanonicalSelect label="Runtime class" records={byType('RUNTIME_CLASS')} selected={value.runtime_class} update={(runtime_class) => onChange({ ...value, runtime_class })} />
      {(['cpu_cores', 'ram_mb', 'gpu_count', 'gpu_vram_mb', 'storage_mb', 'runtime_seconds'] as const).map((field) => <label key={field}><span>{field.replaceAll('_', ' ')}</span><input aria-label={field.replaceAll('_', ' ')} min="0" onChange={(event) => numeric(field, event.target.value)} type="number" value={value[field]} /></label>)}
      <label><span>Network policy</span><select aria-label="Network policy" onChange={(event) => onChange({ ...value, network_policy: event.target.value as ResourceDraft['network_policy'] })} value={value.network_policy}><option value="DENIED">Denied</option><option value="ALLOWED">Allowed</option></select></label>
    </div>
    {selectedCompute && !selectedCompute.availability.is_available && <p role="alert">{selectedCompute.availability.message} Select NONE, BROWSER, or CPU_LIGHT.</p>}
    {selectedRuntime && !selectedRuntime.availability.is_available && <p role="alert">{selectedRuntime.availability.message}</p>}
    {value.network_policy === 'ALLOWED' && <p role="alert">Network access is unavailable for Release 0 assessment. Select Denied.</p>}
    {value.gpu_count === 0 && value.gpu_vram_mb > 0 && <p role="alert">GPU VRAM requires a positive GPU count.</p>}
  </section>;
}

function CanonicalSelect({ label, records, selected, update }: { label: string; records: AuthorVocabularyRecord[]; selected: CanonicalIdentity; update: (identity: CanonicalIdentity) => void }) {
  return <label><span>{label}</span><select aria-label={label} onChange={(event) => update([records[0]?.identity.vocabulary_type ?? '', event.target.value])} value={selected[1]}>{records.map((item) => <option disabled={!item.availability.is_available && item.identity.code !== selected[1]} key={item.identity.code} value={item.identity.code}>{item.labels.en}{item.availability.is_available ? '' : ' — unavailable'}</option>)}</select></label>;
}
