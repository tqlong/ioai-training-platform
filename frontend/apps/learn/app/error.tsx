'use client';

import { useEffect } from 'react';

export default function ErrorBoundary({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="library-error" role="alert">
      <h1>Problem library unavailable</h1>
      <p>We could not load the published problems. Your filters are safe to try again.</p>
      <div className="state-actions">
        <button type="button" onClick={reset}>Try again</button>
        <a href="mailto:feedback@ioai-official.org?subject=IOAI%20Learn%20problem%20library">
          Send feedback
        </a>
      </div>
    </section>
  );
}
