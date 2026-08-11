import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { studioApi } from '../src/api';
import { AssessmentQueue } from '../src/components/assessment-queue';

describe('manual assessment queue', () => {
  it('defaults to pending and applies status and problem filters', async () => {
    const list = vi.spyOn(studioApi, 'listAuthorAssessments').mockResolvedValue({
      items: [{
        attempt_id: 'attempt-1', slug: 'precision', title: { en: 'Precision' },
        status: 'PENDING', submitted_at: '2026-08-11T00:00:00Z', score: null,
      }],
      next_offset: null,
    });

    render(<AssessmentQueue />);

    expect(await screen.findByRole('link', { name: 'Precision' })).toBeTruthy();
    expect(list).toHaveBeenCalledWith({ status: 'PENDING', problem: undefined });
    fireEvent.change(screen.getByRole('combobox', { name: 'Status' }), {
      target: { value: 'ASSESSED' },
    });
    fireEvent.change(screen.getByRole('textbox', { name: 'Problem slug' }), {
      target: { value: 'precision' },
    });
    await waitFor(() => expect(list).toHaveBeenLastCalledWith({
      status: 'ASSESSED', problem: 'precision',
    }));
  });
});
