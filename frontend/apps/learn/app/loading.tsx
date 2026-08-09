export default function Loading() {
  return (
    <section className="library-skeleton" role="status" aria-label="Loading problem library">
      <span className="skeleton-heading" aria-hidden="true" />
      <span className="skeleton-filter" aria-hidden="true" />
      <div className="skeleton-results">
        {Array.from({ length: 5 }, (_, index) => (
          <span key={index} aria-label="Loading problem" />
        ))}
      </div>
      <span className="visually-hidden">Loading the published problem library…</span>
    </section>
  );
}
