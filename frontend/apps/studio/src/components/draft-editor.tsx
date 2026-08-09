'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

import { ApiError, type AuthorDraft, type SaveDraftRequest, type ValidationReport } from '@ioai/api-client';

import { studioApi } from '../api';
import {
  ContentEditor,
  emptyContentDraft,
  type ContentDraft,
} from './content-editor';
import {
  CurriculumEditorLoader,
  emptyCurriculumDraft,
  type CurriculumDraft,
} from './curriculum-editor';
import {
  AssessmentEditor,
  emptyAssessmentDraft,
  type AssessmentDraft,
  type ResponseType,
} from './assessment-editor';
import {
  emptyResourceDraft,
  ResourceEditorLoader,
  type ResourceDraft,
} from './resource-editor';
import { ValidationPanel } from './validation-panel';

type SaveFunction = (
  revisionId: string,
  request: SaveDraftRequest,
) => Promise<AuthorDraft>;

export function DraftEditor({
  initialDraft,
  saveDraft = studioApi.saveAuthorDraft,
  reloadDraft = studioApi.getAuthorDraft,
  autosaveDelay = 1200,
}: {
  initialDraft: AuthorDraft;
  saveDraft?: SaveFunction;
  reloadDraft?: (problemId: string) => Promise<AuthorDraft>;
  autosaveDelay?: number;
}) {
  const initialAutoSlug = initialDraft.slug === null && isContentDraft(initialDraft.content)
    ? slugify(initialDraft.content.title.en)
    : '';
  const [draft, setDraft] = useState(initialDraft);
  const [slug, setSlug] = useState(initialDraft.slug ?? initialAutoSlug);
  const [slugManuallyEdited, setSlugManuallyEdited] = useState(initialDraft.slug !== null);
  const [content, setContent] = useState<ContentDraft>(() => (
    isContentDraft(initialDraft.content) ? initialDraft.content : emptyContentDraft()
  ));
  const [curriculum, setCurriculum] = useState<CurriculumDraft>(() => (
    isCurriculumDraft(initialDraft.metadata)
      ? curriculumFromMetadata(initialDraft.metadata)
      : emptyCurriculumDraft()
  ));
  const [assessment, setAssessment] = useState<AssessmentDraft>(() => (
    isAssessmentDraft(initialDraft.response, initialDraft.scoring)
      ? { response: initialDraft.response, scoring: initialDraft.scoring, scoringValid: true } as AssessmentDraft
      : emptyAssessmentDraft('QUIZ_SINGLE')
  ));
  const [resources, setResources] = useState<ResourceDraft>(() => (
    isResourceMetadata(initialDraft.metadata)
      ? resourceFromMetadata(initialDraft.metadata)
      : emptyResourceDraft()
  ));
  const [dirtyFields, setDirtyFields] = useState<Set<string>>(
    () => new Set(initialAutoSlug ? ['slug'] : []),
  );
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');
  const [conflict, setConflict] = useState(false);
  const [recoveryAvailable, setRecoveryAvailable] = useState(false);
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [validationFailed, setValidationFailed] = useState(false);
  const recoveryKey = `ioai:studio:recovery:${initialDraft.revision_id}`;

  const isDirty = dirtyFields.size > 0;
  useEffect(() => {
    const protectUnsaved = (event: BeforeUnloadEvent) => {
      if (!isDirty) return;
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', protectUnsaved);
    return () => window.removeEventListener('beforeunload', protectUnsaved);
  }, [isDirty]);

  const request = useMemo<SaveDraftRequest>(() => ({
    problem_id: draft.problem_id,
    expected_version: draft.version,
    client_save_key: globalThis.crypto?.randomUUID?.() ?? `save-${draft.version}`,
    slug: slug || null,
    content,
    metadata: curriculumMetadata(curriculum, resources) ?? draft.metadata,
    response: assessment.response,
    scoring: assessment.scoring,
  }), [assessment, content, curriculum, draft, resources, slug]);

  const recovery = useMemo(() => ({
    schemaVersion: 1 as const, problemId: draft.problem_id, revisionId: draft.revision_id,
    serverVersion: draft.version, slug, content, curriculum, assessment, resources,
  }), [assessment, content, curriculum, draft, resources, slug]);

  useEffect(() => {
    const stored = safeReadRecovery(recoveryKey);
    if (stored && stored.problemId === initialDraft.problem_id && stored.revisionId === initialDraft.revision_id) {
      setRecoveryAvailable(true);
    }
  }, [initialDraft.problem_id, initialDraft.revision_id, recoveryKey]);

  const save = async () => {
    setSaveState('saving');
    try {
      const saved = await saveDraft(draft.revision_id, request);
      setDraft(saved);
      setDirtyFields(new Set());
      setSaveState('saved');
      safeRemoveRecovery(recoveryKey);
    } catch (error) {
      safeWriteRecovery(recoveryKey, recovery);
      setSaveState('failed');
      if (error instanceof ApiError && error.code === 'REVISION_CONFLICT') setConflict(true);
    }
  };

  useEffect(() => {
    if (!isDirty || saveState !== 'idle' || conflict || recoveryAvailable) return;
    const timer = window.setTimeout(() => { void save(); }, autosaveDelay);
    return () => window.clearTimeout(timer);
  }, [autosaveDelay, conflict, isDirty, recoveryAvailable, request, saveState]);

  const restoreRecovery = () => {
    const stored = safeReadRecovery(recoveryKey);
    if (!stored) { setRecoveryAvailable(false); return; }
    setSlug(stored.slug); setContent(stored.content); setCurriculum(stored.curriculum);
    setSlugManuallyEdited(Boolean(stored.slug));
    setAssessment(stored.assessment); setResources(stored.resources);
    setDirtyFields(new Set(['recovered'])); setSaveState('idle'); setRecoveryAvailable(false);
  };
  const useServer = async () => {
    const current = await reloadDraft(draft.problem_id);
    safeRemoveRecovery(recoveryKey);
    setDraft(current); setSlug(current.slug ?? ''); setDirtyFields(new Set());
    setSlugManuallyEdited(current.slug !== null);
    setConflict(false); setRecoveryAvailable(false); setSaveState('saved');
  };
  const keepLocal = async () => {
    const current = await reloadDraft(draft.problem_id);
    setDraft(current); setConflict(false); setDirtyFields(new Set(['conflict-resolution']));
    setSaveState('idle');
  };

  return (
    <section aria-labelledby="editor-title" className="studio-page editor-page">
      <div className="editor-topbar">
        <div>
          <p className="eyebrow">Structured draft · {draft.editorial_status}</p>
          <h1 id="editor-title">Edit problem</h1>
          <p><code>{draft.revision_id}</code> · <span>Version {draft.version}</span></p>
        </div>
        <div aria-live="polite" className="save-status">
          {saveState === 'saving' && 'Saving...'}
          {saveState === 'saved' && 'Saved'}
          {saveState === 'failed' && 'Save failed'}
          {saveState === 'idle' && (isDirty ? 'Unsaved changes' : 'No unsaved changes')}
        </div>
      </div>

      <nav aria-label="Editor sections" className="editor-sections">
        {['Basics', 'Content', 'Curriculum', 'Response & scoring', 'Resources'].map((label) => (
          <a href={`#${label.toLowerCase().replaceAll(/[^a-z]+/g, '-')}`} key={label}>{label}</a>
        ))}
      </nav>

      <form onSubmit={(event) => { event.preventDefault(); void save(); }}>
        <section aria-labelledby="basics-heading" className="editor-section" id="basics">
          <h2 id="basics-heading">Basics</h2>
          <label>
            <span>Internal problem ID</span>
            <input readOnly value={draft.problem_id} />
          </label>
          <label>
            <span>URL slug</span>
            <input
              aria-label="URL slug"
              id="field-slug"
              onChange={(event) => {
                setSlug(event.target.value);
                setSlugManuallyEdited(true);
                setDirtyFields((current) => new Set(current).add('slug'));
                setSaveState('idle');
              }}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              placeholder="generated-after-title"
              value={slug}
            />
          </label>
        </section>

        <ContentEditor
          onChange={(next) => {
            setContent(next);
            if (!slugManuallyEdited) setSlug(slugify(next.title.en));
            setDirtyFields((current) => new Set(current).add('content'));
            setSaveState('idle');
          }}
          value={content}
        />

        <CurriculumEditorLoader
          onChange={(next) => {
            setCurriculum(next);
            setDirtyFields((current) => new Set(current).add('metadata'));
            setSaveState('idle');
          }}
          value={curriculum}
        />

        <AssessmentEditor
          onChange={(next) => {
            setAssessment(next);
            setDirtyFields((current) => new Set(current).add('assessment'));
            setSaveState('idle');
          }}
          value={assessment}
        />

        <ResourceEditorLoader
          onChange={(next) => {
            setResources(next);
            setDirtyFields((current) => new Set(current).add('resources'));
            setSaveState('idle');
          }}
          value={resources}
        />

        <div className="editor-actions">
          <button disabled={!isDirty || saveState === 'saving'} type="submit">Save draft</button>
          <button disabled={isDirty} onClick={async () => { try { setValidationFailed(false); setValidationReport(await studioApi.validateAuthorDraft(draft.revision_id, draft.version)); } catch { setValidationFailed(true); } }} title={isDirty ? 'Save the current changes before validation.' : undefined} type="button">Validate draft</button>
          <Link href={`/author/problems/${draft.problem_id}/preview`}>Preview as learner</Link>
        </div>
      </form>
      {validationFailed && <p role="alert">Validation could not be completed for the current saved version.</p>}
      {validationReport && <ValidationPanel report={validationReport} />}
      {recoveryAvailable && <dialog aria-labelledby="recovery-title" open><h2 id="recovery-title">Recover unsaved draft</h2><p>A local recovery copy exists for this revision. Review its target before choosing.</p><button onClick={restoreRecovery} type="button">Restore local copy</button><button onClick={() => { safeRemoveRecovery(recoveryKey); setRecoveryAvailable(false); }} type="button">Discard local copy</button></dialog>}
      {conflict && <dialog aria-labelledby="conflict-title" open><h2 id="conflict-title">Resolve draft conflict</h2><p>The server has a newer revision. Your local recovery copy for version {draft.version} has been retained.</p><button onClick={() => { void keepLocal(); }} type="button">Keep local changes and retry</button><button onClick={() => { void useServer(); }} type="button">Use server version</button><button onClick={() => setConflict(false)} type="button">Review differences before resolving</button></dialog>}
    </section>
  );
}

const isContentDraft = (value: unknown): value is ContentDraft => (
  typeof value === 'object' && value !== null && 'title' in value && 'blocks' in value
);

const slugify = (title: string): string => title
  .normalize('NFKD')
  .replace(/[đĐ]/g, 'd')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '')
  .slice(0, 120)
  .replace(/-+$/g, '');

const isCurriculumDraft = (value: unknown): value is Record<string, unknown> => (
  typeof value === 'object' && value !== null && 'stage' in value
);

const isAssessmentDraft = (
  response: unknown,
  scoring: unknown,
): response is Record<string, unknown> & { type: ResponseType } => (
  typeof response === 'object' && response !== null && 'type' in response &&
  typeof scoring === 'object' && scoring !== null && 'components' in scoring
);

const curriculumFromMetadata = (value: Record<string, unknown>): CurriculumDraft => ({
  stage: (value.stage as CurriculumDraft['stage']) ?? null,
  difficulty: (value.difficulty as CurriculumDraft['difficulty']) ?? null,
  primary_competency: (value.primary_competency as CurriculumDraft['primary_competency']) ?? null,
  secondary_competencies: (value.secondary_competencies as CurriculumDraft['secondary_competencies']) ?? [],
  task_type: (value.task_type as CurriculumDraft['task_type']) ?? null,
  topics: (value.topics as CurriculumDraft['topics']) ?? [],
  prerequisites: (value.prerequisites as CurriculumDraft['prerequisites']) ?? [],
});

const curriculumMetadata = (value: CurriculumDraft, resources: ResourceDraft): Record<string, unknown> | null => {
  if (!value.stage || !value.difficulty || !value.primary_competency || !value.task_type || value.topics.length === 0) return null;
  return {
    ...value,
    modalities: resources.modalities,
    expected_minutes: resources.expected_minutes,
    resources: {
      compute_tier: resources.compute_tier,
      runtime_class: resources.runtime_class,
      cpu_cores: resources.cpu_cores,
      ram_mb: resources.ram_mb,
      gpu_count: resources.gpu_count,
      gpu_vram_mb: resources.gpu_vram_mb,
      storage_mb: resources.storage_mb,
      runtime_seconds: resources.runtime_seconds,
      network_policy: resources.network_policy,
    },
  };
};

type RecoveryRecord = {
  schemaVersion: 1; problemId: string; revisionId: string; serverVersion: number;
  slug: string; content: ContentDraft; curriculum: CurriculumDraft;
  assessment: AssessmentDraft; resources: ResourceDraft;
};

const safeReadRecovery = (key: string): RecoveryRecord | null => {
  try {
    const parsed: unknown = JSON.parse(window.localStorage.getItem(key) ?? 'null');
    if (typeof parsed !== 'object' || parsed === null || !('schemaVersion' in parsed) || parsed.schemaVersion !== 1) return null;
    return parsed as RecoveryRecord;
  } catch { return null; }
};
const safeWriteRecovery = (key: string, value: RecoveryRecord) => {
  try { window.localStorage.setItem(key, JSON.stringify(value)); } catch { /* Recovery is best effort; the editor remains usable. */ }
};
const safeRemoveRecovery = (key: string) => {
  try { window.localStorage.removeItem(key); } catch { /* Storage may be unavailable. */ }
};

const isResourceMetadata = (value: unknown): value is Record<string, unknown> => (
  typeof value === 'object' && value !== null && 'resources' in value && 'modalities' in value
);

const resourceFromMetadata = (value: Record<string, unknown>): ResourceDraft => {
  const limits = value.resources as Record<string, unknown>;
  return {
    modalities: value.modalities as ResourceDraft['modalities'],
    expected_minutes: Number(value.expected_minutes),
    compute_tier: limits.compute_tier as ResourceDraft['compute_tier'],
    runtime_class: limits.runtime_class as ResourceDraft['runtime_class'],
    cpu_cores: Number(limits.cpu_cores), ram_mb: Number(limits.ram_mb),
    gpu_count: Number(limits.gpu_count), gpu_vram_mb: Number(limits.gpu_vram_mb),
    storage_mb: Number(limits.storage_mb), runtime_seconds: Number(limits.runtime_seconds),
    network_policy: limits.network_policy as ResourceDraft['network_policy'],
  };
};
