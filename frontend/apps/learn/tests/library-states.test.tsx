import { fireEvent, render, screen } from '@testing-library/react';

import ErrorBoundary from '../app/error';
import Loading from '../app/loading';


describe('learner library resilient states', () => {
  it('keeps meaningful page and result dimensions while loading', () => {
    render(<Loading />);

    expect(screen.getByRole('status', { name: 'Loading problem library' }))
      .toHaveClass('library-skeleton');
    expect(screen.getAllByLabelText('Loading problem')).toHaveLength(5);
  });

  it('offers safe retry and feedback paths without exposing the error', () => {
    const reset = vi.fn();
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    render(<ErrorBoundary error={new Error('postgres password secret')} reset={reset} />);

    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent('Problem library unavailable');
    expect(alert).not.toHaveTextContent('postgres password secret');
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(reset).toHaveBeenCalledOnce();
    expect(screen.getByRole('link', { name: 'Send feedback' })).toHaveAttribute(
      'href',
      'mailto:feedback@ioai-official.org?subject=IOAI%20Learn%20problem%20library',
    );
  });
});
