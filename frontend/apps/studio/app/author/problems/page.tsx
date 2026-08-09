import { studioApi } from '../../../src/api';
import { AuthorProblemsView } from '../../../src/components/author-problems-view';

export const dynamic = 'force-dynamic';

export default async function AuthorProblemsPage() {
  const result = await studioApi.listAuthorDrafts();
  return <AuthorProblemsView result={result} />;
}
