import { fireEvent, render, screen } from '@testing-library/react';
import type { ValidationReport } from '@ioai/api-client';

import { ValidationPanel } from '../src/components/validation-panel';

const report: ValidationReport = {
  revision_id: 'revision-1', revision_version: 2, publication_eligible: false,
  errors: [{ code: 'REQUIRED_CONTENT_MISSING', section: 'CONTENT', field_path: 'content.title.en', message: 'Complete the English title.', severity: 'ERROR' }],
  warnings: [{ code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.title.vi', message: 'Translation pending.', severity: 'WARNING' }],
};

describe('draft validation panel', () => {
  it('groups all five layers, distinguishes warnings, and focuses the first blocker', () => {
    const title = document.createElement('input');
    title.id = 'field-content-title-en';
    document.body.append(title);
    const { unmount } = render(<ValidationPanel report={report} />);
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
    expect(title.getAttribute('aria-invalid')).toBe('true');
    expect(title.classList.contains('field-has-error')).toBe(true);
    unmount();
    expect(title.hasAttribute('aria-invalid')).toBe(false);
    title.remove();
  });

  it('filters issues by severity tab', () => {
    render(<ValidationPanel report={report} />);

    // By default "All" is active
    expect(screen.getByText('Complete the English title.')).toBeTruthy();
    expect(screen.getByText('Translation pending.')).toBeTruthy();

    // Click "Errors (1)" filter
    const errorTab = screen.getByRole('tab', { name: /Errors \(1\)/i });
    fireEvent.click(errorTab);
    expect(screen.getByText('Complete the English title.')).toBeTruthy();
    expect(screen.queryByText('Translation pending.')).toBeNull();

    // Click "Warnings (1)" filter
    const warningTab = screen.getByRole('tab', { name: /Warnings \(1\)/i });
    fireEvent.click(warningTab);
    expect(screen.queryByText('Complete the English title.')).toBeNull();
    expect(screen.getByText('Translation pending.')).toBeTruthy();

    // Click "All" filter
    const allTab = screen.getByRole('tab', { name: /All/i });
    fireEvent.click(allTab);
    expect(screen.getByText('Complete the English title.')).toBeTruthy();
    expect(screen.getByText('Translation pending.')).toBeTruthy();
  });

  it('aggregates repetitive warnings with the same message into a compact grouped item', () => {
    const multiWarningReport: ValidationReport = {
      revision_id: 'rev-multi',
      revision_version: 1,
      publication_eligible: true,
      errors: [],
      warnings: [
        { code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.title.vi', message: 'Translation is explicitly pending.', severity: 'WARNING' },
        { code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.summary.vi', message: 'Translation is explicitly pending.', severity: 'WARNING' },
        { code: 'TRANSLATION_PENDING', section: 'CONTENT', field_path: 'content.blocks.0.content.vi', message: 'Translation is explicitly pending.', severity: 'WARNING' },
      ],
    };

    render(<ValidationPanel report={multiWarningReport} />);

    // Should display aggregated count text
    expect(screen.getByText(/3 fields/i)).toBeTruthy();
    expect(screen.getByText(/content\.title\.vi/)).toBeTruthy();
    expect(screen.getByText(/content\.summary\.vi/)).toBeTruthy();
    expect(screen.getByText(/content\.blocks\.0\.content\.vi/)).toBeTruthy();
  });

it('renders unvalidated pending state when report is null', () => {
    render(<ValidationPanel report={null} />);
    expect(screen.getByText('Not validated yet')).toBeTruthy();
    expect(screen.getByText('Ready for inspection')).toBeTruthy();
  });
});
