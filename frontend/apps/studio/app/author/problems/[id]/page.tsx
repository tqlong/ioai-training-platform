import { studioApi } from '../../../../src/api';
import { DraftEditor } from '../../../../src/components/draft-editor';

export const dynamic = 'force-dynamic';

export default async function EditProblemPage({ params }: { params: { id: string } }) {
  const draft = await studioApi.getAuthorDraft(params.id);
  return <DraftEditor initialDraft={draft} />;
}
