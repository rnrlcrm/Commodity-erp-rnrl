import React from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { AIInsightBar } from '../../components/2040/AIInsightBar';

export default function SettingsScene() {
  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
          System Settings
        </h1>
        <p className="text-sm text-pearl-300">
          Configure system preferences, integrations, and advanced settings
        </p>
      </HoloPanel>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { title: 'General', icon: '⚙️', count: '12 settings' },
          { title: 'Integrations', icon: '🔗', count: '5 active' },
          { title: 'Security', icon: '🔒', count: '8 policies' },
        ].map((section) => (
          <HoloCard key={section.title} theme="pearl">
            <div className="text-3xl mb-3">{section.icon}</div>
            <div className="text-lg font-heading text-pearl-50 mb-1">{section.title}</div>
            <div className="text-xs text-pearl-400">{section.count}</div>
          </HoloCard>
        ))}
      </div>

      <AIInsightBar module="settings" context={{}} />
    </div>
  );
}
