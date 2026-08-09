import { studioApi } from '../../../../../src/api';
import { LearnerPreview } from '../../../../../src/components/learner-preview';

export const dynamic = 'force-dynamic';

export default async function PreviewProblemPage({ params }: { params: { id: string } }) {
  const draft = await studioApi.getAuthorDraft(params.id);
  return <LearnerPreview initialDraft={draft} />;
}
