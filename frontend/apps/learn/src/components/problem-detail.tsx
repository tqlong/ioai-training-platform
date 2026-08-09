import type { PublicProblemDetail as PublicProblem } from '@ioai/api-client';

type Props = { problem: PublicProblem; labels: Record<string, string>; returnUrl: string };

export function ProblemDetail({ problem, labels, returnUrl }: Props) {
  const label = (code: string) => labels[code] ?? code;
  return <article className="problem-detail">
    <a aria-label="Back to problem library" href={returnUrl}>← Back to problem library</a>
    <header><p className="eyebrow">{problem.public_short_id}</p><h1>{problem.title.en}</h1>
      <p>{label(problem.stage_code)} · {label(problem.difficulty_code)}</p><p>{problem.summary.en}</p></header>
    <aside className="problem-metadata" aria-label="Problem metadata">
      <span>{label(problem.primary_competency_code)}</span><span>{problem.expected_minutes} min</span>
      <span>{label(problem.resources.compute_tier_code)}</span>
      {problem.topic_codes.map((code) => <span key={code}>{label(code)}</span>)}
    </aside>
    <section><h2>Learning objective</h2><p>{problem.objective.en}</p></section>
    {problem.prerequisites.length ? <section><h2>Prerequisites</h2><ul>{problem.prerequisites.map((item, index) => <li key={`${item.target_type}-${item.target_code ?? item.target_id}-${index}`}>{item.relationship.toLowerCase()}: {label(item.target_code ?? item.target_id ?? '')}{item.minimum_evidence ? ` · ${item.minimum_evidence.toLowerCase()}` : ''}</li>)}</ul></section> : null}
    <section aria-label="Problem content">{problem.blocks.map((block) => block.kind === 'HINT' ? <details key={block.order}><summary role="button" aria-label={`Show hint ${block.reveal_order}`}>Hint {block.reveal_order}</summary><p>{block.content.en}</p></details> : block.kind === 'EXPLANATION' ? <details key={block.order}><summary>Explanation</summary><p>{block.content.en}</p></details> : <section key={block.order}><h2>{block.kind.replaceAll('_', ' ').toLowerCase()}</h2><p>{block.content.en}</p></section>)}</section>
    <section className="response-placeholder" aria-label="Your response"><h2>Your response</h2><p>{label(problem.task_type_code)} response form</p></section>
    <footer><a id="problem-feedback" href="#problem-feedback">Report a problem</a><p>Next recommendation will appear here after you work on this problem.</p></footer>
  </article>;
}
