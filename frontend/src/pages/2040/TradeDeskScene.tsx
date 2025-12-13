import React, { useState } from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { VolumetricTable, VolumetricBadge } from '../../components/2040/VolumetricTable';
import { AIInsightBar } from '../../components/2040/AIInsightBar';
import { FloatingActionBar } from '../../components/2040/FloatingActionBar';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/2040/Card';
import { Button } from '../../components/2040/Button';
import { GeometricBackground } from '../../components/2040/GeometricBackground';
import { useAIOrchestrator } from '../../hooks/useAIOrchestrator';
import { useRealtimeChannel } from '../../hooks/useRealtime';
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react';

interface TradeRecord {
  id: string;
  tradeId: string;
  commodity: string;
  quantity: number;
  price: number;
  counterparty: string;
  status: 'pending' | 'executed' | 'settled' | 'failed';
  timestamp: Date;
}

export const TradeDeskScene: React.FC = () => {
  const [trades, setTrades] = useState<TradeRecord[]>([
    {
      id: '1',
      tradeId: 'TD-2040-001',
      commodity: 'Cotton Bales',
      quantity: 500,
      price: 125.50,
      counterparty: 'Acme Trading Co.',
      status: 'executed',
      timestamp: new Date(),
    },
    {
      id: '2',
      tradeId: 'TD-2040-002',
      commodity: 'Wheat',
      quantity: 1000,
      price: 85.25,
      counterparty: 'Global Grains Ltd.',
      status: 'pending',
      timestamp: new Date(),
    },
    {
      id: '3',
      tradeId: 'TD-2040-003',
      commodity: 'Coffee Beans',
      quantity: 250,
      price: 220.00,
      counterparty: 'Bean Corp',
      status: 'settled',
      timestamp: new Date(),
    },
  ]);

  const [selectedTrade, setSelectedTrade] = useState<TradeRecord | null>(null);

  // AI Orchestration
  const { aiState } = useAIOrchestrator({
    module: 'trade-desk',
    context: { trades, selectedTrade },
    enablePredictions: true,
    enableSuggestions: true,
  });

  // Realtime subscriptions
  useRealtimeChannel('trade.ticks', (data) => {
    console.log('Trade tick:', data);
  });

  useRealtimeChannel('trade.executions', (data) => {
    console.log('Trade execution:', data);
    // Update trades with new execution
  });

  useRealtimeChannel('trade.reconciliation', (data) => {
    console.log('Reconciliation update:', data);
  });

  const handleReconcile = () => {
    console.log('Running trade reconciliation...');
  };

  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6 relative">
      <GeometricBackground />
      {/* Header */}
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
              Trade Desk Operations
            </h1>
            <p className="text-sm text-pearl-300">
              Real-time trade execution, reconciliation, and back-office operations
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={handleReconcile}
            >
              Run Reconciliation
            </Button>
            <Button
              variant="primary"
            >
              Export Report
            </Button>
          </div>
        </div>
      </HoloPanel>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Trades', value: '24', change: '+8%', theme: 'saturn' },
          { label: 'Pending Settlement', value: '$2.4M', change: '-3%', theme: 'sun' },
          { label: 'Reconciliation Rate', value: '98.5%', change: '+2%', theme: 'saturn' },
          { label: 'Failed Trades', value: '2', change: '-50%', theme: 'mars' },
        ].map((stat) => (
          <HoloCard key={stat.label} theme={stat.theme as any}>
            <div className="text-xs text-pearl-400 mb-1">{stat.label}</div>
            <div className="text-2xl font-heading text-pearl-50 mb-1">{stat.value}</div>
            <div className={`text-xs ${stat.change.startsWith('+') ? 'text-green-400' : 'text-mars-400'}`}>
              {stat.change}
            </div>
          </HoloCard>
        ))}
      </div>

      {/* Trades Table */}
      <HoloPanel theme="pearl" className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-heading text-pearl-50">Recent Trades</h2>
          <div className="flex items-center gap-2 text-xs text-pearl-400">
            <div className="w-2 h-2 bg-saturn-400 rounded-full animate-pulse" />
            Live
          </div>
        </div>

        <VolumetricTable
          data={trades}
          columns={[
            {
              key: 'tradeId',
              label: 'Trade ID',
              width: '140px',
              render: (value) => (
                <span className="font-mono text-saturn-300">{value}</span>
              ),
            },
            {
              key: 'commodity',
              label: 'Commodity',
              width: '160px',
            },
            {
              key: 'quantity',
              label: 'Quantity',
              width: '120px',
              render: (value) => (
                <span className="font-mono">{value.toLocaleString()}</span>
              ),
            },
            {
              key: 'price',
              label: 'Price',
              width: '120px',
              render: (value) => (
                <span className="font-mono text-sun-300">${value.toFixed(2)}</span>
              ),
            },
            {
              key: 'counterparty',
              label: 'Counterparty',
            },
            {
              key: 'status',
              label: 'Status',
              width: '140px',
              render: (value) => (
                <VolumetricBadge status={value}>
                  {value.toUpperCase()}
                </VolumetricBadge>
              ),
            },
          ]}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => setSelectedTrade(row)}
          theme="saturn"
        />
      </HoloPanel>

      {/* AI Predictions */}
      {aiState.predictions.length > 0 && (
        <HoloPanel theme="saturn" className="p-4">
          <div className="text-sm font-medium text-saturn-300 mb-3">AI Market Predictions</div>
          <div className="space-y-2">
            {aiState.predictions.slice(0, 3).map((pred) => (
              <div
                key={pred.id}
                className="flex items-center gap-3 text-xs p-2 rounded-lg bg-saturn-500/10"
              >
                <div className="flex-1">
                  <span className="text-pearl-200">{pred.message}</span>
                </div>
                <span className="text-saturn-300 font-mono">
                  {(pred.confidence * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </HoloPanel>
      )}

      {/* AI Insight Bar */}
      <AIInsightBar module="trade-desk" context={{ trades, selectedTrade }} />

      {/* Floating Action Bar */}
      {selectedTrade && (
        <FloatingActionBar
          actions={[
            {
              id: 'execute',
              label: 'Execute',
              icon: CheckCircle,
              variant: 'primary',
              onClick: () => {
                console.log('Executing trade:', selectedTrade.tradeId);
                setSelectedTrade(null);
              }
            },
            {
              id: 'reconcile',
              label: 'Reconcile',
              icon: RefreshCw,
              variant: 'secondary',
              onClick: () => {
                console.log('Reconciling trade:', selectedTrade.tradeId);
              }
            },
            {
              id: 'cancel',
              label: 'Cancel',
              icon: XCircle,
              variant: 'danger',
              onClick: () => {
                console.log('Cancelling trade:', selectedTrade.tradeId);
                setSelectedTrade(null);
              }
            }
          ]}
        />
      )}
    </div>
  );
};
