import type { PublicProblemQuery } from '@ioai/api-client';


export type VocabularyOption = { code: string; label: string };
export type StageOption = VocabularyOption & {
  available: boolean;
  availabilityMessage: string;
};
export type TopicOption = VocabularyOption & { parentCode: string | null };
export type ProblemVocabulary = {
  stages: StageOption[];
  topics: TopicOption[];
  competencies: VocabularyOption[];
  difficulties: VocabularyOption[];
  taskTypes: VocabularyOption[];
  computeTiers: VocabularyOption[];
};
export type RawSearchParams = Record<string, string | string[] | undefined>;

const SORTS = ['EDITORIAL', 'NEWEST', 'EXPECTED_TIME', 'TITLE'] as const;

export const parseProblemSearchParams = (
  raw: RawSearchParams,
  vocabulary: ProblemVocabulary,
): PublicProblemQuery => {
  const availableStages = new Set(
    vocabulary.stages.filter((item) => item.available).map((item) => item.code),
  );
  const query: PublicProblemQuery = {
    stage: canonical(raw.stage, availableStages) ?? vocabulary.stages.find((item) => item.available)?.code,
    competency: canonical(raw.competency, codes(vocabulary.competencies)),
    topic: canonical(raw.topic, codes(vocabulary.topics)),
    difficulty: canonical(raw.difficulty, codes(vocabulary.difficulties)),
    taskType: canonical(raw.task_type, codes(vocabulary.taskTypes)),
    computeTier: canonical(raw.compute_tier, codes(vocabulary.computeTiers)),
    expectedMinutesMin: optionalBoundedInteger(raw.expected_minutes_min, 1, 10_000),
    expectedMinutesMax: optionalBoundedInteger(raw.expected_minutes_max, 1, 10_000),
    search: boundedText(raw.q, 128),
    includeSubtopics: single(raw.include_subtopics) === 'true',
    sort: SORTS.includes(single(raw.sort) as (typeof SORTS)[number])
      ? single(raw.sort) as (typeof SORTS)[number]
      : 'EDITORIAL',
    page: boundedInteger(raw.page, 1, Number.MAX_SAFE_INTEGER, 1),
    pageSize: boundedInteger(raw.page_size, 1, 100, 25),
  };
  if (!query.topic) query.includeSubtopics = false;
  if (
    query.expectedMinutesMin !== undefined
    && query.expectedMinutesMax !== undefined
    && query.expectedMinutesMin > query.expectedMinutesMax
  ) {
    query.expectedMinutesMax = query.expectedMinutesMin;
  }
  return query;
};

const single = (value: string | string[] | undefined): string | undefined =>
  Array.isArray(value) ? value[0] : value;

const codes = (values: VocabularyOption[]): Set<string> =>
  new Set(values.map((item) => item.code));

const canonical = (
  value: string | string[] | undefined,
  allowed: Set<string>,
): string | undefined => {
  const candidate = single(value);
  return candidate && allowed.has(candidate) ? candidate : undefined;
};

const boundedText = (
  value: string | string[] | undefined,
  maximum: number,
): string | undefined => {
  const candidate = single(value)?.trim();
  return candidate ? candidate.slice(0, maximum) : undefined;
};

const boundedInteger = (
  value: string | string[] | undefined,
  minimum: number,
  maximum: number,
  fallback: number,
): number => {
  const parsed = Number.parseInt(single(value) ?? '', 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(minimum, Math.min(maximum, parsed));
};

const optionalBoundedInteger = (
  value: string | string[] | undefined,
  minimum: number,
  maximum: number,
): number | undefined => {
  const candidate = single(value);
  return candidate === undefined
    ? undefined
    : boundedInteger(candidate, minimum, maximum, minimum);
};

type ProblemDiscoveryProps = {
  vocabulary: ProblemVocabulary;
  query: PublicProblemQuery;
  resultCount: number;
  problemTitles: string[];
};

export function ProblemDiscovery({
  vocabulary,
  query,
  resultCount,
  problemTitles,
}: ProblemDiscoveryProps) {
  const queryParams = toSearchParams(query);
  const families = vocabulary.topics.filter((item) => item.parentCode === null);
  const activeFilters = activeFilterEntries(query, vocabulary);

  return (
    <section className="problem-library" aria-labelledby="problems-heading">
      <div className="library-heading">
        <div>
          <p className="eyebrow">Practice library</p>
          <h1 id="problems-heading">Problems</h1>
          <p>Choose your stage, find focused practice, and keep moving.</p>
        </div>
        <p className="result-count" aria-live="polite">{resultCount} problems</p>
      </div>

      <div className="stage-selector" role="group" aria-label="Choose pathway stage">
        {vocabulary.stages.map((stage) => stage.available ? (
          <a
            key={stage.code}
            className={stage.code === query.stage ? 'stage active' : 'stage'}
            aria-current={stage.code === query.stage ? 'true' : undefined}
            href={withParameter(queryParams, 'stage', stage.code)}
          >
            {stage.label}
          </a>
        ) : (
          <button
            key={stage.code}
            className="stage unavailable"
            type="button"
            disabled
            title={stage.availabilityMessage}
          >
            {stage.label}<span>Coming next</span>
          </button>
        ))}
      </div>

      <form className="filter-bar" role="search" action="/problems" method="get">
        <input type="hidden" name="stage" value={query.stage} />
        <label className="search-field">
          <span>Search problems</span>
          <input
            type="search"
            name="q"
            defaultValue={query.search}
            placeholder="Titles, objectives, topics…"
          />
        </label>
        <label>
          <span>Topic</span>
          <input
            name="topic"
            list="topic-options"
            defaultValue={query.topic}
            placeholder="Search topic hierarchy"
          />
        </label>
        <datalist id="topic-options">
          {vocabulary.topics.map((topic) => (
            <option key={topic.code} value={topic.code}>
              {topicPath(topic, vocabulary.topics)}
            </option>
          ))}
        </datalist>
        <label>
          <span>Difficulty</span>
          <select name="difficulty" defaultValue={query.difficulty ?? ''}>
            <option value="">All difficulties</option>
            {vocabulary.difficulties.map(option)}
          </select>
        </label>
        <label>
          <span>Type</span>
          <select name="task_type" defaultValue={query.taskType ?? ''}>
            <option value="">All types</option>
            {vocabulary.taskTypes.map(option)}
          </select>
        </label>
        <details>
          <summary>More filters</summary>
          <div className="more-filters">
            <label>
              <span>Primary competency</span>
              <select name="competency" defaultValue={query.competency ?? ''}>
                <option value="">All competencies</option>
                {vocabulary.competencies.map(option)}
              </select>
            </label>
            <label>
              <span>Compute tier</span>
              <select name="compute_tier" defaultValue={query.computeTier ?? ''}>
                <option value="">All compute tiers</option>
                {vocabulary.computeTiers.map(option)}
              </select>
            </label>
            <label>
              <span>Minimum minutes</span>
              <input
                type="number"
                name="expected_minutes_min"
                min="1"
                defaultValue={query.expectedMinutesMin}
              />
            </label>
            <label>
              <span>Maximum minutes</span>
              <input
                type="number"
                name="expected_minutes_max"
                min="1"
                defaultValue={query.expectedMinutesMax}
              />
            </label>
            <label>
              <span>Sort</span>
              <select name="sort" defaultValue={query.sort}>
                <option value="EDITORIAL">Learning path</option>
                <option value="NEWEST">Newest</option>
                <option value="EXPECTED_TIME">Expected time</option>
                <option value="TITLE">Title</option>
              </select>
            </label>
          </div>
        </details>
        <label className="checkbox-field">
          <input
            type="checkbox"
            name="include_subtopics"
            value="true"
            defaultChecked={query.includeSubtopics}
            disabled={!query.topic}
          />
          <span>Include subtopics</span>
        </label>
        <button className="apply-filters" type="submit">Apply filters</button>
        <a className="clear-filters" href="/problems">Clear filters</a>
      </form>

      <ul className="active-filters" aria-label="Active filters">
        {activeFilters.map(([key, label]) => (
          <li key={key}>
            <a
              href={withoutParameter(queryParams, key)}
              aria-label={`Remove ${filterName(key)}: ${label}`}
            >
              {label}<span aria-hidden="true"> ×</span>
            </a>
          </li>
        ))}
      </ul>

      <ul className="topic-shortcuts" aria-label="Topic family shortcuts">
        {families.map((topic) => (
          <li key={topic.code}>
            <a href={withParameter(queryParams, 'topic', topic.code)}>{topic.label}</a>
          </li>
        ))}
      </ul>

      <div className="results-placeholder" aria-label="Published problem results">
        {problemTitles.length ? (
          <ul>{problemTitles.map((title) => <li key={title}>{title}</li>)}</ul>
        ) : (
          <p>No published problems match these filters.</p>
        )}
      </div>
    </section>
  );
}

const option = (item: VocabularyOption) => (
  <option key={item.code} value={item.code}>{item.label}</option>
);

const topicPath = (topic: TopicOption, topics: TopicOption[]): string => {
  const byCode = new Map(topics.map((item) => [item.code, item]));
  const labels = [topic.label];
  let parent = topic.parentCode ? byCode.get(topic.parentCode) : undefined;
  while (parent) {
    labels.unshift(parent.label);
    parent = parent.parentCode ? byCode.get(parent.parentCode) : undefined;
  }
  return labels.join(' › ');
};

const toSearchParams = (query: PublicProblemQuery): URLSearchParams => {
  const parameters = new URLSearchParams();
  const values: Array<[string, string | number | boolean | undefined]> = [
    ['stage', query.stage], ['q', query.search], ['competency', query.competency],
    ['topic', query.topic], ['include_subtopics', query.includeSubtopics || undefined],
    ['difficulty', query.difficulty], ['task_type', query.taskType],
    ['compute_tier', query.computeTier],
    ['expected_minutes_min', query.expectedMinutesMin],
    ['expected_minutes_max', query.expectedMinutesMax],
    ['sort', query.sort === 'EDITORIAL' ? undefined : query.sort],
    ['page', query.page === 1 ? undefined : query.page],
    ['page_size', query.pageSize === 25 ? undefined : query.pageSize],
  ];
  for (const [key, value] of values) {
    if (value !== undefined) parameters.set(key, String(value));
  }
  return parameters;
};

const withParameter = (
  current: URLSearchParams,
  key: string,
  value: string,
): string => {
  const next = new URLSearchParams(current);
  next.set(key, value);
  next.delete('page');
  return `/problems?${next.toString()}`;
};

const withoutParameter = (current: URLSearchParams, key: string): string => {
  const next = new URLSearchParams(current);
  next.delete(key);
  if (key === 'topic') next.delete('include_subtopics');
  next.delete('page');
  const suffix = next.toString();
  return suffix ? `/problems?${suffix}` : '/problems';
};

const activeFilterEntries = (
  query: PublicProblemQuery,
  vocabulary: ProblemVocabulary,
): Array<[string, string]> => {
  const labels = new Map([
    ...vocabulary.stages, ...vocabulary.topics, ...vocabulary.competencies,
    ...vocabulary.difficulties, ...vocabulary.taskTypes, ...vocabulary.computeTiers,
  ].map((item) => [item.code, item.label]));
  return [
    query.search ? ['q', query.search] : undefined,
    query.topic ? ['topic', labels.get(query.topic) ?? query.topic] : undefined,
    query.difficulty ? ['difficulty', labels.get(query.difficulty) ?? query.difficulty] : undefined,
    query.taskType ? ['task_type', labels.get(query.taskType) ?? query.taskType] : undefined,
    query.competency ? ['competency', labels.get(query.competency) ?? query.competency] : undefined,
    query.computeTier ? ['compute_tier', labels.get(query.computeTier) ?? query.computeTier] : undefined,
    query.expectedMinutesMin ? ['expected_minutes_min', `At least ${query.expectedMinutesMin} min`] : undefined,
    query.expectedMinutesMax ? ['expected_minutes_max', `At most ${query.expectedMinutesMax} min`] : undefined,
  ].filter((item): item is [string, string] => item !== undefined);
};

const filterName = (key: string): string => ({
  q: 'search', topic: 'topic', difficulty: 'difficulty', task_type: 'type',
  competency: 'competency', compute_tier: 'compute tier',
  expected_minutes_min: 'minimum time', expected_minutes_max: 'maximum time',
})[key] ?? key;
