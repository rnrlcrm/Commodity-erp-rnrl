/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { CompanyLogo } from '@/components/common/CompanyLogo';

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
          <CompanyLogo size="sm" className="mx-auto mb-4 drop-shadow-[0_0_24px_rgba(59,130,246,0.35)] animate-pulse" />
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
