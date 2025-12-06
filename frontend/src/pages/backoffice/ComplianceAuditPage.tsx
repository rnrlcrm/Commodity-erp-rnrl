/**
 * Compliance / Audit Trail Module
 * Style: Paper-like digital ledger style
 * Purpose: Legally intuitive, resembles traditional ledger books
 */

import { useState } from 'react';
import { 
  DocumentTextIcon,
  ClockIcon,
  UserIcon,
  CheckBadgeIcon,
} from '@heroicons/react/24/outline';

interface AuditEntry {
  id: string;
  timestamp: Date;
  user: string;
  action: string;
  module: string;
  details: string;
  status: 'success' | 'warning' | 'error';
}

export function ComplianceAuditPage() {
  const [auditLog] = useState<AuditEntry[]>([
    {
      id: 'AUD001',
      timestamp: new Date('2024-12-05T14:32:15'),
      user: 'Rajkumar Rungta',
      action: 'Trade Approval',
      module: 'Trade Desk',
      details: 'Approved trade TR2024-0156 for ₹28.47L',
      status: 'success',
    },
    {
      id: 'AUD002',
      timestamp: new Date('2024-12-05T13:18:42'),
      user: 'Naman Rungta',
      action: 'Settlement Initiated',
      module: 'Clearing',
      details: 'Initiated settlement ST001 for ₹28.47L',
      status: 'success',
    },
    {
      id: 'AUD003',
      timestamp: new Date('2024-12-05T11:05:33'),
      user: 'System Admin',
      action: 'Risk Threshold Update',
      module: 'Risk Management',
      details: 'Updated market volatility threshold from 75% to 80%',
      status: 'warning',
    },
    {
      id: 'AUD004',
      timestamp: new Date('2024-12-05T09:47:21'),
      user: 'Lekha Rungta',
      action: 'Partner Verification',
      module: 'Partners',
      details: 'Verified partner ABC Textiles Ltd - KYC complete',
      status: 'success',
    },
  ]);

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header - Paper-like */}
      <div className="bg-gradient-to-b from-amber-50 to-white border-2 border-amber-200/50 rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-bold text-space-900" style={{ fontFamily: 'Georgia, serif' }}>
              Compliance & Audit Trail
            </h1>
            <p className="text-amber-800 mt-1 italic">Complete record of all system activities</p>
          </div>
          <div className="flex items-center gap-2 text-emerald-700 bg-emerald-50 px-4 py-2 rounded border border-emerald-200">
            <CheckBadgeIcon className="w-5 h-5" />
            <span className="font-bold">Compliant</span>
          </div>
        </div>
      </div>

      {/* Stats - Ledger Style */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Entries', value: '2,847', color: 'amber' },
          { label: 'Today', value: '124', color: 'emerald' },
          { label: 'Warnings', value: '3', color: 'sun' },
          { label: 'Compliance Score', value: '98%', color: 'emerald' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white border-2 border-amber-200/50 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-120"
          >
            <p className="text-2xl font-heading font-bold text-space-900 font-mono">{stat.value}</p>
            <p className="text-sm text-amber-800 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Audit Log - Ledger Book Style */}
      <div className="bg-gradient-to-b from-amber-50 to-white border-2 border-amber-200/50 rounded-lg shadow-lg overflow-hidden">
        {/* Ledger Header */}
        <div className="bg-gradient-to-r from-amber-100 to-amber-50 border-b-2 border-amber-300 p-4">
          <h2 className="text-xl font-heading font-bold text-space-900" style={{ fontFamily: 'Georgia, serif' }}>
            Audit Ledger - December 2024
          </h2>
          <p className="text-xs text-amber-700 mt-1 font-mono">
            Page 1 of 28 • Last updated: {new Date().toLocaleString()}
          </p>
        </div>

        {/* Ledger Entries */}
        <div className="divide-y divide-amber-200">
          {auditLog.map((entry, index) => (
            <div
              key={entry.id}
              className="p-4 hover:bg-amber-50/50 transition-colors duration-120"
              style={{
                backgroundImage: index % 2 === 0 ? 'none' : 'repeating-linear-gradient(0deg, transparent, transparent 1px, rgba(251, 191, 36, 0.02) 1px, rgba(251, 191, 36, 0.02) 2px)',
              }}
            >
              <div className="flex items-start gap-4">
                {/* Entry Number - Ledger style */}
                <div className="flex-shrink-0 w-16 text-right">
                  <span className="font-mono text-sm font-bold text-amber-700">
                    #{entry.id.replace('AUD', '')}
                  </span>
                </div>

                {/* Timestamp */}
                <div className="flex-shrink-0 w-40">
                  <div className="flex items-center gap-2 text-amber-800">
                    <ClockIcon className="w-4 h-4" />
                    <div className="font-mono text-xs">
                      <div>{entry.timestamp.toLocaleDateString()}</div>
                      <div className="text-amber-600">{entry.timestamp.toLocaleTimeString()}</div>
                    </div>
                  </div>
                </div>

                {/* User */}
                <div className="flex-shrink-0 w-48">
                  <div className="flex items-center gap-2">
                    <UserIcon className="w-4 h-4 text-amber-700" />
                    <span className="text-sm font-medium text-space-900">{entry.user}</span>
                  </div>
                </div>

                {/* Module Badge */}
                <div className="flex-shrink-0">
                  <span className="px-3 py-1 text-xs font-bold bg-amber-100 text-amber-800 rounded border border-amber-300">
                    {entry.module}
                  </span>
                </div>

                {/* Action & Details */}
                <div className="flex-1">
                  <p className="text-sm font-bold text-space-900 mb-1">{entry.action}</p>
                  <p className="text-xs text-amber-700" style={{ fontFamily: 'Georgia, serif' }}>
                    {entry.details}
                  </p>
                </div>

                {/* Status */}
                <div className="flex-shrink-0">
                  <span
                    className={`px-3 py-1 text-xs font-bold rounded border ${
                      entry.status === 'success'
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                        : entry.status === 'warning'
                        ? 'bg-sun-50 text-sun-700 border-sun-300'
                        : 'bg-mars-50 text-mars-700 border-mars-300'
                    }`}
                  >
                    {entry.status.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Ledger line decoration */}
              {index < auditLog.length - 1 && (
                <div className="mt-3 border-b border-amber-200 border-dashed opacity-30" />
              )}
            </div>
          ))}
        </div>

        {/* Ledger Footer */}
        <div className="bg-gradient-to-r from-amber-100 to-amber-50 border-t-2 border-amber-300 p-4">
          <div className="flex items-center justify-between text-xs text-amber-800 font-mono">
            <span>End of current page</span>
            <span>Certified digitally signed ledger • RNRL Exchange 2040</span>
          </div>
        </div>
      </div>

      {/* Compliance Certificates */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { name: 'SEBI Compliance', status: 'Active', expiry: '2025-12-31' },
          { name: 'ISO 27001', status: 'Active', expiry: '2025-06-30' },
          { name: 'SOC 2 Type II', status: 'Active', expiry: '2025-09-15' },
        ].map((cert) => (
          <div
            key={cert.name}
            className="bg-white border-2 border-emerald-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-120"
          >
            <div className="flex items-start justify-between mb-2">
              <DocumentTextIcon className="w-6 h-6 text-emerald-600" />
              <span className="px-2 py-1 text-xs font-bold bg-emerald-50 text-emerald-700 rounded border border-emerald-200">
                {cert.status}
              </span>
            </div>
            <h3 className="font-heading font-bold text-space-900 mb-1">{cert.name}</h3>
            <p className="text-xs text-amber-700 font-mono">Expires: {cert.expiry}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
