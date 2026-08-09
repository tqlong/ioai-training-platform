import type { PublicVocabularyRecord } from '@ioai/api-client';

import { learnApi } from '../../src/api';
import {
  ProblemDiscovery,
  type ProblemVocabulary,
} from '../../src/components/problem-discovery';
import { parseProblemSearchParams, type RawSearchParams } from '../../src/problem-search-params';


type ProblemsPageProps = {
  searchParams?: RawSearchParams;
};

export const dynamic = 'force-dynamic';

export default async function ProblemsPage({
  searchParams = {},
}: ProblemsPageProps) {
  const vocabulary = await loadProblemVocabulary();
  const query = parseProblemSearchParams(searchParams, vocabulary);
  const problems = await learnApi.listPublicProblems(query);

  return (
    <ProblemDiscovery
      vocabulary={vocabulary}
      query={query}
      resultCount={problems.total}
      items={problems.items}
      starter={problems.items[0] ? {
        slug: problems.items[0].slug,
        title: problems.items[0].title.en,
        objective: problems.items[0].objective.en,
        stageCode: problems.items[0].stage_code,
        stageLabel: label(vocabulary.stages, problems.items[0].stage_code),
        difficultyLabel: label(vocabulary.difficulties, problems.items[0].difficulty_code),
        expectedMinutes: problems.items[0].expected_minutes,
        computeLabel: label(vocabulary.computeTiers, problems.items[0].compute_tier_code),
      } : undefined}
    />
  );
}

const loadProblemVocabulary = async (): Promise<ProblemVocabulary> => {
  const [stages, topics, competencies, difficulties, taskTypes, computeTiers] =
    await Promise.all([
      vocabulary('PATHWAY_STAGE'),
      vocabulary('TOPIC', 500),
      vocabulary('COMPETENCY', 500),
      vocabulary('DIFFICULTY'),
      vocabulary('TASK_TYPE'),
      vocabulary('COMPUTE_TIER'),
    ]);
  return {
    stages: stages.map((item) => ({
      ...option(item),
      available: item.availability.is_available,
      availabilityMessage: item.availability.message,
    })),
    topics: topics.map((item) => ({
      ...option(item),
      parentCode: item.parent_identity?.code ?? null,
    })),
    competencies: competencies.map(option),
    difficulties: difficulties.map(option),
    taskTypes: taskTypes.filter(available).map(option),
    computeTiers: computeTiers.filter(available).map(option),
  };
};

const vocabulary = async (
  vocabularyType: string,
  limit = 100,
): Promise<PublicVocabularyRecord[]> => (
  await learnApi.listPublicVocabulary({ vocabularyType, limit })
).items;

const option = (item: PublicVocabularyRecord) => ({
  code: item.identity.code,
  label: item.labels.en,
});

const available = (item: PublicVocabularyRecord): boolean =>
  item.availability.is_available;

const label = (
  options: Array<{ code: string; label: string }>,
  code: string,
): string => options.find((item) => item.code === code)?.label ?? code;
