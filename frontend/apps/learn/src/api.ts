import { createApiClient } from '@ioai/api-client';


const serverBase = process.env.API_INTERNAL_BASE
  ?? process.env.NEXT_PUBLIC_API_BASE
  ?? 'http://127.0.0.1:8000';
const configuredBase = typeof window === 'undefined'
  ? `${serverBase.replace(/\/$/, '')}/api/v1`
  : '/api/v1';

export const learnApi = createApiClient({
  baseUrl: configuredBase,
});
