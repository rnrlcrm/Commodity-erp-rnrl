/**
 * Sessions Management Page
 * View and manage active login sessions across devices
 */

import { useState, useEffect } from 'react';
import { authService } from '@/services/api/authService';
import type { UserSession } from '@/types/auth';
import {
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  DeviceTabletIcon,
  MapPinIcon,
  ClockIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

export function SessionsPage() {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Fetch sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.getSessions();
      setSessions(response.sessions);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load sessions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogoutSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to logout from this device?')) {
      return;
    }

    setDeletingId(sessionId);

    try {
      await authService.logoutSession(sessionId);
      // Remove from UI
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to logout session');
    } finally {
      setDeletingId(null);
    }
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType) {
      case 'mobile':
        return DevicePhoneMobileIcon;
      case 'tablet':
        return DeviceTabletIcon;
      default:
        return ComputerDesktopIcon;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-heading font-bold text-saturn-900">Active Sessions</h1>
        <p className="text-saturn-600 mt-2">
          Manage your active login sessions across all devices
        </p>
      </div>

      {/* Error message */}
      {error && (
        <div className="p-4 bg-mars-50 border border-mars-200 rounded-xl flex items-start gap-3">
          <ExclamationTriangleIcon className="w-5 h-5 text-mars-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-mars-900">{error}</p>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-flex items-center gap-2 text-saturn-600">
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading sessions...
          </div>
        </div>
      )}

      {/* Sessions list */}
      {!isLoading && sessions.length === 0 && (
        <div className="text-center py-12 glass-neo border border-saturn-200/50 rounded-2xl">
          <p className="text-saturn-600">No active sessions found</p>
        </div>
      )}

      {!isLoading && sessions.length > 0 && (
        <div className="space-y-4">
          {sessions.map((session) => {
            const DeviceIcon = getDeviceIcon(session.device_type);
            
            return (
              <div
                key={session.id}
                className={`p-6 glass-neo border rounded-2xl transition-all duration-150 ${
                  session.is_current
                    ? 'border-sun-300 bg-sun-50/30'
                    : 'border-saturn-200/50 hover:border-saturn-300'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Device icon */}
                  <div className={`p-3 rounded-xl ${
                    session.is_current ? 'bg-sun-100' : 'bg-saturn-100'
                  }`}>
                    <DeviceIcon className={`w-6 h-6 ${
                      session.is_current ? 'text-sun-600' : 'text-saturn-600'
                    }`} />
                  </div>

                  {/* Session info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-heading font-bold text-saturn-900 flex items-center gap-2">
                          {session.device_name}
                          {session.is_current && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-sun-100 text-sun-700 text-xs font-medium rounded-full border border-sun-200">
                              <CheckCircleIcon className="w-3 h-3" />
                              Current
                            </span>
                          )}
                        </h3>
                        <p className="text-sm text-saturn-600 mt-1">
                          {session.browser_name} {session.browser_version} • {session.device_os}
                        </p>
                      </div>

                      {/* Logout button */}
                      {!session.is_current && (
                        <button
                          onClick={() => handleLogoutSession(session.id)}
                          disabled={deletingId === session.id}
                          className="p-2 hover:bg-mars-50 rounded-lg transition-all duration-120 group disabled:opacity-50"
                          title="Logout from this device"
                        >
                          <XMarkIcon className="w-5 h-5 text-saturn-400 group-hover:text-mars-600" />
                        </button>
                      )}
                    </div>

                    {/* Additional info */}
                    <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-saturn-500">
                      <div className="flex items-center gap-1">
                        <MapPinIcon className="w-4 h-4" />
                        <span>{session.ip_address}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <ClockIcon className="w-4 h-4" />
                        <span>Last active {formatDate(session.last_active)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-saturn-400">•</span>
                        <span>Created {formatDate(session.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Total count */}
      {!isLoading && sessions.length > 0 && (
        <div className="text-center text-sm text-saturn-500">
          {sessions.length} active {sessions.length === 1 ? 'session' : 'sessions'}
        </div>
      )}
    </div>
  );
}
