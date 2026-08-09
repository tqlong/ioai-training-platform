import { fireEvent, render, screen } from '@testing-library/react';
import type { AuthorVocabularyRecord } from '@ioai/api-client';

import { emptyResourceDraft, ResourceEditor } from '../src/components/resource-editor';

const record = (type: string, code: string, available = true): AuthorVocabularyRecord => ({
  identity: { vocabulary_type: type, code }, labels: { en: code, vi: code }, aliases: [],
  status: 'ACTIVE', parent_identity: null, breadcrumbs: [], availability: {
    is_available: available, reason_code: available ? 'AVAILABLE' : 'NOT_AVAILABLE_IN_RELEASE_0',
    message: available ? 'Available' : `${code} is not available in Release 0.`,
  },
});
const vocabulary = [
  record('DATA_MODALITY', 'NONE'), record('DATA_MODALITY', 'TABULAR'),
  record('COMPUTE_TIER', 'NONE'), record('COMPUTE_TIER', 'GPU_SMALL', false),
  record('RUNTIME_CLASS', 'INSTANT'),
];

describe('resource policy editor', () => {
  it('enforces NONE modality exclusivity and derives duration display', () => {
    let value = emptyResourceDraft();
    const { rerender } = render(<ResourceEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    fireEvent.click(screen.getByRole('checkbox', { name: /TABULAR/ }));
    rerender(<ResourceEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    expect(value.modalities).toEqual([['DATA_MODALITY', 'TABULAR']]);
    fireEvent.change(screen.getByRole('spinbutton', { name: 'Expected minutes' }), { target: { value: '45' } });
    rerender(<ResourceEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    expect(screen.getByText('Derived duration: STANDARD')).toBeTruthy();
  });

  it('shows actionable Release 0 blockers for unavailable and network policy', () => {
    const value = { ...emptyResourceDraft(), compute_tier: ['COMPUTE_TIER', 'GPU_SMALL'] as [string, string], network_policy: 'ALLOWED' as const };
    render(<ResourceEditor onChange={() => undefined} value={value} vocabulary={vocabulary} />);
    expect(screen.getAllByRole('alert').map((item) => item.textContent).join(' ')).toContain('not available in Release 0');
    expect(screen.getAllByRole('alert').map((item) => item.textContent).join(' ')).toContain('Network access');
  });
});
