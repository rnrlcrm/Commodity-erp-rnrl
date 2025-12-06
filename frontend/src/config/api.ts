/**
 * API Configuration
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  API_VERSION: '/api/v1',
  TIMEOUT: 30000,
  
  // Token configuration
  TOKEN_STORAGE_KEY: 'rnrl_access_token',
  REFRESH_TOKEN_STORAGE_KEY: 'rnrl_refresh_token',
  USER_STORAGE_KEY: 'rnrl_user',
  
  // Refresh token timing (refresh 5 minutes before expiry)
  TOKEN_REFRESH_BUFFER: 5 * 60 * 1000, // 5 minutes in ms
} as const;

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/settings/auth/login',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    LOGOUT_ALL: '/auth/sessions/all',
    ME: '/settings/auth/me',
    CHANGE_PASSWORD: '/settings/auth/change-password',
  },
  
  // Session management
  SESSIONS: {
    LIST: '/auth/sessions',
    DELETE: (sessionId: string) => `/auth/sessions/${sessionId}`,
    DELETE_ALL: '/auth/sessions/all',
  },
} as const;
