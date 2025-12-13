import React, { useState } from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { VolumetricTable, VolumetricBadge } from '../../components/2040/VolumetricTable';
import { AIInsightBar } from '../../components/2040/AIInsightBar';
import { FloatingActionBar } from '../../components/2040/FloatingActionBar';
import { useRealtimeChannel } from '../../hooks/useRealtime';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Edit } from 'lucide-react';

interface Partner {
  id: string;
  name: string;
  type: 'supplier' | 'buyer' | 'transporter';
  creditLimit: number;
  creditUsed: number;
  kycStatus: 'verified' | 'pending' | 'expired';
  riskScore: number;
  lastActivity: Date;
}

export const PartnerManagementScene: React.FC = () => {
  const [partners, setPartners] = useState<Partner[]>([
    {
      id: '1',
      name: 'Global Cotton Suppliers Inc.',
      type: 'supplier',
      creditLimit: 5000000,
      creditUsed: 3200000,
      kycStatus: 'verified',
      riskScore: 85,
      lastActivity: new Date(),
    },
    {
      id: '2',
      name: 'Textile Manufacturing Ltd.',
      type: 'buyer',
      creditLimit: 3000000,
      creditUsed: 2100000,
      kycStatus: 'verified',
      riskScore: 92,
      lastActivity: new Date(),
    },
    {
      id: '3',
      name: 'Swift Logistics Co.',
      type: 'transporter',
      creditLimit: 1000000,
      creditUsed: 450000,
      kycStatus: 'pending',
      riskScore: 78,
      lastActivity: new Date(),
    },
  ]);

  const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null);

  // Realtime subscriptions
  useRealtimeChannel('partners.kyc', (data) => {
    console.log('KYC update:', data);
  });

  useRealtimeChannel('partners.credit', (data) => {
    console.log('Credit update:', data);
  });

  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      {/* Header */}
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
              Business Partner Management
            </h1>
            <p className="text-sm text-pearl-300">
              KYC verification, credit management, and partner risk assessment
            </p>
          </div>
          <motion.button
            className="px-4 py-2 bg-sun-500/20 hover:bg-sun-500/30 text-sun-300 rounded-lg border border-sun-500/40 text-sm font-medium transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            + Add Partner
          </motion.button>
        </div>
      </HoloPanel>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Partners', value: '156', icon: '🤝' },
          { label: 'Pending KYC', value: '12', icon: '📋' },
          { label: 'Credit Utilization', value: '64%', icon: '💰' },
          { label: 'High Risk', value: '3', icon: '⚠️' },
        ].map((stat) => (
          <HoloCard key={stat.label} theme="pearl">
            <div className="flex items-center gap-3">
              <div className="text-3xl">{stat.icon}</div>
              <div className="flex-1">
                <div className="text-xs text-pearl-400 mb-1">{stat.label}</div>
                <div className="text-2xl font-heading text-pearl-50">{stat.value}</div>
              </div>
            </div>
          </HoloCard>
        ))}
      </div>

      {/* Partners Table */}
      <HoloPanel theme="pearl" className="p-6">
        <h2 className="text-xl font-heading text-pearl-50 mb-4">Active Partners</h2>

        <VolumetricTable
          data={partners}
          columns={[
            {
              key: 'name',
              label: 'Partner Name',
              width: '240px',
            },
            {
              key: 'type',
              label: 'Type',
              width: '120px',
              render: (value) => (
                <span className="capitalize text-pearl-300">{value}</span>
              ),
            },
            {
              key: 'creditLimit',
              label: 'Credit Limit',
              width: '140px',
              render: (value) => (
                <span className="font-mono text-sun-300">
                  ${(value / 1000000).toFixed(1)}M
                </span>
              ),
            },
            {
              key: 'creditUsed',
              label: 'Credit Used',
              width: '140px',
              render: (value, row) => {
                const percent = (value / row.creditLimit) * 100;
                return (
                  <div className="space-y-1">
                    <div className="font-mono text-xs text-pearl-200">
                      ${(value / 1000000).toFixed(1)}M
                    </div>
                    <div className="h-1 bg-pearl-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          percent > 80 ? 'bg-mars-500' : 'bg-saturn-500'
                        }`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              },
            },
            {
              key: 'kycStatus',
              label: 'KYC Status',
              width: '120px',
              render: (value) => {
                const statusMap = {
                  verified: 'completed',
                  pending: 'pending',
                  expired: 'failed',
                };
                return (
                  <VolumetricBadge status={statusMap[value as keyof typeof statusMap] as any}>
                    {value.toUpperCase()}
                  </VolumetricBadge>
                );
              },
            },
            {
              key: 'riskScore',
              label: 'Risk Score',
              width: '120px',
              render: (value) => {
                const color = value >= 80 ? 'text-green-400' : value >= 60 ? 'text-sun-400' : 'text-mars-400';
                return (
                  <span className={`font-mono ${color}`}>{value}/100</span>
                );
              },
            },
          ]}
          keyExtractor={(row) => row.id}
          theme="saturn"
        />
      </HoloPanel>

      {/* AI Insight Bar */}
      <AIInsightBar module="partners" context={{ partners }} />
    </div>
  );
};
