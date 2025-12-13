/**
 * Two-Factor Authentication Setup Page
 * Enable/disable 2FA with QR code and verification
 */

import { FormEvent, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '@/services/api/authService';
import { Button } from '@/components/2040/Button';
import { HoloPanel } from '@/components/2040/HoloPanel';
import { VolumetricBadge } from '@/components/2040/VolumetricTable';
import SettingsSceneLayout from './components/SettingsSceneLayout';
import {
  ShieldCheckIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

export function TwoFactorPage() {
  const [isEnabled, setIsEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [step, setStep] = useState<'status' | 'setup' | 'verify'>('status');

  useEffect(() => {
    void check2FAStatus();
  }, []);

  const check2FAStatus = async () => {
    try {
      const response = await authService.get2FAStatus();
      setIsEnabled(response.enabled);
    } catch (err) {
      console.error('Failed to check 2FA status:', err);
    }
  };

  const handleEnable2FA = async () => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await authService.setup2FA();
      setQrCode(response.qr_code);
      setSecret(response.secret);
      setStep('setup');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate 2FA setup');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyAndEnable = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await authService.verify2FA(verificationCode);
      setSuccess('Two-factor authentication enabled successfully.');
      setIsEnabled(true);
      setStep('status');
      setVerificationCode('');
      setQrCode(null);
      setSecret(null);

      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!confirm('Disable two-factor authentication? Your account will be less secure.')) {
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      await authService.disable2FA();
      setSuccess('Two-factor authentication disabled.');
      setIsEnabled(false);

      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disable 2FA');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setStep('status');
    setQrCode(null);
    setSecret(null);
    setVerificationCode('');
    setError(null);
  };

  const renderStep = () => {
    if (step === 'setup' && qrCode) {
      return (
        <HoloPanel theme="space" className="space-y-6 border border-white/5">
          <div className="text-center space-y-2">
            <h3 className="text-xl font-heading text-pearl-50">Scan Verification Glyph</h3>
            <p className="text-sm text-pearl-300/80">
              Use an authenticator like Google Authenticator or Authy to register this credential.
            </p>
          </div>

          <div className="flex justify-center">
            <div className="rounded-3xl border border-white/30 bg-pearl-50 p-6 shadow-holo">
              <img src={qrCode} alt="2FA QR Code" className="h-64 w-64" />
            </div>
          </div>

          {secret && (
            <div className="rounded-2xl border border-white/10 bg-space-900/60 p-4">
              <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">
                Manual Entry Code
              </p>
              <p className="mt-2 font-mono text-base tracking-[0.3em] text-pearl-100">{secret}</p>
            </div>
          )}

          <div className="flex flex-col gap-3 md:flex-row">
            <Button type="button" variant="secondary" sheen={false} className="flex-1" onClick={handleCancel}>
              Cancel
            </Button>
            <Button type="button" className="flex-1" onClick={() => setStep('verify')}>
              Next: Verify Code
            </Button>
          </div>
        </HoloPanel>
      );
    }

    if (step === 'verify') {
      return (
        <HoloPanel theme="space" className="space-y-6 border border-white/5">
          <div className="text-center space-y-2">
            <h3 className="text-xl font-heading text-pearl-50">Confirm Activation</h3>
            <p className="text-sm text-pearl-300/80">Enter the 6-digit token generated by your authenticator.</p>
          </div>

          <form onSubmit={handleVerifyAndEnable} className="mx-auto flex max-w-sm flex-col gap-4">
            <label htmlFor="verification-code" className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">
              Verification Code
            </label>
            <input
              id="verification-code"
              type="text"
              value={verificationCode}
              onChange={(event) => setVerificationCode(event.target.value.replace(/[^0-9]/g, ''))}
              maxLength={6}
              required
              className="w-full rounded-2xl border border-white/10 bg-space-900/60 px-6 py-4 text-center text-2xl font-mono tracking-[0.6em] text-pearl-100 placeholder-pearl-500 focus:border-saturn-400/60 focus:outline-none"
              placeholder="000000"
            />

            <div className="flex flex-col gap-3 md:flex-row">
              <Button type="button" variant="secondary" sheen={false} className="flex-1" onClick={() => setStep('setup')}>
                Back
              </Button>
              <Button type="submit" className="flex-1" disabled={isLoading || verificationCode.length !== 6}>
                {isLoading ? 'Verifying…' : 'Enable 2FA'}
              </Button>
            </div>
          </form>
        </HoloPanel>
      );
    }

    return (
      <HoloPanel
        theme="space"
        className="flex flex-col gap-6 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div className="flex items-start gap-4">
          <div
            className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${
              isEnabled
                ? 'from-emerald-400 to-emerald-600 shadow-[0_0_35px_rgba(16,185,129,0.35)]'
                : 'from-saturn-400 to-saturn-600 shadow-[0_0_35px_rgba(95,99,251,0.3)]'
            }`}
          >
            <ShieldCheckIcon className="h-7 w-7 text-white" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-heading text-pearl-50">Two-Factor Authentication</h3>
            <p className="text-sm text-pearl-300/80">
              Require a rotating authenticator challenge in addition to your password for zero-trust compliance.
            </p>
          </div>
        </div>

        <div className="flex flex-col items-start gap-3 md:items-end">
          <VolumetricBadge status={isEnabled ? 'completed' : 'failed'}>
            {isEnabled ? 'Enabled' : 'Disabled'}
          </VolumetricBadge>
          {isEnabled ? (
            <Button type="button" variant="danger" sheen={false} onClick={handleDisable2FA} disabled={isLoading}>
              {isLoading ? 'Disabling…' : 'Disable 2FA'}
            </Button>
          ) : (
            <Button type="button" onClick={handleEnable2FA} disabled={isLoading}>
              {isLoading ? 'Preparing…' : 'Enable 2FA'}
            </Button>
          )}
        </div>
      </HoloPanel>
    );
  };

  return (
    <SettingsSceneLayout
      title="Two-Factor Authentication"
      subtitle="Deploy multi-factor verification across every login event"
      actions={
        <Link to="/2040/settings/sessions" className="inline-block">
          <Button sheen={false} variant="secondary">
            Review Sessions
          </Button>
        </Link>
      }
    >
      <div className="space-y-6">
        {success && (
          <HoloPanel theme="sun" className="flex items-start gap-3 border border-white/10 px-4 py-3 text-sm text-pearl-50">
            <CheckCircleIcon className="h-5 w-5 flex-shrink-0" />
            <span>{success}</span>
          </HoloPanel>
        )}

        {error && (
          <HoloPanel theme="mars" className="flex items-start gap-3 border border-white/10 px-4 py-3 text-sm text-pearl-50">
            <ExclamationCircleIcon className="h-5 w-5 flex-shrink-0" />
            <span>{error}</span>
          </HoloPanel>
        )}

        {renderStep()}

        <HoloPanel theme="space" className="border border-white/5">
          <h4 className="text-sm font-heading uppercase tracking-[0.3em] text-pearl-200/80">
            Why enable MFA?
          </h4>
          <ul className="mt-4 space-y-2 text-xs text-pearl-200/70">
            <li>• Neutralises stolen password attacks by demanding a physical device.</li>
            <li>• Generates time-bound codes every 30 seconds for tamper-proof logins.</li>
            <li>• Aligns with SOC2 and ISO 27001 control requirements.</li>
            <li>• Recommended for all operators managing trading or compliance workflows.</li>
          </ul>
        </HoloPanel>
      </div>
    </SettingsSceneLayout>
  );
}
