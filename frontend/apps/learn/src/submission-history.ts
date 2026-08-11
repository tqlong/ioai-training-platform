import type { PublicSubmissionResult } from '@ioai/api-client';

const KEY = 'ioai.learn.submissions.v1';
const LIMIT = 100;

export type LocalSubmission = {
  attemptId: string;
  receipt: string;
  slug: string;
  title: string;
  status: PublicSubmissionResult['outcome'];
  passed?: boolean;
  submittedAt: string;
};

export const readSubmissionHistory = (): LocalSubmission[] => {
  if (typeof window === 'undefined') return [];
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(KEY) ?? '[]');
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isSubmission).slice(0, LIMIT);
  } catch {
    return [];
  }
};

export const recordSubmission = (
  result: PublicSubmissionResult,
  context: { receipt: string; slug: string; title: string },
): void => {
  if (typeof window === 'undefined') return;
  const item: LocalSubmission = {
    attemptId: result.attempt_id,
    receipt: context.receipt,
    slug: context.slug,
    title: context.title,
    status: result.outcome,
    passed: result.passed ?? undefined,
    submittedAt: result.submitted_at,
  };
  const next = [item, ...readSubmissionHistory().filter(value => value.attemptId !== item.attemptId)].slice(0, LIMIT);
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    // Submission still succeeds when browser storage is unavailable.
  }
};

export const updateSubmissionStatus = (
  attemptId: string,
  status: PublicSubmissionResult['outcome'],
  passed?: boolean,
): void => {
  if (typeof window === 'undefined') return;
  const items = readSubmissionHistory();
  const next = items.map(item => item.attemptId === attemptId ? { ...item, status, passed } : item);
  try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { /* local-only best effort */ }
};

const isSubmission = (value: unknown): value is LocalSubmission => {
  if (!value || typeof value !== 'object') return false;
  const item = value as Record<string, unknown>;
  return typeof item.attemptId === 'string' && typeof item.receipt === 'string' &&
    typeof item.slug === 'string' && typeof item.title === 'string' &&
    (item.status === 'ACCEPTED_RESULT' || item.status === 'PENDING_ASSESSMENT') &&
    typeof item.submittedAt === 'string';
};
