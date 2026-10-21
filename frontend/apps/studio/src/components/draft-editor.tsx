'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { Copy, Check } from 'lucide-react';

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
  ConfirmResponseTypeModal,
  emptyAssessmentDraft,
  hasCustomResponseData,
  responseTypes,
  type AssessmentDraft,
  type ResponseType,
} from './assessment-editor';
import {
  emptyResourceDraft,
  ResourceEditorLoader,
  type ResourceDraft,
} from './resource-editor';
import { ValidationPanel } from './validation-panel';
import { EditorialReviewWorkspace } from './editorial-review';

type SaveFunction = (
  revisionId: string,
  request: SaveDraftRequest,
) => Promise<AuthorDraft>;

export function DraftEditor({
  initialDraft,
  saveDraft = studioApi.saveAuthorDraft,
  reloadDraft = studioApi.getAuthorDraft,
  validateDraft = studioApi.validateAuthorDraft,
  autosaveDelay = 1200,
}: {
  initialDraft: AuthorDraft;
  saveDraft?: SaveFunction;
  reloadDraft?: (problemId: string) => Promise<AuthorDraft>;
  validateDraft?: (revisionId: string, version: number) => Promise<ValidationReport>;
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
  const [validating, setValidating] = useState(false);
  const [pendingCurriculumChange, setPendingCurriculumChange] = useState<{
    nextCurriculum: CurriculumDraft;
    targetType: ResponseType;
  } | null>(null);
  const previewing = useRef(false);
  const recoveryKey = `ioai:studio:recovery:${initialDraft.revision_id}`;
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = (key: string, text: string) => {
    void navigator.clipboard?.writeText?.(text);
    setCopiedKey(key);
    window.setTimeout(() => setCopiedKey((curr) => (curr === key ? null : curr)), 1500);
  };

  const handleValidate = async () => {
    setValidating(true);
    try {
      setValidationFailed(false);
      setValidationReport(await validateDraft(draft.revision_id, draft.version));
    } catch {
      setValidationFailed(true);
    } finally {
      setValidating(false);
    }
  };

  const handlePreview = () => {
    previewing.current = true;
    try {
      sessionStorage.setItem(`ioai:studio:preview:${draft.revision_id}`, JSON.stringify({
        expected_version: draft.version,
        unsaved_state: {
          problem_id: draft.problem_id,
          slug: request.slug,
          content: request.content,
          metadata: request.metadata,
          response: request.response,
          scoring: request.scoring,
        },
      }));
    } catch { /* Saved preview remains available without session storage. */ }
  };

  const isReadOnly = draft.editorial_status !== 'DRAFT';
  const isDirty = !isReadOnly && dirtyFields.size > 0;
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

  const [activeSection, setActiveSection] = useState<SectionId>('basics');
  const [focusMode, setFocusMode] = useState(true);

  const handleSelectSection = (sectionId: SectionId) => {
    setActiveSection(sectionId);
    const target = SECTIONS.find((s) => s.id === sectionId);
    const targetAnchor = target?.anchor ?? sectionId;
    if (typeof window !== 'undefined') {
      requestAnimationFrame(() => {
        try {
          if (focusMode) {
            const mainPanel = document.querySelector('.editor-main-panel');
            if (mainPanel && typeof mainPanel.scrollIntoView === 'function') {
              mainPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else if (typeof window.scrollTo === 'function') {
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }
          } else {
            const el = document.getElementById(targetAnchor);
            if (el && typeof el.scrollIntoView === 'function') {
              el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }
        } catch {
          // Scroll is progressive enhancement; ignored in test/headless environments
        }
      });
    }
  };

  const save = async () => {
    if (isReadOnly || previewing.current) return;
    setSaveState('saving');
    try {
      const saved = await saveDraft(draft.revision_id, request);
      setDraft(saved);
      setDirtyFields(new Set());
      setSaveState('saved');
      safeRemoveRecovery(recoveryKey);
      try {
        const report = await validateDraft(saved.revision_id, saved.version);
        setValidationReport(report);
        setValidationFailed(false);
      } catch {
        // Auto-validation is non-blocking
      }
    } catch (error) {
      safeWriteRecovery(recoveryKey, recovery);
      setSaveState('failed');
      if (error instanceof ApiError && error.code === 'REVISION_CONFLICT') setConflict(true);
    }
  };

  useEffect(() => {
    if (isReadOnly || !isDirty || saveState !== 'idle' || conflict || recoveryAvailable) return;
    const timer = window.setTimeout(() => { void save(); }, autosaveDelay);
    return () => window.clearTimeout(timer);
  }, [autosaveDelay, conflict, isDirty, isReadOnly, recoveryAvailable, request, saveState]);

  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace('#', '');
      if (!hash) return;
      if (hash.startsWith('field-slug') || hash === 'basics') handleSelectSection('basics');
      else if (hash.startsWith('field-content') || hash === 'content') handleSelectSection('content');
      else if (hash.startsWith('field-response') || hash.startsWith('scoring') || hash === 'response-scoring') handleSelectSection('assessment');
      else if (hash.startsWith('field-metadata-pathway') || hash.startsWith('field-metadata-task') || hash === 'curriculum') handleSelectSection('curriculum');
      else if (hash.startsWith('field-metadata-compute') || hash.startsWith('field-metadata-runtime') || hash.startsWith('field-metadata-expected') || hash === 'resources') handleSelectSection('resources');
      else if (hash === 'review-publish' || hash.startsWith('editorial')) handleSelectSection('review');
    };
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, [focusMode]);

  const restoreRecovery = () => {
    const stored = safeReadRecovery(recoveryKey);
    if (!stored) { setRecoveryAvailable(false); return; }
    setSlug(stored.slug); setContent(stored.content); setCurriculum(stored.curriculum);
    setSlugManuallyEdited(Boolean(stored.slug));
    setAssessment(stored.assessment); setResources(stored.resources);
    setDirtyFields(new Set(['recovered'])); setSaveState('idle'); setRecoveryAvailable(false);
  };
  const invalidateValidation = () => {
    setValidationReport(null);
    setValidationFailed(false);
  };
  const useServer = async () => {
    const current = await reloadDraft(draft.problem_id);
    safeRemoveRecovery(recoveryKey);
    setDraft(current);
    setSlug(current.slug ?? '');
    setSlugManuallyEdited(current.slug !== null);
    setContent(isContentDraft(current.content) ? current.content : emptyContentDraft());
    setCurriculum(
      isCurriculumDraft(current.metadata)
        ? curriculumFromMetadata(current.metadata)
        : emptyCurriculumDraft(),
    );
    setAssessment(
      isAssessmentDraft(current.response, current.scoring)
        ? ({ response: current.response, scoring: current.scoring, scoringValid: true } as AssessmentDraft)
        : emptyAssessmentDraft('QUIZ_SINGLE'),
    );
    setResources(
      isResourceMetadata(current.metadata)
        ? resourceFromMetadata(current.metadata)
        : emptyResourceDraft(),
    );
    setDirtyFields(new Set());
    invalidateValidation();
    setConflict(false);
    setRecoveryAvailable(false);
    setSaveState('saved');
  };
  const keepLocal = async () => {
    const current = await reloadDraft(draft.problem_id);
    setDraft(current); setConflict(false); setDirtyFields(new Set(['conflict-resolution']));
    setSaveState('idle');
  };

  const activeIndex = SECTIONS.findIndex((s) => s.id === activeSection);
  const prevSection = activeIndex > 0 ? SECTIONS[activeIndex - 1] : null;
  const nextSection = activeIndex < SECTIONS.length - 1 ? SECTIONS[activeIndex + 1] : null;

  return (
    <section aria-labelledby="editor-title" className="studio-page editor-page">
      <header className="studio-header editor-dark-header">
        <nav aria-label="Editor header" className="studio-nav">
          <div className="editor-brand-group">
            <Link href="/author/problems" className="studio-brand">
              <span className="studio-brand-title">IOAI Studio</span>
            </Link>
            <span className="editor-nav-sep" aria-hidden="true">/</span>
            <span className="problem-id-chip dark-chip">
              #{draft.problem_id.length > 8 ? `${draft.problem_id.slice(0, 8)}...` : draft.problem_id}
              <button
                type="button"
                className="copy-chip-btn dark-copy"
                onClick={() => handleCopy('header-problem-id', draft.problem_id)}
                title={copiedKey === 'header-problem-id' ? 'Copied!' : `Copy full ID: ${draft.problem_id}`}
                aria-label="Copy problem ID"
              >
                {copiedKey === 'header-problem-id' ? (
                  <Check className="copy-check-icon" size={13} aria-hidden="true" />
                ) : (
                  <Copy size={13} aria-hidden="true" />
                )}
              </button>
            </span>
            <h1 id="editor-title" className="sr-only">Edit problem</h1>
          </div>

          <div className="editor-dark-actions">
            <div aria-live="polite" className="save-status editor-save-status">
              {isReadOnly ? (
                <span className="save-state-text readonly">Read-only ({draft.editorial_status.toLowerCase().replace('_', ' ')})</span>
              ) : saveState === 'saving' ? (
                <span className="save-state-text saving">Saving...</span>
              ) : saveState === 'saved' ? (
                <span className="save-state-text saved">Saved</span>
              ) : saveState === 'failed' ? (
                <span className="save-state-text failed">Save failed</span>
              ) : isDirty ? (
                <span className="save-state-text unsaved">Unsaved changes</span>
              ) : (
                <span className="save-state-text clean">No unsaved changes</span>
              )}
            </div>
            <div className="editor-btn-group">
              <Link
                className="preview-as-learner-link dark-btn"
                href={`/author/problems/${draft.problem_id}/preview`}
                onClick={handlePreview}
              >
                Preview as learner
              </Link>
              <button
                className="save-draft-btn dark-save"
                disabled={isReadOnly || saveState === 'saving' || !isDirty}
                onClick={save}
                type="button"
              >
                Save draft
              </button>
            </div>
          </div>
        </nav>
      </header>

      <div className="editor-page-body">
        <div className="editor-meta-row">
        <div className="editor-meta-left-spacer" aria-hidden="true" />
        <div className="editor-meta-content">
          <span className="meta-rev-label">rev id:</span>
          <code className="meta-rev-code">{draft.revision_id}</code>
          <button
            type="button"
            className="copy-chip-btn"
            onClick={() => handleCopy('meta-revision-id', draft.revision_id)}
            title={copiedKey === 'meta-revision-id' ? 'Copied!' : `Copy revision ID: ${draft.revision_id}`}
            aria-label="Copy revision ID"
          >
            {copiedKey === 'meta-revision-id' ? (
              <Check className="copy-check-icon" size={13} aria-hidden="true" />
            ) : (
              <Copy size={13} aria-hidden="true" />
            )}
          </button>
          <span className="meta-divider" aria-hidden="true">·</span>
          <span className="meta-version">Version {draft.version}</span>
          <span className="meta-divider" aria-hidden="true">·</span>
          <span className={`meta-status-tag status-${draft.editorial_status.toLowerCase()}`}>
            {draft.editorial_status}
          </span>
        </div>
        <div className="editor-meta-right-spacer" aria-hidden="true" />
      </div>

      {isReadOnly && (
        <aside aria-label="Read-only revision notice" className="recovery-banner" role="status">
          <div className="recovery-banner-content">
            <div>
              <h2 className="recovery-banner-heading">Read-only revision</h2>
              <p>
                This revision is in <strong>{draft.editorial_status}</strong> status and cannot be edited.
                {draft.editorial_status === 'PUBLISHED' && ' To make changes, start a new draft revision from the problem list.'}
                {draft.editorial_status === 'ARCHIVED' && ' Archived problems can be republished by starting a new draft revision.'}
                {draft.editorial_status === 'CHANGES_REQUESTED' && ' Review the requested changes and select "Address changes" from the problem list.'}
              </p>
            </div>
          </div>
        </aside>
      )}

      {recoveryAvailable && (
        <aside aria-labelledby="recovery-title" className="recovery-banner" role="region">
          <div className="recovery-banner-content">
            <div>
              <h2 id="recovery-title" className="recovery-banner-heading">Recover unsaved draft</h2>
              <p>A local recovery copy exists for this revision. Review its target before choosing.</p>
            </div>
            <div className="recovery-banner-actions">
              <button className="recovery-restore-btn" onClick={restoreRecovery} type="button">
                Restore local copy
              </button>
              <button
                className="recovery-discard-btn"
                onClick={() => {
                  safeRemoveRecovery(recoveryKey);
                  setRecoveryAvailable(false);
                }}
                type="button"
              >
                Discard local copy
              </button>
            </div>
          </div>
        </aside>
      )}

      <div className={`editor-workspace ${focusMode ? 'focus-mode' : 'view-all-mode'}`}>
        <aside aria-label="Editor sections" className="editor-left-rail">
          <nav aria-label="Editor sections" className="editor-sections-nav">
            <div className="editor-sections-header">
              <span className="editor-sections-title">Sections</span>
              <div aria-label="Editor view mode" className="view-mode-toggle-group" role="group">
                <button
                  aria-pressed={focusMode}
                  className={`view-mode-btn ${focusMode ? 'active' : ''}`}
                  onClick={() => setFocusMode(true)}
                  title="Show one focused section at a time"
                  type="button"
                >
                  Focus
                </button>
                <button
                  aria-pressed={!focusMode}
                  className={`view-mode-btn ${!focusMode ? 'active' : ''}`}
                  onClick={() => setFocusMode(false)}
                  title="Show all sections continuously"
                  type="button"
                >
                  All
                </button>
              </div>
            </div>
            {SECTIONS.map((section) => {
              const active = activeSection === section.id;
              const errors = validationReport?.errors.filter((e) => e.section === section.reportKey).length ?? 0;
              const warnings = validationReport?.warnings.filter((w) => w.section === section.reportKey).length ?? 0;
              return (
                <button
                  className={`editor-section-tab-btn ${active ? 'active' : ''}`}
                  data-active={active ? 'true' : 'false'}
                  key={section.id}
                  onClick={() => handleSelectSection(section.id)}
                  type="button"
                >
                  <span className="section-tab-label">{section.label}</span>
                  <span className="section-tab-badge">
                    {validationReport ? (
                      errors > 0 ? (
                        <span className="tab-badge error">✖ {errors}</span>
                      ) : warnings > 0 ? (
                        <span className="tab-badge warning">⚠ {warnings}</span>
                      ) : (
                        <span className="tab-badge ok" data-testid="section-ok-badge">
                        <Check size={16} strokeWidth={2.6} aria-hidden="true" data-testid="section-check-icon" />
                      </span>
                      )
                    ) : null}
                  </span>
                </button>
              );
            })}
          </nav>
        </aside>

        <div className="editor-main-panel">
          <form onSubmit={(event) => { event.preventDefault(); void save(); }}>
            <fieldset disabled={isReadOnly} style={{ border: 'none', margin: 0, padding: 0, minWidth: 0 }}>
            <div className={`editor-section-wrap ${activeSection === 'basics' ? 'is-active' : 'is-inactive'}`}>
              <section aria-labelledby="basics-heading" className="editor-section editor-slug-panel" id="basics">
                <div className="section-panel-header">
                  <h2 id="basics-heading">Publication slug</h2>
                  <p className="section-panel-desc">
                    Configure the permanent public URL path for this problem. Generated automatically from the English title or customizable below.
                  </p>
                </div>
                <div className="editor-field slug-field-group">
                  <div className="field-label-row">
                    <label htmlFor="field-slug">URL slug</label>
                    <span className="required-star">*</span>
                  </div>
                  <div className="slug-input-prefix-wrap">
                    <span className="slug-prefix">/problems/</span>
                    <input
                      aria-label="URL slug"
                      id="field-slug"
                      className="slug-input"
                      disabled={isReadOnly}
                      onChange={(event) => {
                        const nextSlug = event.target.value;
                        setSlug(nextSlug);
                        setSlugManuallyEdited(nextSlug.trim().length > 0);
                        setDirtyFields((current) => new Set(current).add('slug'));
                        setSaveState('idle');
                        invalidateValidation();
                      }}
                      pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
                      placeholder="generated-after-title"
                      value={slug}
                    />
                  </div>
                  <p className="field-hint">
                    Permanent public route: <code>/problems/{slug || 'generated-after-title'}</code>
                  </p>
                </div>
                <div className="editor-field readonly-field-group">
                  <span className="field-subtle-label">Internal problem ID</span>
                  <div className="readonly-id-row">
                    <input aria-label="Internal problem ID" className="readonly-id-input" readOnly value={draft.problem_id} />
                    <button
                      type="button"
                      className="copy-chip-btn"
                      onClick={() => handleCopy('internal-problem-id', draft.problem_id)}
                      title={copiedKey === 'internal-problem-id' ? 'Copied!' : 'Copy internal problem ID'}
                      aria-label="Copy internal problem ID"
                    >
                      {copiedKey === 'internal-problem-id' ? (
                        <Check className="copy-check-icon" size={14} aria-hidden="true" />
                      ) : (
                        <Copy size={14} aria-hidden="true" />
                      )}
                    </button>
                  </div>
                </div>
              </section>
            </div>

            <div className={`editor-section-wrap ${activeSection === 'content' ? 'is-active' : 'is-inactive'}`}>
              <ContentEditor
                onChange={(next) => {
                  setContent(next);
                  if (!slugManuallyEdited) setSlug(slugify(next.title.en));
                  setDirtyFields((current) => new Set(current).add('content'));
                  setSaveState('idle');
                  invalidateValidation();
                }}
                value={content}
              />
            </div>

            <div className={`editor-section-wrap ${activeSection === 'assessment' ? 'is-active' : 'is-inactive'}`}>
              <AssessmentEditor
                onChange={(next) => {
                  setAssessment(next);
                  if (next.response.type !== assessment.response.type) {
                    setCurriculum((prev) => ({
                      ...prev,
                      task_type: ['TASK_TYPE', next.response.type],
                    }));
                    setDirtyFields((current) => new Set(current).add('metadata'));
                  }
                  setDirtyFields((current) => new Set(current).add('assessment'));
                  setSaveState('idle');
                  invalidateValidation();
                }}
                value={assessment}
              />
            </div>

            <div className={`editor-section-wrap ${activeSection === 'curriculum' ? 'is-active' : 'is-inactive'}`}>
              <CurriculumEditorLoader
                onChange={(next) => {
                  const nextTaskTypeCode = next.task_type?.[1];
                  const currentTaskTypeCode = curriculum.task_type?.[1];
                  if (
                    nextTaskTypeCode &&
                    nextTaskTypeCode !== currentTaskTypeCode &&
                    (responseTypes as readonly string[]).includes(nextTaskTypeCode)
                  ) {
                    const targetType = nextTaskTypeCode as ResponseType;
                    if (targetType !== assessment.response.type) {
                      if (hasCustomResponseData(assessment.response)) {
                        setPendingCurriculumChange({ nextCurriculum: next, targetType });
                        return;
                      }
                      setAssessment(emptyAssessmentDraft(targetType));
                      setDirtyFields((current) => new Set(current).add('assessment'));
                    }
                  }
                  setCurriculum(next);
                  setDirtyFields((current) => new Set(current).add('metadata'));
                  setSaveState('idle');
                  invalidateValidation();
                }}
                value={curriculum}
              />
            </div>

            <div className={`editor-section-wrap ${activeSection === 'resources' ? 'is-active' : 'is-inactive'}`}>
              <ResourceEditorLoader
                onChange={(next) => {
                  setResources(next);
                  setDirtyFields((current) => new Set(current).add('resources'));
                  setSaveState('idle');
                  invalidateValidation();
                }}
                value={resources}
              />
            </div>
            </fieldset>

            <div aria-label="Step navigation" className="editor-step-nav">
              <button
                aria-label={prevSection ? `Previous section: ${prevSection.shortLabel}` : 'Previous section'}
                className="step-nav-btn prev"
                disabled={!prevSection}
                onClick={() => prevSection && handleSelectSection(prevSection.id)}
                type="button"
              >
                {prevSection ? `← ${prevSection.shortLabel}` : '←'}
              </button>
              <span className="step-nav-indicator">
                Step {activeIndex + 1} of 6: {SECTIONS[activeIndex].shortLabel}
              </span>
              <button
                aria-label={nextSection ? `Next section: ${nextSection.shortLabel}` : 'Next section'}
                className="step-nav-btn next"
                disabled={!nextSection}
                onClick={() => nextSection && handleSelectSection(nextSection.id)}
                type="button"
              >
                {nextSection ? `${nextSection.shortLabel} →` : '→'}
              </button>
            </div>

          </form>

          <div className={`editor-section-wrap ${activeSection === 'review' ? 'is-active' : 'is-inactive'}`} id="review-publish">
            <EditorialReviewWorkspace
              dirty={isDirty}
              draft={draft}
              onDraftChange={(updated) => {
                setDraft(updated);
                setValidationReport(null);
                setValidationFailed(false);
              }}
            />
          </div>
        </div>

        <aside aria-label="Validation inspector" className="editor-right-rail">
          <ValidationPanel
            isDirty={isDirty}
            isValidating={validating}
            onValidate={handleValidate}
            report={validationReport}
            validationFailed={validationFailed}
          />
        </aside>
      </div>

      <nav aria-label="Mobile section navigation" className="editor-mobile-bottom-nav">
        <button
          aria-label={prevSection ? `Mục trước: ${prevSection.shortLabel}` : 'Mục trước'}
          className="mobile-step-btn prev"
          disabled={!prevSection}
          onClick={() => prevSection && handleSelectSection(prevSection.id)}
          type="button"
        >
          {prevSection ? `← ${prevSection.shortLabel}` : '←'}
        </button>
        <div className="mobile-step-info">
          <span className="mobile-step-text">Bước {activeIndex + 1}/6: {SECTIONS[activeIndex].shortLabel}</span>
        </div>
        <button
          aria-label={nextSection ? `Mục tiếp theo: ${nextSection.shortLabel}` : 'Mục tiếp theo'}
          className="mobile-step-btn next"
          disabled={!nextSection}
          onClick={() => nextSection && handleSelectSection(nextSection.id)}
          type="button"
        >
          {nextSection ? `${nextSection.shortLabel} →` : '→'}
        </button>
      </nav>

      {pendingCurriculumChange && (
        <ConfirmResponseTypeModal
          onCancel={() => setPendingCurriculumChange(null)}
          onConfirm={() => {
            const { nextCurriculum, targetType } = pendingCurriculumChange;
            setPendingCurriculumChange(null);
            setCurriculum(nextCurriculum);
            setAssessment(emptyAssessmentDraft(targetType));
            setDirtyFields((current) => new Set(current).add('metadata').add('assessment'));
            setSaveState('idle');
            invalidateValidation();
          }}
          pendingType={pendingCurriculumChange.targetType}
        />
      )}
      {conflict && <dialog aria-labelledby="conflict-title" open><h2 id="conflict-title">Resolve draft conflict</h2><p>The server has a newer revision. Your local recovery copy for version {draft.version} has been retained.</p><button onClick={() => { void keepLocal(); }} type="button">Keep local changes and retry</button><button onClick={() => { void useServer(); }} type="button">Use server version</button><button onClick={() => setConflict(false)} type="button">Review differences before resolving</button></dialog>}
      </div>
    </section>
  );
}

export const SECTIONS = [
  { id: 'basics', num: 1, label: '1. Basics', shortLabel: 'Basics', anchor: 'basics', reportKey: 'PUBLICATION' },
  { id: 'content', num: 2, label: '2. Content', shortLabel: 'Content', anchor: 'content', reportKey: 'CONTENT' },
  { id: 'assessment', num: 3, label: '3. Response & scoring', shortLabel: 'Assessment', anchor: 'response-scoring', reportKey: 'ASSESSMENT' },
  { id: 'curriculum', num: 4, label: '4. Curriculum', shortLabel: 'Curriculum', anchor: 'curriculum', reportKey: 'CURRICULUM' },
  { id: 'resources', num: 5, label: '5. Resources', shortLabel: 'Resources', anchor: 'resources', reportKey: 'RESOURCES' },
  { id: 'review', num: 6, label: '6. Review & publish', shortLabel: 'Review', anchor: 'review-publish', reportKey: 'PUBLICATION' },
] as const;

export type SectionId = (typeof SECTIONS)[number]['id'];

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
