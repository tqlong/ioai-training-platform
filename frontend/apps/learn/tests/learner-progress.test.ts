import {
  createLearnerProgressAdapter,
  browserProgressAdapter,
  LEARNER_PROGRESS_KEY,
  parseLearnerProgress,
  type ProgressStorage,
} from '../src/learner-progress';


const memoryStorage = (): ProgressStorage & { value: string | null } => ({
  value: null,
  getItem() { return this.value; },
  setItem(_key, value) { this.value = value; },
  removeItem() { this.value = null; },
});

describe('versioned anonymous learner progress', () => {
  it('bounds valid state and drops forbidden or excess fields', () => {
    const state = parseLearnerProgress(JSON.stringify({
      schemaVersion: 1,
      problems: {
        metrics: { status: 'COMPLETED', evidence: 'PRACTICED', elapsedSeconds: 30, hintCount: 2, response: 'secret', editorial_status: 'PUBLISHED' },
        invalid: { status: 'MASTERED' },
      },
      recentCompleted: Array.from({ length: 20 }, (_, index) => ({ slug: `p-${index}`, title: `Problem ${index}` })),
      identity: { email: 'learner@example.test' },
    }));
    expect(state?.problems.metrics).toEqual({ status: 'COMPLETED', evidence: 'PRACTICED', elapsedSeconds: 30, hintCount: 2 });
    expect(state?.problems.invalid).toBeUndefined();
    expect(state?.recentCompleted).toHaveLength(3);
    expect(JSON.stringify(state)).not.toMatch(/secret|editorial|email|MASTERED/);
  });

  it('records open, attempt, completion, and evidence as separate bounded dimensions', () => {
    const storage = memoryStorage();
    const adapter = createLearnerProgressAdapter(storage);
    adapter.record({ slug: 'metrics', title: 'Metrics', status: 'ATTEMPTED' });
    adapter.record({ slug: 'metrics', title: 'Metrics', status: 'COMPLETED', evidence: 'APPLIED' });
    expect(adapter.read().state.problems.metrics).toEqual({ status: 'COMPLETED', evidence: 'APPLIED' });
    expect(adapter.read().state.recentCompleted).toEqual([{ slug: 'metrics', title: 'Metrics' }]);
    adapter.recordTransition('metrics', 'next');
    expect(adapter.read().state).toEqual(expect.objectContaining({
      continuationTransitions: 1, lastContinuation: { from: 'metrics', to: 'next' },
    }));
    expect(storage.value).not.toContain('response');
  });

  it('quarantines corrupt state and reports unavailable storage without throwing', () => {
    const corrupt = memoryStorage();
    corrupt.value = '{';
    expect(createLearnerProgressAdapter(corrupt).read()).toEqual(expect.objectContaining({ corrupt: true }));
    const unavailable: ProgressStorage = { getItem: () => { throw new Error('denied'); }, setItem: () => { throw new Error('denied'); }, removeItem: () => undefined };
    expect(createLearnerProgressAdapter(unavailable).read()).toEqual(expect.objectContaining({ available: false }));
    expect(() => createLearnerProgressAdapter(unavailable).record({ slug: 'x', title: 'X', status: 'ATTEMPTED' })).not.toThrow();
  });

  it('migrates the supported guidance-only v1 record into the progress key', () => {
    localStorage.clear();
    localStorage.setItem('ioai.learn.guidance.v1', JSON.stringify({
      schemaVersion: 1, recentCompleted: [{ slug: 'one', title: 'One' }],
    }));
    expect(browserProgressAdapter()?.read().state.recentCompleted[0]?.slug).toBe('one');
    expect(localStorage.getItem(LEARNER_PROGRESS_KEY)).toContain('"problems"');
    expect(localStorage.getItem('ioai.learn.guidance.v1')).toBeNull();
  });
});
