import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { BackofficeLayout2040 } from './layouts/BackofficeLayout2040';
import { DashboardPage } from './pages/backoffice/DashboardPage';
import { ClearingSettlementPage } from './pages/backoffice/ClearingSettlementPage';
import { RiskMonitoringPage } from './pages/backoffice/RiskMonitoringPage';
import { ComplianceAuditPage } from './pages/backoffice/ComplianceAuditPage';
import { UserManagementPage } from './pages/backoffice/UserManagementPage';
import { AccountsFinancePage } from './pages/backoffice/AccountsFinancePage';

export default function App() {
  console.log('App component rendered - 2040 Architecture!');
  
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<Navigate to="/backoffice" replace />} />
        <Route path="/backoffice" element={<BackofficeLayout2040 />}>
          <Route index element={<DashboardPage />} />
          <Route path="trade-desk" element={<PlaceholderPage title="Trade Desk" />} />
          <Route path="clearing" element={<ClearingSettlementPage />} />
          <Route path="risk" element={<RiskMonitoringPage />} />
          <Route path="audit" element={<ComplianceAuditPage />} />
          <Route path="users" element={<UserManagementPage />} />
          <Route path="accounts" element={<AccountsFinancePage />} />
          <Route path="settings" element={<PlaceholderPage title="Settings" />} />
          <Route path="*" element={<PlaceholderPage title="Page Not Found" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="max-w-4xl mx-auto p-12 animate-fadeIn">
      <div className="bg-gradient-to-br from-saturn-50 to-sun-50 border-2 border-saturn-200 rounded-2xl p-12 text-center">
        <h1 className="text-4xl font-heading font-bold text-space-900 mb-4">{title}</h1>
        <p className="text-saturn-600 text-lg">This module is under development</p>
        <p className="text-saturn-500 text-sm mt-2">Part of the 2040 Vision Architecture</p>
      </div>
    </div>
  );
}
