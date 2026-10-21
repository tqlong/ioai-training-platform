'use client';

import { useEffect, useRef, useState } from 'react';
import type { RefObject } from 'react';
import { RotateCw } from 'lucide-react';
import type { ValidationReport } from '@ioai/api-client';

const sections = ['CONTENT', 'CURRICULUM', 'ASSESSMENT', 'RESOURCES', 'PUBLICATION'] as const;
const anchors: Record<string, string> = {
  CONTENT: 'content', CURRICULUM: 'curriculum', ASSESSMENT: 'response-scoring',
  RESOURCES: 'resources', PUBLICATION: 'basics',
};

export const issueTarget = (section: string, path: string): string => {
  const exact: Record<string, string> = {
    slug: 'field-slug',
    'content.title.en': 'field-content-title-en',
    'content.title.vi': 'field-content-title-vi',
    'content.summary.en': 'field-content-summary-en',
    'content.summary.vi': 'field-content-summary-vi',
    'response.response_type': 'field-response-response-type',
    'scoring.response_type': 'response-scoring',
    'metadata.expected_minutes': 'field-metadata-expected-minutes',
    'metadata.stage': 'field-metadata-pathway-stage',
    'metadata.task_type': 'field-metadata-task-type',
    'metadata.resources.compute_tier': 'field-metadata-compute-tier',
    'metadata.resources.runtime_class': 'field-metadata-runtime-class',
  };
  if (exact[path]) return exact[path];
  if (/^content\.objectives\.0\.en$/.test(path)) return 'field-content-learning-objective-en';
  return anchors[section];
};

export function ValidationPanel({
  report,
  onValidate,
  isValidating = false,
  isDirty = false,
  validationFailed = false,
}: {
  report: ValidationReport | null;
  onValidate?: () => void;
  isValidating?: boolean;
  isDirty?: boolean;
  validationFailed?: boolean;
}) {
  const firstBlocker = useRef<HTMLAnchorElement>(null);
  const [severityFilter, setSeverityFilter] = useState<'ALL' | 'ERROR' | 'WARNING'>('ALL');

  useEffect(() => {
    if (!report) return;
    const marked = report.errors.flatMap((issue) => {
      const element = document.getElementById(issueTarget(issue.section, issue.field_path));
      if (!(element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement || element instanceof HTMLSelectElement)) return [];
      element.setAttribute('aria-invalid', 'true');
      element.classList.add('field-has-error');
      return [element];
    });
    firstBlocker.current?.focus();
    return () => marked.forEach((element) => {
      element.removeAttribute('aria-invalid');
      element.classList.remove('field-has-error');
    });
  }, [report]);

  if (!report) {
    return (
      <aside aria-label="Draft validation" className="validation-panel validation-panel-empty">
        <div className="validation-panel-header">
          <div className="validation-title-block">
            <span className="validation-title">Draft validation</span>
            <p className="validation-eligibility validation-pending">Not validated yet</p>
          </div>
        </div>
        <div className="validation-empty-card">
          <p className="validation-empty-title">Ready for inspection</p>
          <p className="validation-empty-text">
            No validation report yet. Click <strong>Validate draft</strong> to inspect publication requirements, required fields, and schema invariants.
          </p>
          {onValidate && (
            <button
              className="validate-draft-btn primary-action"
              disabled={isDirty || isValidating}
              onClick={onValidate}
              title={isDirty ? 'Save the current changes before validation.' : undefined}
              type="button"
            >
              {isValidating ? 'Validating...' : 'Validate draft'}
            </button>
          )}
          {isDirty && (
            <p className="validation-dirty-hint">
              Save draft changes to enable validation.
            </p>
          )}
          {validationFailed && (
            <p className="validation-failed-alert" role="alert">
              Validation could not be completed for the current saved version.
            </p>
          )}
        </div>
      </aside>
    );
  }

  const totalErrors = report.errors.length;
  const totalWarnings = report.warnings.length;
  const totalIssues = totalErrors + totalWarnings;

  return (
    <aside aria-labelledby="validation-heading" className="validation-panel">
      <div className="validation-panel-header">
        <div className="validation-heading-row">
          <div className="validation-title-block">
            <h2 id="validation-heading">Draft validation</h2>
            <p className={`validation-eligibility ${report.publication_eligible ? "eligible" : "not-eligible"}`}>
              {report.publication_eligible ? 'Eligible for publication' : 'Not eligible for publication'}
            </p>
          </div>
          {onValidate && (
            <button
              aria-label="Re-validate draft"
              className="validate-reload-btn"
              disabled={isDirty || isValidating}
              onClick={onValidate}
              title={isDirty ? 'Save draft changes before re-validating' : 'Re-validate draft'}
              type="button"
            >
              <RotateCw className={`reload-icon ${isValidating ? 'spin' : ''}`} size={32} strokeWidth={2.4} aria-hidden="true" />
            </button>
          )}
        </div>
        <div aria-label="Filter validation issues by severity" className="validation-filter-tabs" role="tablist">
          <button
            aria-selected={severityFilter === 'ALL'}
            className={`validation-filter-btn ${severityFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('ALL')}
            role="tab"
            type="button"
          >
            All ({totalIssues})
          </button>
          <button
            aria-selected={severityFilter === 'ERROR'}
            className={`validation-filter-btn filter-error ${severityFilter === 'ERROR' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('ERROR')}
            role="tab"
            type="button"
          >
            Errors ({totalErrors})
          </button>
          <button
            aria-selected={severityFilter === 'WARNING'}
            className={`validation-filter-btn filter-warning ${severityFilter === 'WARNING' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('WARNING')}
            role="tab"
            type="button"
          >
            Warnings ({totalWarnings})
          </button>
        </div>
      </div>
      {isDirty && (
        <p className="validation-dirty-hint">
          Save draft changes to re-validate.
        </p>
      )}
      {validationFailed && (
        <p className="validation-failed-alert" role="alert">
          Validation could not be completed for the current saved version.
        </p>
      )}

      <div className="validation-panel-body">
        {sections.map((section) => {
          const errors = severityFilter === 'WARNING'
            ? []
            : report.errors.filter((issue) => issue.section === section);
          const warnings = severityFilter === 'ERROR'
            ? []
            : report.warnings.filter((issue) => issue.section === section);

          const hasIssues = errors.length > 0 || warnings.length > 0;
          const noIssuesAtAll = report.errors.filter((i) => i.section === section).length === 0 &&
                                report.warnings.filter((i) => i.section === section).length === 0;

          return (
            <section aria-labelledby={`validation-${section}`} className="validation-section" key={section}>
              <h3 id={`validation-${section}`}>{section[0]}{section.slice(1).toLowerCase()}</h3>
              {noIssuesAtAll ? (
                <p className="validation-no-issues">No issues.</p>
              ) : !hasIssues ? (
                <p className="validation-no-issues">No matching issues for the selected filter.</p>
              ) : (
                <>
                  {errors.length > 0 && (
                    <IssueGroup
                      firstBlocker={firstBlocker}
                      firstError={report.errors[0]}
                      heading={`Errors (${errors.length})`}
                      issues={errors}
                      section={section}
                    />
                  )}
                  {warnings.length > 0 && (
                    <IssueGroup
                      firstBlocker={firstBlocker}
                      firstError={report.errors[0]}
                      heading={`Warnings (${warnings.length})`}
                      issues={warnings}
                      section={section}
                    />
                  )}
                </>
              )}
            </section>
          );
        })}
      </div>
    </aside>
  );
}

function IssueGroup({ heading, issues, section, firstBlocker, firstError }: {
  heading: string;
  issues: ValidationReport['errors'];
  section: string;
  firstBlocker: RefObject<HTMLAnchorElement>;
  firstError: ValidationReport['errors'][number] | undefined;
}) {
  // Group issues by (code, message) to aggregate repetitive occurrences
  const groupedIssues = issues.reduce((acc, issue) => {
    const key = `${issue.code}:::${issue.message}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(issue);
    return acc;
  }, {} as Record<string, ValidationReport['errors']>);

  return (
    <div className="validation-issue-group">
      <h4>{heading}</h4>
      <ul>
        {Object.entries(groupedIssues).map(([key, group]) => {
          const firstItem = group[0];
          const isError = firstItem.severity === 'ERROR';

          if (group.length === 1) {
            const issue = firstItem;
            const isFirst = issue === firstError;
            return (
              <li data-severity={issue.severity} key={`${issue.code}-${issue.field_path}`}>
                <a href={`#${issueTarget(section, issue.field_path)}`} ref={isFirst ? firstBlocker : undefined}>
                  <span aria-hidden="true" className="severity-icon">{isError ? '✖' : '⚠'}</span>{' '}
                  <span className="severity-label">{isError ? 'Error:' : 'Warning:'}</span> {issue.message}{' '}
                  <span className="validation-path">({issue.field_path})</span>
                </a>
              </li>
            );
          }

          return (
            <li className="validation-issue-aggregated" data-severity={firstItem.severity} key={key}>
              <details className="validation-aggregated-details" open>
                <summary className="validation-aggregated-summary">
                  <span aria-hidden="true" className="severity-icon">{isError ? '✖' : '⚠'}</span>{' '}
                  <span className="severity-label">{isError ? 'Error:' : 'Warning:'}</span>{' '}
                  <span className="aggregated-message">{firstItem.message}</span>{' '}
                  <span className="aggregated-count">({group.length} fields)</span>
                </summary>
                <ul className="aggregated-paths-list">
                  {group.map((item) => {
                    const isFirst = item === firstError;
                    return (
                      <li key={item.field_path}>
                        <a href={`#${issueTarget(section, item.field_path)}`} ref={isFirst ? firstBlocker : undefined}>
                          <span className="validation-path">({item.field_path})</span>
                        </a>
                      </li>
                    );
                  })}
                </ul>
              </details>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
