import { createApiClient } from '@ioai/api-client';


const configuredBase = process.env.API_INTERNAL_BASE
  ?? process.env.NEXT_PUBLIC_API_BASE
  ?? 'http://127.0.0.1:8000';

export const learnApi = createApiClient({
  baseUrl: `${configuredBase.replace(/\/$/, '')}/api/v1`,
});
