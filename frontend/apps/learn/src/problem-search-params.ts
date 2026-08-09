import type { PublicProblemQuery } from '@ioai/api-client';

import type { ProblemVocabulary, VocabularyOption } from './components/problem-discovery';

export type RawSearchParams = Record<string, string | string[] | undefined>;

const SORTS = ['EDITORIAL', 'NEWEST', 'EXPECTED_TIME', 'TITLE'] as const;

export const parseProblemSearchParams = (
  raw: RawSearchParams,
  vocabulary: ProblemVocabulary,
): PublicProblemQuery => {
  const availableStages = new Set(vocabulary.stages.filter((item) => item.available).map((item) => item.code));
  const query: PublicProblemQuery = {
    stage: canonical(raw.stage, availableStages) ?? vocabulary.stages.find((item) => item.available)?.code,
    competency: canonical(raw.competency, codes(vocabulary.competencies)),
    topic: canonical(raw.topic, codes(vocabulary.topics)),
    difficulty: canonical(raw.difficulty, codes(vocabulary.difficulties)),
    taskType: canonical(raw.task_type, codes(vocabulary.taskTypes)),
    computeTier: canonical(raw.compute_tier, codes(vocabulary.computeTiers)),
    expectedMinutesMin: optionalBoundedInteger(raw.expected_minutes_min, 1, 10_000),
    expectedMinutesMax: optionalBoundedInteger(raw.expected_minutes_max, 1, 10_000),
    search: boundedText(raw.q, 128),
    includeSubtopics: single(raw.include_subtopics) === 'true',
    sort: SORTS.includes(single(raw.sort) as (typeof SORTS)[number])
      ? single(raw.sort) as (typeof SORTS)[number]
      : 'EDITORIAL',
    page: boundedInteger(raw.page, 1, Number.MAX_SAFE_INTEGER, 1),
    pageSize: boundedInteger(raw.page_size, 1, 100, 25),
  };
  if (!query.topic) query.includeSubtopics = false;
  if (query.expectedMinutesMin !== undefined && query.expectedMinutesMax !== undefined && query.expectedMinutesMin > query.expectedMinutesMax) {
    query.expectedMinutesMax = query.expectedMinutesMin;
  }
  return query;
};

const single = (value: string | string[] | undefined): string | undefined => Array.isArray(value) ? value[0] : value;
const codes = (values: VocabularyOption[]): Set<string> => new Set(values.map((item) => item.code));
const canonical = (value: string | string[] | undefined, allowed: Set<string>): string | undefined => {
  const candidate = single(value);
  return candidate && allowed.has(candidate) ? candidate : undefined;
};
const boundedText = (value: string | string[] | undefined, maximum: number): string | undefined => {
  const candidate = single(value)?.trim();
  return candidate ? candidate.slice(0, maximum) : undefined;
};
const boundedInteger = (value: string | string[] | undefined, minimum: number, maximum: number, fallback: number): number => {
  const parsed = Number.parseInt(single(value) ?? '', 10);
  return Number.isFinite(parsed) ? Math.max(minimum, Math.min(maximum, parsed)) : fallback;
};
const optionalBoundedInteger = (value: string | string[] | undefined, minimum: number, maximum: number): number | undefined => {
  const candidate = single(value);
  return candidate === undefined ? undefined : boundedInteger(candidate, minimum, maximum, minimum);
};
