/**
 * Auth Store - Zustand State Management
 * Handles authentication state, login, logout, and token management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services/api/authService';
import capabilitiesService from '@/services/api/capabilitiesService';
import type { LoginRequest, AuthState, AuthError } from '@/types/auth';

interface AuthActions {
  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  loadUser: () => Promise<void>;
  loadCapabilities: () => Promise<void>; // New: Load user capabilities
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  
  // Token management
  refreshAccessToken: () => Promise<void>;
  checkAuthStatus: () => boolean;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login action
      login: async (credentials: LoginRequest) => {
        console.log('[DEBUG] Login started with credentials:', { email: credentials.email, passwordLength: credentials.password?.length });
        set({ isLoading: true, error: null });

        try {
          console.log('[DEBUG] Calling authService.login...');
          const response = await authService.login(credentials);
          console.log('[DEBUG] Login response received:', response);

          // Check if 2FA is required
          if ('two_fa_required' in response && response.two_fa_required) {
            console.log('[DEBUG] 2FA required');
            set({
              isLoading: false,
              error: response.message,
            });
            return;
          }

          // Type guard - we know it's LoginResponse now
          const loginResponse = response as { access_token: string; refresh_token: string };
          console.log('[DEBUG] Tokens received, storing...');

          // Store tokens
          authService.storeTokens(loginResponse.access_token, loginResponse.refresh_token);

          // Fetch user details
          console.log('[DEBUG] Fetching current user...');
          const user = await authService.getCurrentUser();
          console.log('[DEBUG] User fetched:', user);
          authService.storeUser(user);

          // Fetch user capabilities and merge
          try {
            console.log('[DEBUG] Fetching capabilities...');
            const capabilitiesData = await capabilitiesService.getMyCapabilities();
            user.capabilities = capabilitiesData.capabilities || [];
            console.log('[DEBUG] Capabilities loaded:', user.capabilities?.length);
          } catch (capError) {
            console.warn('Failed to load capabilities, using empty array:', capError);
            user.capabilities = [];
          }

          console.log('[DEBUG] Login successful, updating state');
          set({
            user,
            accessToken: loginResponse.access_token,
            refreshToken: loginResponse.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          console.error('[DEBUG] Login error caught:', error);
          console.error('[DEBUG] Error response:', error.response);
          console.error('[DEBUG] Error data:', error.response?.data);
          console.error('[DEBUG] Error status:', error.response?.status);
          
          const authError: AuthError = {
            message: error.response?.data?.detail || 'Login failed',
            code: error.response?.status?.toString(),
            details: error.response?.data?.errors,
          };

          console.error('[DEBUG] AuthError created:', authError);

          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: authError.message,
          });

          throw authError;
        }
      },

      // Logout from current device
      logout: async () => {
        set({ isLoading: true });

        try {
          await authService.logout();
        } catch (error) {
          console.error('Logout error:', error);
          // Continue with local logout even if API call fails
        } finally {
          authService.clearStorage();
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      // Logout from all devices
      logoutAll: async () => {
        set({ isLoading: true });

        try {
          await authService.logoutAll();
        } catch (error) {
          console.error('Logout all error:', error);
        } finally {
          authService.clearStorage();
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      // Load user from storage or API
      loadUser: async () => {
        set({ isLoading: true });

        try {
          // Check if tokens exist in storage
          const { accessToken, refreshToken } = authService.getStoredTokens();
          
          if (!accessToken || !refreshToken) {
            set({ isLoading: false });
            return;
          }

          // Try to get user from storage first
          let user = authService.getStoredUser();

          // If not in storage, fetch from API
          if (!user) {
            user = await authService.getCurrentUser();
            authService.storeUser(user);
          }

          // Always fetch fresh capabilities
          try {
            const capabilitiesData = await capabilitiesService.getMyCapabilities();
            user.capabilities = capabilitiesData.capabilities || [];
          } catch (capError) {
            console.warn('Failed to load capabilities:', capError);
            user.capabilities = user.capabilities || [];
          }

          set({
            user,
            accessToken,
            refreshToken,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          // Token invalid or expired - clear storage
          authService.clearStorage();
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      // Refresh access token
      refreshAccessToken: async () => {
        const { refreshToken } = get();

        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        try {
          const response = await authService.refreshToken(refreshToken);

          authService.storeTokens(response.access_token, response.refresh_token);

          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
          });
        } catch (error) {
          // Refresh failed - logout user
          authService.clearStorage();
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            error: 'Session expired. Please login again.',
          });

          throw error;
        }
      },

      // Check if user is authenticated
      checkAuthStatus: () => {
        const { accessToken, refreshToken } = authService.getStoredTokens();
        return !!(accessToken && refreshToken);
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Set loading
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      // Load capabilities for current user
      loadCapabilities: async () => {
        const { user } = get();
        if (!user) return;

        try {
          const capabilitiesData = await capabilitiesService.getMyCapabilities();
          set({
            user: {
              ...user,
              capabilities: capabilitiesData.capabilities || [],
            },
          });
        } catch (error) {
          console.error('Failed to load capabilities:', error);
        }
      },
    }),
    {
      name: 'rnrl-auth-storage',
      partialize: (state) => ({
        // Only persist these fields
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
