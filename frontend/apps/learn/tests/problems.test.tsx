import { renderToStaticMarkup } from 'react-dom/server';

import ProblemsPage from '../app/problems/page';

describe('IOAI Learn /problems shell', () => {
  it('renders without throwing', () => {
    const body = renderToStaticMarkup(<ProblemsPage />);

    expect(body).toContain('Problems');
    expect(body).toContain('No published problems yet.');
    expect(body).not.toContain('Draft preview');
    expect(body).not.toContain('revision_id');
    expect(body).not.toContain('editorial_status');
  });
});
