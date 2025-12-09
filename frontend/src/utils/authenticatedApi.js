/**
 * Authenticated Backend API Client for Frontend
 * 
 * This utility ensures all frontend requests to the backend are authenticated
 * with proper identity tokens when running in Cloud Run.
 * 
 * For local development, use the local dev script to get tokens.
 */

const BACKEND_URL = import.meta.env.VITE_API_URL || 'https://backend-service-565186585906.us-central1.run.app';
const METADATA_SERVER_URL = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity';

/**
 * Gets an identity token from the GCP metadata server (Cloud Run only)
 * @param {string} audience - The target service URL
 * @returns {Promise<string>} Identity token
 */
async function getIdentityToken(audience) {
  try {
    const response = await fetch(`${METADATA_SERVER_URL}?audience=${audience}`, {
      headers: {
        'Metadata-Flavor': 'Google'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get identity token: ${response.status}`);
    }
    
    return await response.text();
  } catch (error) {
    console.error('Error getting identity token:', error);
    // In development, you might want to use a different auth method
    // or skip token for local backend
    if (import.meta.env.DEV) {
      console.warn('Running in dev mode - no identity token used');
      return null;
    }
    throw error;
  }
}

/**
 * Makes an authenticated request to the backend
 * @param {string} path - API path (e.g., '/api/v1/users')
 * @param {RequestInit} options - Fetch options
 * @returns {Promise<Response>}
 */
export async function authenticatedFetch(path, options = {}) {
  const url = `${BACKEND_URL}${path}`;
  
  // Get identity token for production
  let token = null;
  if (!import.meta.env.DEV) {
    token = await getIdentityToken(BACKEND_URL);
  }
  
  // Merge headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Add authorization header if we have a token
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Make the request
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  return response;
}

/**
 * Convenience methods for common HTTP verbs
 */
export const api = {
  get: (path, options = {}) => authenticatedFetch(path, { ...options, method: 'GET' }),
  
  post: (path, data, options = {}) => authenticatedFetch(path, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  put: (path, data, options = {}) => authenticatedFetch(path, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  patch: (path, data, options = {}) => authenticatedFetch(path, {
    ...options,
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  
  delete: (path, options = {}) => authenticatedFetch(path, {
    ...options,
    method: 'DELETE',
  }),
};

/**
 * Example usage:
 * 
 * import { api } from './utils/authenticatedApi';
 * 
 * // GET request
 * const response = await api.get('/api/v1/users');
 * const users = await response.json();
 * 
 * // POST request
 * const response = await api.post('/api/v1/users', { name: 'John' });
 * 
 * // With custom headers
 * const response = await api.get('/api/v1/users', {
 *   headers: { 'X-Custom-Header': 'value' }
 * });
 */
