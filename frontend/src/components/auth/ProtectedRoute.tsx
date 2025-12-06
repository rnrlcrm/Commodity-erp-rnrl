/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, loadUser, checkAuthStatus } = useAuth();
  const location = useLocation();

  useEffect(() => {
    // On mount, try to load user from storage/API
    if (!isAuthenticated && checkAuthStatus()) {
      loadUser();
    }
  }, [isAuthenticated, loadUser, checkAuthStatus]);

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-pearl-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-sun-400 via-saturn-500 to-mars-500 shadow-xl shadow-saturn-500/30 mb-4 animate-pulse">
            <span className="text-white font-heading font-bold text-2xl">RN</span>
          </div>
          <p className="text-saturn-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Render protected content
  return <>{children}</>;
}
