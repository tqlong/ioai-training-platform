import { createApiClient } from '@ioai/api-client';

const configuredBase = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8000';
const baseUrl = `${configuredBase.replace(/\/$/, '')}/api/v1`;

export const studioApi = createApiClient({ baseUrl });
