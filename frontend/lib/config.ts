// Use NEXT_PUBLIC_API_URL in production (Railway), empty string in development (Replit)
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export function getApiUrl(endpoint: string): string {
  // If we have a full API URL (Railway production), use it
  if (API_BASE_URL) {
    // Remove leading slash from endpoint if present
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${API_BASE_URL}/${cleanEndpoint}`;
  }
  
  // Otherwise use relative paths (Replit development with internal rewrites)
  if (endpoint.startsWith('/')) {
    return endpoint;
  }
  return `/${endpoint}`;
}
