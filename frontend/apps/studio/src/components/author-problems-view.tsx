import Link from 'next/link';

import type { AuthorDraftList } from '@ioai/api-client';

export function AuthorProblemsView({ result }: { result: AuthorDraftList }) {
  return (
    <section aria-labelledby="author-problems-title" className="studio-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Editorial workspace</p>
          <h1 id="author-problems-title">Author problems</h1>
          <p>Create, validate, preview, and prepare structured problems for review.</p>
        </div>
        <Link className="primary-action" href="/author/problems/new">
          Create problem
        </Link>
      </div>

      <div aria-label="Problem status" className="status-tabs" role="group">
        <button aria-pressed="true" type="button">All ({result.count})</button>
        <button aria-pressed="false" type="button">Draft</button>
        <button aria-pressed="false" type="button">In review</button>
        <button aria-pressed="false" type="button">Changes requested</button>
      </div>

      <div className="list-tools">
        <label>
          <span>Search author problems</span>
          <input name="search" placeholder="Search title or problem ID" type="search" />
        </label>
        <label>
          <span>Editorial status</span>
          <select name="status" defaultValue="ALL">
            <option value="ALL">All statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="IN_REVIEW">In review</option>
          </select>
        </label>
      </div>

      {result.count === 0 ? (
        <div className="empty-state">
          <h2>No author problems yet</h2>
          <p>Start the first structured draft. Nothing is public until publication.</p>
          <Link href="/author/problems/new">Create the first problem</Link>
        </div>
      ) : (
        <div className="draft-table-wrap">
          <table>
            <caption className="sr-only">Author problem revisions</caption>
            <thead>
              <tr>
                <th scope="col">Problem</th>
                <th scope="col">Status</th>
                <th scope="col">Revision</th>
                <th scope="col">Last saved</th>
                <th scope="col"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              {result.items.map((draft) => (
                <tr key={draft.revision_id}>
                  <td><code>{draft.problem_id}</code></td>
                  <td><span className="status-label">{formatStatus(draft.editorial_status)}</span></td>
                  <td><code>{draft.revision_id}</code> · v{draft.version}</td>
                  <td><time dateTime={draft.last_saved_at}>{formatDate(draft.last_saved_at)}</time></td>
                  <td><Link href={`/author/problems/${draft.problem_id}`}>Resume editing</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

const formatStatus = (status: string) => status.toLowerCase().replaceAll('_', ' ');
const formatDate = (value: string) => new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'UTC',
}).format(new Date(value));
