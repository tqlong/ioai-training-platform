'use client';

import { createApiClient, type ApiClient } from '@ioai/api-client';
import { useEffect, useState } from 'react';


const STORAGE_KEY = 'ioai.learn.guidance.v1';
const MAX_STORAGE_LENGTH = 20_000;
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
    const source = storage ?? safeLocalStorage();
    if (!source) return;
    const restored = parseLearningGuidanceContext(source.getItem(STORAGE_KEY));
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
): LearningGuidanceContext | null => {
  if (!raw || raw.length > MAX_STORAGE_LENGTH) return null;
  try {
    const value: unknown = JSON.parse(raw);
    if (!isRecord(value) || value.schemaVersion !== 1) return null;
    const weeklyGoal = parseProgress(value.weeklyGoal, 365);
    const currentPath = parseCurrentPath(value.currentPath);
    if (value.weeklyGoal !== undefined && !weeklyGoal) return null;
    if (value.currentPath !== undefined && !currentPath) return null;
    return {
      schemaVersion: 1,
      weeklyGoal,
      currentPath,
      prerequisites: stringList(value.prerequisites, 3),
      recentCompleted: recentList(value.recentCompleted),
      suggestedTopics: topicList(value.suggestedTopics),
    };
  } catch {
    return null;
  }
};

const safeLocalStorage = (): StorageReader | undefined => {
  try {
    return window.localStorage;
  } catch {
    return undefined;
  }
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const boundedInteger = (value: unknown, maximum: number): value is number =>
  Number.isInteger(value) && typeof value === 'number' && value >= 0 && value <= maximum;

const parseProgress = (
  value: unknown,
  maximum: number,
): { target: number; completed: number } | undefined => {
  if (value === undefined) return undefined;
  if (!isRecord(value) || !boundedInteger(value.target, maximum) || value.target < 1) return undefined;
  if (!boundedInteger(value.completed, value.target)) return undefined;
  return { target: value.target, completed: value.completed };
};

const parseCurrentPath = (
  value: unknown,
): { label: string; completed: number; total: number } | undefined => {
  if (value === undefined) return undefined;
  if (!isRecord(value) || !shortText(value.label)) return undefined;
  if (!boundedInteger(value.total, 1_000) || value.total < 1) return undefined;
  if (!boundedInteger(value.completed, value.total)) return undefined;
  return { label: value.label, completed: value.completed, total: value.total };
};

const shortText = (value: unknown): value is string =>
  typeof value === 'string' && value.trim().length > 0 && value.length <= 160;

const stringList = (value: unknown, maximum: number): string[] =>
  Array.isArray(value) ? value.filter(shortText).slice(0, maximum) : [];

const recentList = (value: unknown): RecentProblem[] =>
  Array.isArray(value) ? value.filter((item): item is RecentProblem => (
    isRecord(item) && shortText(item.slug) && shortText(item.title)
  )).slice(0, 3) : [];

const topicList = (value: unknown): SuggestedTopic[] =>
  Array.isArray(value) ? value.filter((item): item is SuggestedTopic => (
    isRecord(item) && shortText(item.code) && shortText(item.label)
  )).slice(0, 2) : [];
