import type { ApiClient, PublicProblemDetail } from '@ioai/api-client';
import { canonicalVocabularyRecords } from '@ioai/vocabulary';


type DetailApi = Pick<ApiClient, 'getPublicProblem'>;

export type LoadedProblemDetail = {
  problem: PublicProblemDetail;
  labels: Record<string, string>;
};

export const loadProblemDetail = async (
  api: DetailApi,
  slug: string,
): Promise<LoadedProblemDetail> => {
  const problem = await api.getPublicProblem(slug);
  const identities = new Set([
    identity('PATHWAY_STAGE', problem.stage_code),
    identity('DIFFICULTY', problem.difficulty_code),
    identity('COMPETENCY', problem.primary_competency_code),
    identity('TASK_TYPE', problem.task_type_code),
    identity('COMPUTE_TIER', problem.resources.compute_tier_code),
    ...problem.secondary_competency_codes.map((code) => identity('COMPETENCY', code)),
    ...problem.topic_codes.map((code) => identity('TOPIC', code)),
    ...problem.modality_codes.map((code) => identity('DATA_MODALITY', code)),
    ...problem.prerequisites.flatMap((prerequisite) => prerequisite.target_code
      ? [identity(prerequisite.target_type, prerequisite.target_code)]
      : []),
  ]);
  const labels = Object.fromEntries(
    canonicalVocabularyRecords
      .filter((record) => identities.has(identity(record.vocabulary_type, record.code)))
      .flatMap((record) => [
        [record.code, record.labels.en],
        [identity(record.vocabulary_type, record.code), record.labels.en],
      ]),
  );
  return { problem, labels };
};

const identity = (vocabularyType: string, code: string): string =>
  `${vocabularyType}:${code}`;
