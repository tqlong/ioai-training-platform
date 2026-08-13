import type { PublicProblemDetail as PublicProblem } from '@ioai/api-client';

import { LearnerActions } from './learner-actions';
import { ProblemOpenedTracker } from './problem-opened-tracker';

type Props = { problem: PublicProblem; labels: Record<string, string>; returnUrl: string };

export function ProblemDetail({ problem, labels, returnUrl }: Props) {
  const label = (code: string) => labels[code] ?? code;
  const typedLabel = (vocabularyType: string, code: string) =>
    labels[`${vocabularyType}:${code}`]
      ?? (vocabularyType === 'DATA_MODALITY' && code === 'NONE' ? 'No Dataset' : label(code));
  return <article className="problem-detail">
    <ProblemOpenedTracker slug={problem.slug} title={problem.title.en} />
    <a aria-label="Back to problem library" href={returnUrl}>← Back to problem library</a>
    <header><p className="eyebrow">{problem.public_short_id}</p><h1>{problem.title.en}</h1>
      <p>{label(problem.stage_code)} · {label(problem.difficulty_code)}</p><p>{problem.summary.en}</p></header>
    <aside aria-label="Problem metadata">
      <dl className="problem-metadata">
        <div><dt>Competency</dt><dd>{typedLabel('COMPETENCY', problem.primary_competency_code)}</dd></div>
        <div><dt>Time</dt><dd>{problem.expected_minutes} min</dd></div>
        <div><dt>Compute</dt><dd>{typedLabel('COMPUTE_TIER', problem.resources.compute_tier_code)}</dd></div>
        <div><dt>Data</dt><dd>{problem.modality_codes.map((code) => typedLabel('DATA_MODALITY', code)).join(', ')}</dd></div>
        {problem.topic_codes.map((code) => <div key={code}><dt>Topic</dt><dd>{typedLabel('TOPIC', code)}</dd></div>)}
      </dl>
    </aside>
    <section><h2>Learning objective</h2><p>{problem.objective.en}</p></section>
    {problem.prerequisites.length ? <section><h2>Prerequisites</h2><ul>{problem.prerequisites.map((item, index) => <li key={`${item.target_type}-${item.target_code ?? item.target_id}-${index}`}>{item.relationship.toLowerCase()}: {label(item.target_code ?? item.target_id ?? '')}{item.minimum_evidence ? ` · ${item.minimum_evidence.toLowerCase()}` : ''}</li>)}</ul></section> : null}
    <section aria-label="Problem content">{problem.blocks.map((block) => block.kind === 'HINT' ? <details key={block.order}><summary role="button" aria-label={`Show hint ${block.reveal_order}`}>Hint {block.reveal_order}</summary><p>{block.content.en}</p></details> : block.kind === 'EXPLANATION' ? <details key={block.order}><summary>Explanation</summary><p>{block.content.en}</p></details> : <section key={block.order}><h2>{block.kind.replaceAll('_', ' ').toLowerCase()}</h2><p>{block.content.en}</p></section>)}</section>
    <LearnerActions slug={problem.slug} title={problem.title.en} stage={problem.stage_code} schema={problem.response_schema} />
  </article>;
}
