import { ioaiUiVersion } from '../src';

import { describe, expect, it } from 'vitest';

describe('ui', () => {
  it('exposes a visible version token', () => {
    expect(ioaiUiVersion).toBeTruthy();
  });
});
