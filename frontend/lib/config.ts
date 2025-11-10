export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function getApiUrl(endpoint: string): string {
  if (endpoint.startsWith('/')) {
    return `${API_BASE_URL}${endpoint}`;
  }
  return `${API_BASE_URL}/${endpoint}`;
}
