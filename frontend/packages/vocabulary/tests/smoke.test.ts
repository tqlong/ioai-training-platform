import { reservedVocabularyRootCodes } from '../src';

import { describe, expect, it } from 'vitest';

describe('vocabulary', () => {
  it('starts with deterministic vocabulary roots', () => {
    expect(Array.isArray(reservedVocabularyRootCodes)).toBe(true);
  });
});
