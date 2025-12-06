/**
 * useAuth Hook
 * Convenient hook to access auth store
 */

import { useAuthStore } from '@/store/authStore';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    logoutAll,
    loadUser,
    clearError,
    checkAuthStatus,
  } = useAuthStore();

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    logoutAll,
    loadUser,
    clearError,
    checkAuthStatus,
  };
};
