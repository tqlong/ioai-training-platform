import { problems } from '../../src/fixtures/problems';

export default function ProblemsPage() {
  return (
    <section>
      <h1>Problems</h1>
      {problems.length === 0 ? (
        <p>No published problems yet.</p>
      ) : (
        <ul>
          {problems.map((problem) => (
            <li key={problem.id}>{problem.title}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
