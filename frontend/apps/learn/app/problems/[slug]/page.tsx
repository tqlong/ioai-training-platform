import { notFound } from 'next/navigation';

import { ApiError } from '@ioai/api-client';

import { learnApi } from '../../../src/api';
import { ProblemDetail } from '../../../src/components/problem-detail';
import { safeReturnUrl } from '../../../src/problem-navigation';

type Props = { params: { slug: string }; searchParams?: { return_to?: string | string[] } };
export const dynamic = 'force-dynamic';

export default async function ProblemPage({ params, searchParams = {} }: Props) {
  try {
    const problem = await learnApi.getPublicProblem(params.slug);
    const codes = [problem.stage_code, problem.difficulty_code, problem.primary_competency_code, problem.task_type_code, problem.resources.compute_tier_code, ...problem.topic_codes, ...problem.prerequisite_codes];
    const records = await Promise.all(['PATHWAY_STAGE', 'DIFFICULTY', 'COMPETENCY', 'TASK_TYPE', 'COMPUTE_TIER', 'TOPIC'].map((vocabularyType) => learnApi.listPublicVocabulary({ vocabularyType, limit: 500 })));
    const labels = Object.fromEntries(records.flatMap((page) => page.items).filter((item) => codes.includes(item.identity.code)).map((item) => [item.identity.code, item.labels.en]));
    const candidate = Array.isArray(searchParams.return_to) ? searchParams.return_to[0] : searchParams.return_to;
    const returnUrl = safeReturnUrl(candidate);
    return <ProblemDetail problem={problem} labels={labels} returnUrl={returnUrl} />;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}
