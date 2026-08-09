import { render, screen } from '@testing-library/react';
import type { ValidationReport } from '@ioai/api-client';

import { ValidationPanel } from '../src/components/validation-panel';

const report: ValidationReport = {
  revision_id: 'revision-1', revision_version: 2, publication_eligible: false,
  errors: [{ code: 'REQUIRED_CONTENT_MISSING', section: 'CONTENT', field_path: 'content.title.en', message: 'Complete the English title.', severity: 'ERROR' }],
  warnings: [{ code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.title.vi', message: 'Translation pending.', severity: 'WARNING' }],
};

describe('draft validation panel', () => {
  it('groups all five layers, distinguishes warnings, and focuses the first blocker', () => {
    render(<ValidationPanel report={report} />);
    for (const section of ['Content', 'Curriculum', 'Assessment', 'Resources', 'Publication']) expect(screen.getByRole('heading', { name: section })).toBeTruthy();
    const blocker = screen.getByRole('link', { name: /Complete the English title/ });
    expect(document.activeElement).toBe(blocker);
    expect(blocker.getAttribute('href')).toBe('#field-content-title-en');
    expect(screen.getByText('Translation pending.').closest('[data-severity]')?.getAttribute('data-severity')).toBe('WARNING');
    expect(screen.getByRole('heading', { name: 'Errors (1)' })).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Warnings (1)' })).toBeTruthy();
    expect(screen.getByText('Error:', { exact: true })).toBeTruthy();
    expect(screen.getByText('Warning:', { exact: true })).toBeTruthy();
    expect(screen.getByText('Not eligible for publication')).toBeTruthy();
  });
});
