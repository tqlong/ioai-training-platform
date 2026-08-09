import { createApiClient } from '@ioai/api-client';

const configuredBase = typeof window === 'undefined'
  ? process.env.API_INTERNAL_BASE ?? 'http://127.0.0.1:8000'
  : '';
const baseUrl = `${configuredBase.replace(/\/$/, '')}/api/v1`;

export const studioApi = createApiClient({ baseUrl });
