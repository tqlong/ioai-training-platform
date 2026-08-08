import { renderToStaticMarkup } from 'react-dom/server';

import ProblemsPage from '../app/problems/page';

describe('IOAI Learn /problems shell', () => {
  it('renders without throwing', () => {
    const body = renderToStaticMarkup(<ProblemsPage />);

    expect(body).toContain('Problems');
  });
});
