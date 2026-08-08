'use client';

import { useEffect } from 'react';

export default function ErrorBoundary({ error }: { error: Error }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return <p role="alert">Unable to load this page.</p>;
}
