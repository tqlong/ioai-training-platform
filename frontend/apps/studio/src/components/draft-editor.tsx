'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

import type { AuthorDraft, SaveDraftRequest } from '@ioai/api-client';

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

type SaveFunction = (
  revisionId: string,
  request: SaveDraftRequest,
) => Promise<AuthorDraft>;

export function DraftEditor({
  initialDraft,
  saveDraft = studioApi.saveAuthorDraft,
}: {
  initialDraft: AuthorDraft;
  saveDraft?: SaveFunction;
}) {
  const [draft, setDraft] = useState(initialDraft);
  const [slug, setSlug] = useState(initialDraft.slug ?? '');
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
  const [dirtyFields, setDirtyFields] = useState<Set<string>>(new Set());
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');

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

  const save = async () => {
    setSaveState('saving');
    try {
      const saved = await saveDraft(draft.revision_id, request);
      setDraft(saved);
      setDirtyFields(new Set());
      setSaveState('saved');
    } catch {
      setSaveState('failed');
    }
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
              onChange={(event) => {
                setSlug(event.target.value);
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
          <button type="button">Validate draft</button>
          <Link href={`/author/problems/${draft.problem_id}/preview`}>Preview as learner</Link>
        </div>
      </form>
    </section>
  );
}

const isContentDraft = (value: unknown): value is ContentDraft => (
  typeof value === 'object' && value !== null && 'title' in value && 'blocks' in value
);

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
