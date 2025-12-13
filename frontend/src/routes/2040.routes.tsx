import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Layout2040 } from '../layouts/Layout2040';

// 2040 Module Scenes
import { TradeDeskScene } from '../pages/2040/TradeDeskScene';
import { PartnerManagementScene } from '../pages/2040/PartnerManagementScene';
import { DocumentIntelligenceScene } from '../pages/2040/DocumentIntelligenceScene';

// Lazy load other scenes
const SettingsScene = React.lazy(() => import('../pages/2040/SettingsScene'));
const UserManagementScene = React.lazy(() => import('../pages/2040/UserManagementScene'));
const QualityScene = React.lazy(() => import('../pages/2040/QualityScene'));
const LogisticsScene = React.lazy(() => import('../pages/2040/LogisticsScene'));
const DeliveryScene = React.lazy(() => import('../pages/2040/DeliveryScene'));
const AccountsScene = React.lazy(() => import('../pages/2040/AccountsScene'));
const DisputesScene = React.lazy(() => import('../pages/2040/DisputesScene'));
const AuditScene = React.lazy(() => import('../pages/2040/AuditScene'));

export const router2040 = createBrowserRouter([
  {
    path: '/2040',
    element: <Layout2040 />,
    children: [
      {
        index: true,
        element: <Navigate to="/2040/trade-desk" replace />,
      },
      {
        path: 'settings',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <SettingsScene />
          </React.Suspense>
        ),
      },
      {
        path: 'users',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <UserManagementScene />
          </React.Suspense>
        ),
      },
      {
        path: 'partners',
        element: <PartnerManagementScene />,
      },
      {
        path: 'trade-desk',
        element: <TradeDeskScene />,
      },
      {
        path: 'quality',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <QualityScene />
          </React.Suspense>
        ),
      },
      {
        path: 'logistics',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <LogisticsScene />
          </React.Suspense>
        ),
      },
      {
        path: 'delivery',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <DeliveryScene />
          </React.Suspense>
        ),
      },
      {
        path: 'accounts',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <AccountsScene />
          </React.Suspense>
        ),
      },
      {
        path: 'disputes',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <DisputesScene />
          </React.Suspense>
        ),
      },
      {
        path: 'audit',
        element: (
          <React.Suspense fallback={<div>Loading...</div>}>
            <AuditScene />
          </React.Suspense>
        ),
      },
      {
        path: 'documents',
        element: <DocumentIntelligenceScene />,
      },
    ],
  },
]);
