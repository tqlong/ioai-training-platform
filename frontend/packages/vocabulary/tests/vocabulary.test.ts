import { describe, expect, it } from 'vitest';

import {
  canonicalVocabularyRecords,
  identityKey,
  isAuthorValueAvailable,
  vocabularyRoots,
} from '../src';

describe('canonical vocabulary package', () => {
  it('consumes every generated artifact record with bilingual labels', () => {
    expect(canonicalVocabularyRecords).toHaveLength(343);
    expect(
      canonicalVocabularyRecords.find(
        (record) => record.code === 'AI_1_FOUNDATIONS',
      )?.labels,
    ).toEqual({ en: 'AI Foundations', vi: 'Nền tảng AI' });
  });

  it('preserves composite identity when canonical codes overlap', () => {
    const transformers = canonicalVocabularyRecords.filter(
      (record) => record.code === 'DL_TRANSFORMERS',
    );

    expect(transformers.map(identityKey)).toEqual([
      'COMPETENCY:DL_TRANSFORMERS',
      'TOPIC:DL_TRANSFORMERS',
    ]);
  });

  it('derives hierarchy roots and aliases from generated data', () => {
    const roots = vocabularyRoots('TOPIC');

    expect(roots.some((record) => record.code === 'TOPIC_MATHEMATICS')).toBe(true);
    expect(roots.every((record) => record.parent_code === null)).toBe(true);
    expect(canonicalVocabularyRecords.every((record) => Array.isArray(record.aliases))).toBe(
      true,
    );
  });

  it('reads availability from the generated author API contract', () => {
    expect(
      isAuthorValueAvailable({
        identity: { vocabulary_type: 'TASK_TYPE', code: 'MODEL_TRAINING' },
        labels: { en: 'Model training', vi: 'Huấn luyện mô hình' },
        aliases: [],
        parent_identity: null,
        breadcrumbs: [],
        status: 'ACTIVE',
        availability: {
          is_available: false,
          reason_code: 'UNAVAILABLE_IN_RELEASE_0',
          message: 'Unavailable.',
        },
      }),
    ).toBe(false);
  });
});
