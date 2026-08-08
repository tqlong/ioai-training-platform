export type ApiClient = {
  baseUrl: string;
};

export const createApiClient = ({ baseUrl }: ApiClient): ApiClient => ({
  baseUrl,
});
