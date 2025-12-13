/**
 * Sessions Management Page
 * View and manage active login sessions across devices
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '@/services/api/authService';
import type { UserSession } from '@/types/auth';
import { Button } from '@/components/2040/Button';
import { HoloPanel } from '@/components/2040/HoloPanel';
import { VolumetricBadge } from '@/components/2040/VolumetricTable';
import SettingsSceneLayout from './components/SettingsSceneLayout';
import {
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  DeviceTabletIcon,
  MapPinIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

export function SessionsPage() {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    void loadSessions();
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
    if (!confirm('Logout this device? It will lose access immediately.')) {
      return;
    }

    setDeletingId(sessionId);

    try {
      await authService.logoutSession(sessionId);
      setSessions((prev) => prev.filter((session) => session.id !== sessionId));
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

  const renderBody = () => {
    if (isLoading) {
      return (
        <HoloPanel theme="space" className="p-12 text-center text-pearl-200">
          Synchronising active sessions…
        </HoloPanel>
      );
    }

    if (sessions.length === 0) {
      return (
        <HoloPanel theme="space" className="p-12 text-center text-pearl-200">
          No active sessions detected.
        </HoloPanel>
      );
    }

    return (
      <div className="space-y-4">
        <HoloPanel
          theme="space"
          className="flex flex-wrap items-center justify-between gap-4 border border-white/5"
        >
          <div>
            <h3 className="text-lg font-heading text-pearl-50">Session Overview</h3>
            <p className="text-sm text-pearl-300/80">Monitor connected devices and revoke anomalies instantly.</p>
          </div>
          <VolumetricBadge status="active">
            {sessions.length} active {sessions.length === 1 ? 'session' : 'sessions'}
          </VolumetricBadge>
        </HoloPanel>

        <div className="space-y-4">
          {sessions.map((session) => {
            const DeviceIcon = getDeviceIcon(session.device_type);

            return (
              <HoloPanel
                key={session.id}
                theme="space"
                elevated
                className="flex flex-col gap-5 border border-white/5 p-5 md:flex-row md:items-start md:justify-between"
              >
                <div className="flex flex-1 items-start gap-4">
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${
                      session.is_current
                        ? 'from-sun-400 to-sun-600 shadow-[0_0_35px_rgba(255,209,84,0.35)]'
                        : 'from-saturn-500 to-saturn-700 shadow-[0_0_25px_rgba(95,99,251,0.25)]'
                    }`}
                  >
                    <DeviceIcon className="h-6 w-6 text-white" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-3">
                      <h3 className="text-lg font-heading text-pearl-50">{session.device_name}</h3>
                      <VolumetricBadge status={session.is_current ? 'completed' : 'active'}>
                        {session.is_current ? 'Current Device' : 'Remote Session'}
                      </VolumetricBadge>
                    </div>
                    <p className="text-sm text-pearl-300/80">
                      {session.browser_name} {session.browser_version} • {session.device_os}
                    </p>
                    <div className="flex flex-wrap items-center gap-4 text-xs text-pearl-200/70">
                      <span className="inline-flex items-center gap-1">
                        <MapPinIcon className="h-4 w-4" />
                        {session.ip_address || 'Not available'}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <ClockIcon className="h-4 w-4" />
                        Last active {formatDate(session.last_active)}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <ClockIcon className="h-4 w-4" />
                        Created {formatDate(session.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                {!session.is_current && (
                  <div className="flex items-center gap-3 md:flex-col md:items-end">
                    <Button
                      type="button"
                      variant="danger"
                      sheen={false}
                      onClick={() => handleLogoutSession(session.id)}
                      disabled={deletingId === session.id}
                    >
                      {deletingId === session.id ? 'Revoking…' : 'Revoke Access'}
                    </Button>
                  </div>
                )}
              </HoloPanel>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <SettingsSceneLayout
      title="Session Security"
      subtitle="Audit connected clients and terminate suspicious presences"
      actions={
        <Link to="/2040/settings/2fa" className="inline-block">
          <Button sheen={false} variant="secondary">
            Configure 2FA
          </Button>
        </Link>
      }
    >
      <div className="space-y-6">
        {error && (
          <HoloPanel theme="mars" className="flex items-start gap-3 border border-white/10 px-4 py-3 text-sm text-pearl-50">
            <ExclamationTriangleIcon className="h-5 w-5 flex-shrink-0" />
            <span>{error}</span>
          </HoloPanel>
        )}
        {renderBody()}
      </div>
    </SettingsSceneLayout>
  );
}
