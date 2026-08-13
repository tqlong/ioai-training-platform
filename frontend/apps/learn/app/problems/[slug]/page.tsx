import { notFound } from 'next/navigation';

import { ApiError } from '@ioai/api-client';

import { learnApi } from '../../../src/api';
import { ProblemDetail } from '../../../src/components/problem-detail';
import { loadProblemDetail } from '../../../src/problem-detail-loader';
import { safeReturnUrl } from '../../../src/problem-navigation';

type Props = { params: { slug: string }; searchParams?: { return_to?: string | string[] } };
export const dynamic = 'force-dynamic';

export default async function ProblemPage({ params, searchParams = {} }: Props) {
  try {
    const { problem, labels } = await loadProblemDetail(learnApi, params.slug);
    const candidate = Array.isArray(searchParams.return_to) ? searchParams.return_to[0] : searchParams.return_to;
    const returnUrl = safeReturnUrl(candidate);
    return <ProblemDetail problem={problem} labels={labels} returnUrl={returnUrl} />;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}
