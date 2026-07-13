export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export function getApiUrl(path) {
  if (path.startsWith('http')) {
    return path;
  }
  if (path.startsWith('/')) {
    return `${API_BASE_URL}${path}`;
  }
  return `${API_BASE_URL}/${path}`;
}