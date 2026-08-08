import { renderToStaticMarkup } from 'react-dom/server';

import AuthorProblemsPage from '../app/author/problems/page';

describe('IOAI Studio /author/problems shell', () => {
  it('renders without throwing', () => {
    const body = renderToStaticMarkup(<AuthorProblemsPage />);

    expect(body).toContain('Author problems');
  });
});
