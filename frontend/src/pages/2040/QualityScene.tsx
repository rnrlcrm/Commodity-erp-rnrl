import React from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { AIInsightBar } from '../../components/2040/AIInsightBar';

export default function QualityScene() {
  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
          Quality Management
        </h1>
        <p className="text-sm text-pearl-300">
          AI-powered quality inspections, reports, and compliance tracking
        </p>
      </HoloPanel>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Inspections Today', value: '45', icon: '🔍' },
          { label: 'Pass Rate', value: '96.2%', icon: '✓' },
          { label: 'Pending Reports', value: '8', icon: '📋' },
          { label: 'Issues Flagged', value: '3', icon: '⚠️' },
        ].map((stat) => (
          <HoloCard key={stat.label} theme="pearl">
            <div className="text-3xl mb-2">{stat.icon}</div>
            <div className="text-xs text-pearl-400 mb-1">{stat.label}</div>
            <div className="text-2xl font-heading text-pearl-50">{stat.value}</div>
          </HoloCard>
        ))}
      </div>

      <AIInsightBar module="quality" context={{}} />
    </div>
  );
}
