export const LEARNER_PROGRESS_KEY = 'ioai.learn.progress.v1';
const LEGACY_GUIDANCE_KEY = 'ioai.learn.guidance.v1';
const MAX_BYTES = 40_000;
const MAX_PROBLEMS = 100;
const STATUSES = ['NOT_STARTED', 'ATTEMPTED', 'COMPLETED'] as const;
const EVIDENCE = ['INTRODUCED', 'PRACTICED', 'APPLIED', 'PROFICIENT'] as const;

export type TaskStatus = typeof STATUSES[number];
export type LearningEvidence = typeof EVIDENCE[number];
export type ProblemProgress = {
  status: TaskStatus;
  evidence?: LearningEvidence;
  elapsedSeconds?: number;
  hintCount?: number;
};
export type LearnerProgress = {
  schemaVersion: 1;
  problems: Record<string, ProblemProgress>;
  recentCompleted: Array<{ slug: string; title: string }>;
  weeklyGoal?: { target: number; completed: number };
  currentPath?: { label: string; completed: number; total: number };
  prerequisites: string[];
  suggestedTopics: Array<{ code: string; label: string }>;
};
export type ProgressStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;
export type ProgressRead = { state: LearnerProgress; available: boolean; corrupt: boolean };
export type ProgressEvent = { slug: string; title: string; status: TaskStatus; evidence?: LearningEvidence; elapsedSeconds?: number; hintCount?: number };

const empty = (): LearnerProgress => ({ schemaVersion: 1, problems: {}, recentCompleted: [], prerequisites: [], suggestedTopics: [] });

export const parseLearnerProgress = (raw: string | null): LearnerProgress | null => {
  if (!raw || raw.length > MAX_BYTES) return null;
  try {
    const value: unknown = JSON.parse(raw);
    if (!record(value) || value.schemaVersion !== 1) return null;
    if (value.problems !== undefined && !record(value.problems)) return null;
    const problems: Record<string, ProblemProgress> = {};
    for (const [slug, candidate] of Object.entries(value.problems ?? {}).slice(0, MAX_PROBLEMS)) {
      if (!short(slug) || !record(candidate) || !status(candidate.status)) continue;
      const item: ProblemProgress = { status: candidate.status };
      if (evidence(candidate.evidence)) item.evidence = candidate.evidence;
      if (bounded(candidate.elapsedSeconds, 604_800)) item.elapsedSeconds = candidate.elapsedSeconds;
      if (bounded(candidate.hintCount, 100)) item.hintCount = candidate.hintCount;
      problems[slug] = item;
    }
    const recentCompleted = Array.isArray(value.recentCompleted)
      ? value.recentCompleted.filter((item): item is { slug: string; title: string } => record(item) && short(item.slug) && short(item.title)).slice(0, 3)
      : [];
    const weeklyGoal = progress(value.weeklyGoal, 365);
    const currentPath = path(value.currentPath);
    if (value.weeklyGoal !== undefined && !weeklyGoal) return null;
    if (value.currentPath !== undefined && !currentPath) return null;
    return {
      schemaVersion: 1, problems, recentCompleted, weeklyGoal, currentPath,
      prerequisites: strings(value.prerequisites, 3),
      suggestedTopics: Array.isArray(value.suggestedTopics)
        ? value.suggestedTopics.filter((item): item is { code: string; label: string } => record(item) && short(item.code) && short(item.label)).slice(0, 2)
        : [],
    };
  } catch { return null; }
};

export const createLearnerProgressAdapter = (storage: ProgressStorage) => ({
  read(): ProgressRead {
    try {
      const raw = storage.getItem(LEARNER_PROGRESS_KEY);
      if (!raw) return { state: empty(), available: true, corrupt: false };
      const state = parseLearnerProgress(raw);
      if (state) return { state, available: true, corrupt: false };
      storage.removeItem(LEARNER_PROGRESS_KEY);
      return { state: empty(), available: true, corrupt: true };
    } catch { return { state: empty(), available: false, corrupt: false }; }
  },
  record(event: ProgressEvent): ProgressRead {
    const current = this.read();
    if (!current.available || !short(event.slug) || !short(event.title)) return current;
    const previous = current.state.problems[event.slug];
    const nextStatus = STATUSES[Math.max(STATUSES.indexOf(previous?.status ?? 'NOT_STARTED'), STATUSES.indexOf(event.status))];
    const next: ProblemProgress = { status: nextStatus };
    const nextEvidence = evidence(event.evidence) && (!previous?.evidence || EVIDENCE.indexOf(event.evidence) >= EVIDENCE.indexOf(previous.evidence)) ? event.evidence : previous?.evidence;
    if (nextEvidence) next.evidence = nextEvidence;
    const elapsed = event.elapsedSeconds ?? previous?.elapsedSeconds;
    const hints = event.hintCount ?? previous?.hintCount;
    if (bounded(elapsed, 604_800)) next.elapsedSeconds = elapsed;
    if (bounded(hints, 100)) next.hintCount = hints;
    const problems = { ...current.state.problems, [event.slug]: next };
    const boundedProblems = Object.fromEntries(Object.entries(problems).slice(-MAX_PROBLEMS));
    const recentCompleted = nextStatus === 'COMPLETED'
      ? [{ slug: event.slug, title: event.title }, ...current.state.recentCompleted.filter(item => item.slug !== event.slug)].slice(0, 3)
      : current.state.recentCompleted;
    const state: LearnerProgress = {
      ...current.state, schemaVersion: 1, problems: boundedProblems, recentCompleted,
    };
    try {
      const encoded = JSON.stringify(state);
      if (encoded.length > MAX_BYTES) return { state: current.state, available: true, corrupt: false };
      storage.setItem(LEARNER_PROGRESS_KEY, encoded);
      window.dispatchEvent(new CustomEvent('ioai-progress', { detail: state }));
      return { state, available: true, corrupt: false };
    } catch { return { state: current.state, available: false, corrupt: false }; }
  },
});

export const browserProgressAdapter = () => {
  try {
    const adapter = createLearnerProgressAdapter(window.localStorage);
    if (!window.localStorage.getItem(LEARNER_PROGRESS_KEY)) {
      const migrated = parseLearnerProgress(window.localStorage.getItem(LEGACY_GUIDANCE_KEY));
      if (migrated) {
        window.localStorage.setItem(LEARNER_PROGRESS_KEY, JSON.stringify(migrated));
        window.localStorage.removeItem(LEGACY_GUIDANCE_KEY);
      }
    }
    return adapter;
  }
  catch { return undefined; }
};

const record = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const short = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0 && value.length <= 160;
const status = (value: unknown): value is TaskStatus => typeof value === 'string' && STATUSES.includes(value as TaskStatus);
const evidence = (value: unknown): value is LearningEvidence => typeof value === 'string' && EVIDENCE.includes(value as LearningEvidence);
const bounded = (value: unknown, maximum: number): value is number => typeof value === 'number' && Number.isInteger(value) && value >= 0 && value <= maximum;
const progress = (value: unknown, maximum: number) => {
  if (value === undefined) return undefined;
  if (!record(value) || !bounded(value.target, maximum) || value.target < 1 || !bounded(value.completed, value.target)) return undefined;
  return { target: value.target, completed: value.completed };
};
const path = (value: unknown) => {
  if (value === undefined) return undefined;
  if (!record(value) || !short(value.label) || !bounded(value.total, 1000) || value.total < 1 || !bounded(value.completed, value.total)) return undefined;
  return { label: value.label, completed: value.completed, total: value.total };
};
const strings = (value: unknown, maximum: number): string[] => Array.isArray(value) ? value.filter(short).slice(0, maximum) : [];
