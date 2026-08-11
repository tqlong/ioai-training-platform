import { readSubmissionHistory, recordSubmission, updateSubmissionStatus } from '../src/submission-history';

describe('device-local submission history', () => {
  it('stores private receipt links, updates status, and bounds history to 100', () => {
    localStorage.clear();
    for (let index = 0; index < 105; index += 1) {
      recordSubmission({
        attempt_id: `attempt-${index}`,
        receipt: `receipt-${index}`,
        result_url: `/submissions/attempt-${index}`,
        submitted_at: new Date(index * 1000).toISOString(),
        outcome: 'PENDING_ASSESSMENT',
        message: 'Pending',
      }, { receipt: `private-${index}`, slug: `problem-${index}`, title: `Problem ${index}` });
    }

    expect(readSubmissionHistory()).toHaveLength(100);
    expect(readSubmissionHistory()[0]).toMatchObject({ attemptId: 'attempt-104', receipt: 'private-104' });
    updateSubmissionStatus('attempt-104', 'ACCEPTED_RESULT');
    expect(readSubmissionHistory()[0]?.status).toBe('ACCEPTED_RESULT');
  });

  it('discards corrupt local history without throwing', () => {
    localStorage.setItem('ioai.learn.submissions.v1', '{');
    expect(readSubmissionHistory()).toEqual([]);
  });
});
