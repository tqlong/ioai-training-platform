'use client';

import { createApiClient, type ApiClient } from '@ioai/api-client';
import { useEffect, useState } from 'react';

import { browserProgressAdapter, LEARNER_PROGRESS_KEY, parseLearnerProgress } from '../learner-progress';

const EMPTY_LABELS: Record<string, string> = {};

export type StarterRecommendation = {
  slug: string;
  title: string;
  objective: string;
  stageCode?: string;
  stageLabel: string;
  difficultyLabel: string;
  expectedMinutes: number;
  computeLabel: string;
};

type StorageReader = Pick<Storage, 'getItem'>;
type RecentProblem = { slug: string; title: string };
type SuggestedTopic = { code: string; label: string };
export type LearningGuidanceContext = {
  schemaVersion: 1;
  weeklyGoal?: { target: number; completed: number };
  currentPath?: { label: string; completed: number; total: number };
  prerequisites: string[];
  recentCompleted: RecentProblem[];
  suggestedTopics: SuggestedTopic[];
};

type LearningGuidanceProps = {
  starter: StarterRecommendation;
  storage?: StorageReader;
  api?: Pick<ApiClient, 'getPublicRecommendation'>;
  labels?: Record<string, string>;
};

const browserApi = createApiClient({ baseUrl: '/api/v1' });

export function LearningGuidance({
  starter,
  storage,
  api = browserApi,
  labels = EMPTY_LABELS,
}: LearningGuidanceProps) {
  const [context, setContext] = useState<LearningGuidanceContext | null>(null);
  const [recommendation, setRecommendation] = useState(starter);
  const [recommendationLabel, setRecommendationLabel] = useState('Recommended start');
  const [reason, setReason] = useState('First published problem in this stage.');

  useEffect(() => {
    const restored = storage
      ? parseLearningGuidanceContext(storage.getItem(LEARNER_PROGRESS_KEY))
      : browserProgressAdapter()?.read().state ?? null;
    setContext(restored);
    const current = restored?.recentCompleted[0];
    if (!current || !starter.stageCode) return;
    void api.getPublicRecommendation(current.slug, {
      stage: starter.stageCode,
      completed: restored.recentCompleted.map((item) => item.slug),
    }).then((next) => {
      if (!next) return;
      setRecommendation({
        slug: next.slug,
        title: next.title.en,
        objective: next.reason,
        stageCode: next.stage_code,
        stageLabel: labels[next.stage_code] ?? next.stage_code,
        difficultyLabel: labels[next.difficulty_code] ?? next.difficulty_code,
        expectedMinutes: next.expected_minutes,
        computeLabel: labels[next.compute_tier_code] ?? next.compute_tier_code,
      });
      setRecommendationLabel(next.label);
      setReason(next.reason);
    }).catch(() => undefined);
  }, [api, labels, starter, storage]);

  return (
    <div className="learning-guidance">
      <article className="recommendation-card" aria-labelledby="recommendation-title">
        <p className="recommendation-label">{recommendationLabel}</p>
        <h2 id="recommendation-title">{recommendation.title}</h2>
        <p>{recommendation.objective}</p>
        <p className="recommendation-meta">
          {recommendation.stageLabel} · {recommendation.difficultyLabel}
        </p>
        <p className="recommendation-meta">
          {recommendation.expectedMinutes} min · {recommendation.computeLabel}
        </p>
        <div className="recommendation-actions">
          <a href={`/problems/${recommendation.slug}`}>Continue problem</a>
          <details>
            <summary>Why this?</summary>
            <p>{reason}</p>
          </details>
        </div>
      </article>

      <aside className="learning-sidebar" aria-label="Learning path guidance">
        <section>
          <h2>Weekly goal</h2>
          {context?.weeklyGoal ? (
            <p>{context.weeklyGoal.completed} of {context.weeklyGoal.target} completed</p>
          ) : <p>Set a weekly goal when you are ready.</p>}
        </section>
        <section>
          <h2>Current path</h2>
          {context?.currentPath ? (
            <p>{context.currentPath.label} — {context.currentPath.completed} of {context.currentPath.total}</p>
          ) : <p>Start with the recommended problem.</p>}
        </section>
        {context?.prerequisites.length ? (
          <section>
            <h2>Prerequisites to review</h2>
            <ul>{context.prerequisites.map((item) => (
              <li key={item} data-testid="prerequisite-review">{item}</li>
            ))}</ul>
          </section>
        ) : null}
        {context?.recentCompleted.length ? (
          <section>
            <h2>Recently completed</h2>
            <ul>{context.recentCompleted.map((item) => (
              <li key={item.slug} data-testid="recent-completion">
                <a href={`/problems/${item.slug}`}>{item.title}</a>
              </li>
            ))}</ul>
          </section>
        ) : null}
        {context?.suggestedTopics.length ? (
          <section>
            <h2>Suggested next topics</h2>
            <ul>{context.suggestedTopics.map((item) => (
              <li key={item.code} data-testid="suggested-topic">
                <a href={`/problems?topic=${encodeURIComponent(item.code)}`}>{item.label}</a>
              </li>
            ))}</ul>
          </section>
        ) : null}
      </aside>
    </div>
  );
}

export const parseLearningGuidanceContext = (
  raw: string | null,
): LearningGuidanceContext | null => parseLearnerProgress(raw);
