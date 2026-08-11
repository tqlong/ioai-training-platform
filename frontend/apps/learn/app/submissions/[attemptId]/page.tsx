import { SubmissionResult } from '../../../src/components/submission-result';

export default function SubmissionPage({ params }: { params: { attemptId: string } }) {
  return <SubmissionResult attemptId={params.attemptId} />;
}
