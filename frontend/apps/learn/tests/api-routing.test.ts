import { learnApi } from '../src/api';

it('uses the same-origin API rewrite in the browser bundle', () => {
  expect(learnApi.baseUrl).toBe('/api/v1');
});
