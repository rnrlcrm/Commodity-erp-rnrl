/**
 * Profile & Settings Page
 * User profile information and security settings
 */

import { useState, useEffect, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { authService } from '@/services/api/authService';
import { PasswordStrengthMeter } from '@/components/auth/PasswordStrengthMeter';
import { Button } from '@/components/2040/Button';
import { HoloPanel } from '@/components/2040/HoloPanel';
import { VolumetricBadge } from '@/components/2040/VolumetricTable';
import SettingsSceneLayout from './components/SettingsSceneLayout';
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/react/24/outline';

export function ProfilePage() {
  const { user } = useAuth();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [mfaStatus, setMfaStatus] = useState<'loading' | 'enabled' | 'disabled' | 'unavailable'>('loading');

  useEffect(() => {
    let active = true;

    const loadMfaStatus = async () => {
      try {
        const response = await authService.get2FAStatus();
        if (active) {
          setMfaStatus(response.enabled ? 'enabled' : 'disabled');
        }
      } catch (error) {
        if (active) {
          setMfaStatus('unavailable');
        }
      }
    };

    void loadMfaStatus();

    return () => {
      active = false;
    };
  }, []);

  const handlePasswordChange = async (event: FormEvent) => {
    event.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(false);

    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    setIsChangingPassword(true);

    try {
      await authService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      setPasswordSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');

      setTimeout(() => setPasswordSuccess(false), 5000);
    } catch (error: any) {
      setPasswordError(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const initials = user?.full_name?.substring(0, 2).toUpperCase() || 'U';

  return (
    <SettingsSceneLayout
      title="Account Settings"
      subtitle="Control identity, credentials, and platform security"
      actions={
        <>
          <Link to="/2040/settings/sessions" className="inline-block">
            <Button variant="secondary" sheen={false}>
              Manage Sessions
            </Button>
          </Link>
          <Link to="/2040/settings/2fa" className="inline-block">
            <Button>Configure 2FA</Button>
          </Link>
        </>
      }
    >
      <div className="space-y-8">
        <div className="grid gap-4 lg:grid-cols-3">
          <HoloPanel
            theme="space"
            elevated
            className="flex flex-col items-center gap-4 border border-white/5 text-center"
          >
            <div className="flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-sun-400 via-saturn-500 to-mars-500 text-3xl font-heading text-white shadow-holo">
              {initials}
            </div>
            <div className="space-y-1">
              <h3 className="text-xl font-heading text-pearl-50">{user?.full_name || 'Unidentified User'}</h3>
              <p className="text-sm text-pearl-300/80">{user?.role || user?.user_type || 'Role unknown'}</p>
            </div>
            <VolumetricBadge status={user?.is_active ? 'active' : 'failed'}>
              {user?.is_active ? 'Active Account' : 'Inactive Account'}
            </VolumetricBadge>
          </HoloPanel>

          <HoloPanel theme="space" className="lg:col-span-2 space-y-5 border border-white/5">
            <div className="grid gap-5 md:grid-cols-2">
              {[{
                label: 'Email Address',
                value: user?.email,
              },
              {
                label: 'User Type',
                value: user?.user_type,
              },
              {
                label: 'Account ID',
                value: user?.id,
                monospaced: true,
              },
              {
                label: 'Organization ID',
                value: user?.organization_id,
                monospaced: true,
              }].map(({ label, value, monospaced }) => (
                <div key={label}>
                  <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">{label}</p>
                  <p
                    className={`mt-2 text-lg text-pearl-50 ${
                      monospaced ? 'font-mono text-base tracking-[0.2em]' : ''
                    }`}
                  >
                    {value || '—'}
                  </p>
                </div>
              ))}
            </div>

            <div className="grid gap-5 md:grid-cols-2">
                <div>
                  <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">Account Created</p>
                  <p className="mt-2 text-sm text-pearl-200/90">
                    {user?.created_at
                      ? new Date(user.created_at).toLocaleString()
                      : 'Not recorded'}
                  </p>
                </div>
              <div>
                <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">MFA Status</p>
                <p className="mt-2 text-sm text-pearl-200/90">
                  {mfaStatus === 'loading'
                    ? 'Checking…'
                    : mfaStatus === 'enabled'
                    ? 'Enabled'
                    : mfaStatus === 'disabled'
                    ? 'Disabled'
                    : 'Unavailable'}
                </p>
              </div>
            </div>
          </HoloPanel>
        </div>

        <HoloPanel theme="space" className="space-y-6 border border-white/5">
          <div className="space-y-2">
            <h3 className="text-xl font-heading text-pearl-50">Credential Rotation</h3>
            <p className="text-sm text-pearl-300/80">
              Update your secret phrase regularly to maintain compliance with security policy.
            </p>
          </div>

          {passwordSuccess && (
            <div className="flex items-start gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
              <CheckCircleIcon className="h-5 w-5 flex-shrink-0" />
              <span>Password changed successfully.</span>
            </div>
          )}

          {passwordError && (
            <div className="flex items-start gap-3 rounded-xl border border-mars-500/30 bg-mars-500/10 px-4 py-3 text-sm text-mars-200">
              <ExclamationCircleIcon className="h-5 w-5 flex-shrink-0" />
              <span>{passwordError}</span>
            </div>
          )}

          <form onSubmit={handlePasswordChange} className="grid gap-5 md:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="current-password" className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">
                Current Password
              </label>
              <div className="relative">
                <input
                  id="current-password"
                  type={showCurrentPassword ? 'text' : 'password'}
                  value={currentPassword}
                  onChange={(event) => setCurrentPassword(event.target.value)}
                  required
                  className="w-full rounded-xl border border-white/10 bg-space-900/60 px-4 py-3 pr-12 text-pearl-100 placeholder-pearl-500 focus:border-saturn-400/60 focus:outline-none"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-3 flex items-center text-saturn-200/70 hover:text-pearl-100"
                  aria-label={showCurrentPassword ? 'Hide current password' : 'Show current password'}
                >
                  {showCurrentPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="new-password" className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">
                New Password
              </label>
              <div className="relative">
                <input
                  id="new-password"
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  required
                  minLength={8}
                  className="w-full rounded-xl border border-white/10 bg-space-900/60 px-4 py-3 pr-12 text-pearl-100 placeholder-pearl-500 focus:border-saturn-400/60 focus:outline-none"
                  placeholder="At least 8 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-3 flex items-center text-saturn-200/70 hover:text-pearl-100"
                  aria-label={showNewPassword ? 'Hide new password' : 'Show new password'}
                >
                  {showNewPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </button>
              </div>
              {newPassword && (
                <div className="mt-3">
                  <PasswordStrengthMeter password={newPassword} />
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="confirm-password" className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">
                Confirm New Password
              </label>
              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
                className="w-full rounded-xl border border-white/10 bg-space-900/60 px-4 py-3 text-pearl-100 placeholder-pearl-500 focus:border-saturn-400/60 focus:outline-none"
                placeholder="Repeat new password"
              />
            </div>

            <div className="flex items-end">
              <Button type="submit" disabled={isChangingPassword} className="w-full">
                {isChangingPassword ? 'Changing…' : 'Change Password'}
              </Button>
            </div>
          </form>
        </HoloPanel>
      </div>
    </SettingsSceneLayout>
  );
}
