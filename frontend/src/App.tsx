import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { InactivityMonitor } from './components/auth/InactivityMonitor';
import { ToastProvider } from './contexts/ToastContext';
import { LoginPage } from './pages/auth/LoginPage';
import { ForgotPasswordPage } from './pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/auth/ResetPasswordPage';

// 2040 Holographic System
import { Layout2040 } from './layouts/Layout2040';

// 2040 Holographic Module Scenes
import { TradeDeskScene } from './pages/2040/TradeDeskScene';
import { PartnerManagementScene } from './pages/2040/PartnerManagementScene';
import { DocumentIntelligenceScene } from './pages/2040/DocumentIntelligenceScene';

// Lazy load remaining 2040 scenes
const SettingsScene = React.lazy(() => import('./pages/2040/SettingsScene'));
const UserManagementScene = React.lazy(() => import('./pages/2040/UserManagementScene'));
const QualityScene = React.lazy(() => import('./pages/2040/QualityScene'));
const LogisticsScene = React.lazy(() => import('./pages/2040/LogisticsScene'));
const DeliveryScene = React.lazy(() => import('./pages/2040/DeliveryScene'));
const AccountsScene = React.lazy(() => import('./pages/2040/AccountsScene'));
const DisputesScene = React.lazy(() => import('./pages/2040/DisputesScene'));
const AuditScene = React.lazy(() => import('./pages/2040/AuditScene'));

const ProfileSettingsPage = React.lazy(() =>
  import('./pages/settings/ProfilePage').then((module) => ({ default: module.ProfilePage }))
);
const OrganizationSettingsPage = React.lazy(() => import('./pages/settings/OrganizationPage'));
const CommoditiesSettingsPage = React.lazy(() => import('./pages/settings/CommoditiesPage'));
const LocationsSettingsPage = React.lazy(() => import('./pages/settings/LocationsPage'));
const SessionsSettingsPage = React.lazy(() =>
  import('./pages/settings/SessionsPage').then((module) => ({ default: module.SessionsPage }))
);
const TwoFactorSettingsPage = React.lazy(() =>
  import('./pages/settings/TwoFactorPage').then((module) => ({ default: module.TwoFactorPage }))
);

export default function App() {
  console.log('App component rendered - 2040 Architecture with Auth!');
  
  return (
    <ToastProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <InactivityMonitor />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        
        {/* Protected routes - All using 2040 Holographic System */}
        <Route path="/" element={<Navigate to="/2040/trade-desk" replace />} />
        <Route 
          path="/2040" 
          element={
            <ProtectedRoute>
              <Layout2040 />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/2040/trade-desk" replace />} />
          
          {/* All 2040 Holographic Modules */}
          <Route path="trade-desk" element={<TradeDeskScene />} />
          
          <Route path="partners" element={<PartnerManagementScene />} />
          
          <Route path="documents" element={<DocumentIntelligenceScene />} />
          
          <Route path="quality" element={
            <React.Suspense fallback={<LoadingScene />}>
              <QualityScene />
            </React.Suspense>
          } />
          
          <Route path="logistics" element={
            <React.Suspense fallback={<LoadingScene />}>
              <LogisticsScene />
            </React.Suspense>
          } />
          
          <Route path="delivery" element={
            <React.Suspense fallback={<LoadingScene />}>
              <DeliveryScene />
            </React.Suspense>
          } />
          
          <Route path="disputes" element={
            <React.Suspense fallback={<LoadingScene />}>
              <DisputesScene />
            </React.Suspense>
          } />
          
          <Route path="audit" element={
            <React.Suspense fallback={<LoadingScene />}>
              <AuditScene />
            </React.Suspense>
          } />
          
          <Route path="users" element={
            <React.Suspense fallback={<LoadingScene />}>
              <UserManagementScene />
            </React.Suspense>
          } />
          
          <Route path="accounts" element={
            <React.Suspense fallback={<LoadingScene />}>
              <AccountsScene />
            </React.Suspense>
          } />
          
          <Route path="settings" element={
            <React.Suspense fallback={<LoadingScene />}>
              <SettingsScene />
            </React.Suspense>
          } />
          <Route path="settings/profile" element={
            <React.Suspense fallback={<LoadingScene />}>
              <ProfileSettingsPage />
            </React.Suspense>
          } />
          <Route path="settings/organization" element={
            <React.Suspense fallback={<LoadingScene />}>
              <OrganizationSettingsPage />
            </React.Suspense>
          } />
          <Route path="settings/commodities" element={
            <React.Suspense fallback={<LoadingScene />}>
              <CommoditiesSettingsPage />
            </React.Suspense>
          } />
          <Route path="settings/locations" element={
            <React.Suspense fallback={<LoadingScene />}>
              <LocationsSettingsPage />
            </React.Suspense>
          } />
          <Route path="settings/sessions" element={
            <React.Suspense fallback={<LoadingScene />}>
              <SessionsSettingsPage />
            </React.Suspense>
          } />
          <Route path="settings/2fa" element={
            <React.Suspense fallback={<LoadingScene />}>
              <TwoFactorSettingsPage />
            </React.Suspense>
          } />
          
          <Route path="*" element={<PlaceholderPage title="Page Not Found" />} />
        </Route>
        
        {/* Legacy redirects */}
        <Route path="/backoffice/*" element={<Navigate to="/2040/trade-desk" replace />} />
      </Routes>
    </BrowserRouter>
      </ToastProvider>
  );
}

function PlaceholderPage({ title }: Readonly<{ title: string }>) {
  return (
    <div className="min-h-screen bg-space-500 flex items-center justify-center p-6">
      <div className="hologlass-saturn rounded-holo-lg p-12 text-center max-w-2xl">
        <div className="text-6xl mb-6">🚧</div>
        <h1 className="text-4xl font-heading font-bold text-pearl-50 mb-4 text-glow-saturn">{title}</h1>
        <p className="text-pearl-300 text-lg mb-2">This holographic module is materializing</p>
        <p className="text-pearl-400 text-sm">Part of the 2040 Vision Architecture</p>
      </div>
    </div>
  );
}

function LoadingScene() {
  return (
    <div className="min-h-screen bg-space-500 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-saturn-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <div className="text-pearl-200 text-sm">Loading holographic interface...</div>
      </div>
    </div>
  );
}
