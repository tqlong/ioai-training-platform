'use client';

import { useEffect, useRef } from 'react';
import type { RefObject } from 'react';
import type { ValidationReport } from '@ioai/api-client';

const sections = ['CONTENT', 'CURRICULUM', 'ASSESSMENT', 'RESOURCES', 'PUBLICATION'] as const;
const anchors: Record<string, string> = {
  CONTENT: 'content', CURRICULUM: 'curriculum', ASSESSMENT: 'response-scoring',
  RESOURCES: 'resources', PUBLICATION: 'basics',
};

const issueTarget = (section: string, path: string): string => {
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

export function ValidationPanel({ report }: { report: ValidationReport }) {
  const firstBlocker = useRef<HTMLAnchorElement>(null);
  useEffect(() => { firstBlocker.current?.focus(); }, [report]);
  return <aside aria-labelledby="validation-heading" className="validation-panel">
    <h2 id="validation-heading">Draft validation</h2>
    <p className="validation-eligibility">{report.publication_eligible ? 'Eligible for publication' : 'Not eligible for publication'}</p>
    {sections.map((section) => {
      const errors = report.errors.filter((issue) => issue.section === section);
      const warnings = report.warnings.filter((issue) => issue.section === section);
      return <section aria-labelledby={`validation-${section}`} key={section}>
        <h3 id={`validation-${section}`}>{section[0]}{section.slice(1).toLowerCase()}</h3>
        {errors.length === 0 && warnings.length === 0 ? <p>No issues.</p> : <>
          {errors.length > 0 && <IssueGroup heading={`Errors (${errors.length})`} issues={errors} section={section} firstBlocker={firstBlocker} firstError={report.errors[0]} />}
          {warnings.length > 0 && <IssueGroup heading={`Warnings (${warnings.length})`} issues={warnings} section={section} firstBlocker={firstBlocker} firstError={report.errors[0]} />}
        </>}
      </section>;
    })}
  </aside>;
}

function IssueGroup({ heading, issues, section, firstBlocker, firstError }: {
  heading: string;
  issues: ValidationReport['errors'];
  section: string;
  firstBlocker: RefObject<HTMLAnchorElement>;
  firstError: ValidationReport['errors'][number] | undefined;
}) {
  return <div className="validation-issue-group">
    <h4>{heading}</h4>
    <ul>{issues.map((issue) => {
      const first = issue === firstError;
      const error = issue.severity === 'ERROR';
      return <li data-severity={issue.severity} key={`${issue.code}-${issue.field_path}`}><a href={`#${issueTarget(section, issue.field_path)}`} ref={first ? firstBlocker : undefined}><span aria-hidden="true" className="severity-icon">{error ? '✖' : '⚠'}</span> <span className="severity-label">{error ? 'Error:' : 'Warning:'}</span> {issue.message} <span className="validation-path">({issue.field_path})</span></a></li>;
    })}</ul>
  </div>;
}
