import React from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { AIInsightBar } from '../../components/2040/AIInsightBar';

export default function AccountsScene() {
  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
          Accounts & Settlement
        </h1>
        <p className="text-sm text-pearl-300">
          Financial transactions, reconciliation, and automated settlement processing
        </p>
      </HoloPanel>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Pending Settlements', value: '$3.2M', icon: '💰' },
          { label: 'Processed Today', value: '$8.5M', icon: '✓' },
          { label: 'Reconciliation Rate', value: '99.1%', icon: '🎯' },
          { label: 'Discrepancies', value: '5', icon: '⚠️' },
        ].map((stat) => (
          <HoloCard key={stat.label} theme="pearl">
            <div className="text-3xl mb-2">{stat.icon}</div>
            <div className="text-xs text-pearl-400 mb-1">{stat.label}</div>
            <div className="text-2xl font-heading text-pearl-50">{stat.value}</div>
          </HoloCard>
        ))}
      </div>

      <AIInsightBar module="accounts" context={{}} />
    </div>
  );
}
