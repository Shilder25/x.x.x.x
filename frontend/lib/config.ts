export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://keen-essence-production.up.railway.app';

export function getApiUrl(endpoint: string): string {
  if (endpoint.startsWith('/')) {
    return `${API_BASE_URL}${endpoint}`;
  }
  return `${API_BASE_URL}/${endpoint}`;
}
