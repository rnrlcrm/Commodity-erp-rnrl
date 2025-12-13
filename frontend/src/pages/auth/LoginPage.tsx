/**
 * Login Page - 2040 Holographic Design
 * Email/Password authentication for internal users
 */

import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { EnvelopeIcon, LockClosedIcon, ExclamationCircleIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/hooks/useAuth';
import { GeometricBackground } from '@/components/2040/GeometricBackground';
import { HolographicBackground } from '@/components/2040/HolographicBackground';
import { Button } from '@/components/2040';
import { CompanyLogo } from '@/components/common/CompanyLogo';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{ email?: string; password?: string }>({});

  const validateForm = (): boolean => {
    const errors: { email?: string; password?: string } = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) errors.email = 'Email is required';
    else if (!emailRegex.test(email)) errors.email = 'Please enter a valid email address';
    if (!password) errors.password = 'Password is required';
    else if (password.length < 8) errors.password = 'Password must be at least 8 characters';
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    clearError();
    if (!validateForm()) return;
    try {
      await login({ email, password });
      navigate('/2040/trade-desk');
    } catch (err) {
      console.error('Login failed', err);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-space-950 text-pearl-50">
      <GeometricBackground />
      <HolographicBackground />

      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-32 right-1/4 h-72 w-72 rounded-full bg-saturn-500/20 blur-3xl" />
        <div className="absolute bottom-[-10rem] left-1/3 h-96 w-96 rounded-full bg-sun-500/10 blur-[120px]" />
      </div>

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12 text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mx-auto mb-6"
          >
            <CompanyLogo
              size="lg"
              className="mx-auto drop-shadow-[0_0_35px_rgba(59,130,246,0.35)]"
            />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.45 }}
            className="text-3xl font-heading font-semibold tracking-wide text-pearl-50"
          >
            2040 Holographic Access System
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45, duration: 0.45 }}
            className="mt-3 text-sm text-pearl-300"
          >
            Sign in to manage global cotton trade operations, insights, and automations.
          </motion.p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 18 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
          className="w-full max-w-lg rounded-3xl border border-pearl-500/20 bg-space-900/70 p-8 shadow-[0_20px_60px_rgba(8,15,40,0.55)] backdrop-blur-xl"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="flex items-start gap-3 rounded-xl border border-mars-400/40 bg-mars-500/15 px-4 py-3 text-sm text-mars-200">
                <ExclamationCircleIcon className="mt-0.5 h-5 w-5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-pearl-100">
                Email Address
              </label>
              <div className="relative">
                <EnvelopeIcon className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-saturn-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => {
                    setEmail(event.target.value);
                    setValidationErrors((prev) => ({ ...prev, email: undefined }));
                  }}
                  autoComplete="email"
                  className={`block w-full rounded-2xl border bg-pearl-500/10 py-3 pl-12 pr-4 text-pearl-50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-saturn-400/70 ${
                    validationErrors.email ? 'border-mars-500 focus:ring-mars-400/70' : 'border-pearl-500/20'
                  }`}
                  placeholder="admin@rnrl.com"
                  disabled={isLoading}
                />
              </div>
              {validationErrors.email && <p className="text-xs text-mars-300">{validationErrors.email}</p>}
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-pearl-100">
                Password
              </label>
              <div className="relative">
                <LockClosedIcon className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-saturn-400" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => {
                    setPassword(event.target.value);
                    setValidationErrors((prev) => ({ ...prev, password: undefined }));
                  }}
                  autoComplete="current-password"
                  className={`block w-full rounded-2xl border bg-pearl-500/10 py-3 pl-12 pr-12 text-pearl-50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-saturn-400/70 ${
                    validationErrors.password ? 'border-mars-500 focus:ring-mars-400/70' : 'border-pearl-500/20'
                  }`}
                  placeholder="••••••••"
                  disabled={isLoading}
                />
                <Button
                  type="button"
                  variant="secondary"
                  sheen={false}
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 bg-transparent text-saturn-300 hover:text-pearl-100 border-none rounded-none shadow-none"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </Button>
              </div>
              {validationErrors.password && <p className="text-xs text-mars-300">{validationErrors.password}</p>}
            </div>

            <div className="flex items-center justify-between text-sm">
              <label htmlFor="remember-me" className="flex items-center gap-2 text-pearl-300">
                <input
                  id="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) => setRememberMe(event.target.checked)}
                  className="h-4 w-4 rounded border-pearl-500/30 bg-pearl-500/10 text-saturn-500 focus:ring-saturn-500"
                />
                Remember me
              </label>
              <Link to="/forgot-password" className="font-medium text-saturn-300 transition hover:text-saturn-200">
                Forgot password?
              </Link>
            </div>

            <Button type="submit" className="w-full py-3 text-base font-semibold" disabled={isLoading}>
              {isLoading ? 'Signing in…' : 'Enter the Backoffice'}
            </Button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
