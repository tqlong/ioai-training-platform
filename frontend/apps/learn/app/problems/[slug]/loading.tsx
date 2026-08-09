export default function ProblemLoading() {
  return <section className="library-skeleton" role="status" aria-label="Loading problem">
    <span className="skeleton-heading" aria-hidden="true" />
    <span className="skeleton-filter" aria-hidden="true" />
    <div className="skeleton-results"><span aria-hidden="true" /><span aria-hidden="true" /></div>
    <span className="visually-hidden">Loading the published problem…</span>
  </section>;
}
