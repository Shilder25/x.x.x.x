export const API_BASE_URL = '';

export function getApiUrl(endpoint: string): string {
  if (endpoint.startsWith('/')) {
    return endpoint;
  }
  return `/${endpoint}`;
}
