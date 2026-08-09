'use client';

import { useEffect } from 'react';

import { browserProgressAdapter } from '../learner-progress';

export function ProblemOpenedTracker({ slug, title }: { slug: string; title: string }) {
  useEffect(() => {
    browserProgressAdapter()?.record({ slug, title, status: 'NOT_STARTED' });
  }, [slug, title]);
  return null;
}
