/**
 * Axios Instance with Interceptors
 * Handles token attachment, refresh, and error handling
 * Supports Cloud Run identity tokens for service-to-service authentication
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG } from '@/config/api';

// GCP Metadata server for identity tokens (Cloud Run only)
const METADATA_SERVER_URL = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity';
const isProduction = import.meta.env.PROD;

// Cache for identity token
let cachedIdentityToken: string | null = null;
let tokenExpiry: number = 0;

/**
 * Get identity token from GCP metadata server (Cloud Run only)
 */
async function getIdentityToken(): Promise<string | null> {
  // Skip in development
  if (!isProduction) {
    return null;
  }

  // Return cached token if still valid (with 5 min buffer)
  if (cachedIdentityToken && Date.now() < tokenExpiry - 5 * 60 * 1000) {
    return cachedIdentityToken;
  }

  try {
    const response = await fetch(`${METADATA_SERVER_URL}?audience=${API_CONFIG.BASE_URL}`, {
      headers: {
        'Metadata-Flavor': 'Google'
      }
    });

    if (!response.ok) {
      console.warn('Failed to get identity token from metadata server');
      return null;
    }

    const token = await response.text();
    
    // Parse token to get expiry (tokens are valid for 1 hour)
    cachedIdentityToken = token;
    tokenExpiry = Date.now() + 60 * 60 * 1000; // 1 hour
    
    return token;
  } catch (error) {
    console.warn('Error getting identity token:', error);
    return null;
  }
}

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_CONFIG.BASE_URL}${API_CONFIG.API_VERSION}`,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Request interceptor - attach token (user JWT or identity token)
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // First, try to get user JWT token from localStorage (for authenticated users)
    const token = localStorage.getItem(API_CONFIG.TOKEN_STORAGE_KEY);
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    } else if (isProduction && config.headers) {
      // In production without user token, use identity token for service-to-service auth
      const identityToken = await getIdentityToken();
      if (identityToken) {
        config.headers.Authorization = `Bearer ${identityToken}`;
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If error is not 401 or no original request, reject immediately
    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    // If already retried, reject
    if (originalRequest._retry) {
      // Clear tokens and redirect to login
      localStorage.removeItem(API_CONFIG.TOKEN_STORAGE_KEY);
      localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_STORAGE_KEY);
      localStorage.removeItem(API_CONFIG.USER_STORAGE_KEY);
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // If already refreshing, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return apiClient(originalRequest);
        })
        .catch((err) => {
          return Promise.reject(err);
        });
    }

    // Start refresh process
    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem(API_CONFIG.REFRESH_TOKEN_STORAGE_KEY);

    if (!refreshToken) {
      isRefreshing = false;
      localStorage.removeItem(API_CONFIG.TOKEN_STORAGE_KEY);
      localStorage.removeItem(API_CONFIG.USER_STORAGE_KEY);
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      // Refresh token
      const response = await axios.post(
        `${API_CONFIG.BASE_URL}${API_CONFIG.API_VERSION}/auth/refresh`,
        { refresh_token: refreshToken },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const { access_token, refresh_token: newRefreshToken } = response.data;

      // Store new tokens
      localStorage.setItem(API_CONFIG.TOKEN_STORAGE_KEY, access_token);
      localStorage.setItem(API_CONFIG.REFRESH_TOKEN_STORAGE_KEY, newRefreshToken);

      // Update header for original request
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
      }

      // Process queued requests
      processQueue(null, access_token);
      isRefreshing = false;

      // Retry original request
      return apiClient(originalRequest);
    } catch (refreshError) {
      // Refresh failed - logout user
      processQueue(refreshError as Error, null);
      isRefreshing = false;

      localStorage.removeItem(API_CONFIG.TOKEN_STORAGE_KEY);
      localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_STORAGE_KEY);
      localStorage.removeItem(API_CONFIG.USER_STORAGE_KEY);
      
      window.location.href = '/login';
      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;
