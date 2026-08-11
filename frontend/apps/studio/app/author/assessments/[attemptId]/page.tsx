import { AssessmentForm } from '../../../../src/components/assessment-queue';

export default function AssessmentPage({ params }: { params: { attemptId: string } }) {
  return <AssessmentForm attemptId={params.attemptId} />;
}
