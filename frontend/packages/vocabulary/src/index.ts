import type { AuthorVocabularyRecord } from '@ioai/api-client';

import vocabularyArtifact from './generated/vocabulary.json' with { type: 'json' };

export type CanonicalVocabularyRecord =
  (typeof vocabularyArtifact.records)[number];

export const canonicalVocabularyRecords = vocabularyArtifact.records;

export const identityKey = (
  record: Pick<CanonicalVocabularyRecord, 'vocabulary_type' | 'code'>,
): string => `${record.vocabulary_type}:${record.code}`;

export const vocabularyRoots = (
  vocabularyType: string,
): CanonicalVocabularyRecord[] =>
  canonicalVocabularyRecords.filter(
    (record) =>
      record.vocabulary_type === vocabularyType && record.parent_code === null,
  );

export const isAuthorValueAvailable = (
  record: AuthorVocabularyRecord,
): boolean => record.availability.is_available;
