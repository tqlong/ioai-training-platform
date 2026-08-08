import { drafts } from '../../../src/fixtures/drafts';

export default function AuthorProblemsPage() {
  return (
    <section>
      <h1>Author problems</h1>
      {drafts.length === 0 ? (
        <p>No draft problems in progress.</p>
      ) : (
        <ul>
          {drafts.map((draft) => (
            <li key={draft.id}>{draft.title}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
