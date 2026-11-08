import { studioApi } from '../../../../src/api';
import { DraftEditor } from '../../../../src/components/draft-editor';

export const dynamic = 'force-dynamic';

export default async function EditProblemPage({
  params,
  searchParams,
}: {
  params: { id: string };
  searchParams?: Promise<{ revision?: string }> | { revision?: string };
}) {
  const sp = await searchParams;
  const draft = sp?.revision
    ? await studioApi.getAuthorRevision(sp.revision)
    : await studioApi.getAuthorDraft(params.id);
  return <DraftEditor key={draft.revision_id} initialDraft={draft} />;
}
