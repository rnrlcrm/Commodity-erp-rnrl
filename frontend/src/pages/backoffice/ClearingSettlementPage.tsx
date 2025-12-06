/**
 * Clearing & Settlement Module
 * Style: Calm minimal UI (white + navy)
 * Purpose: Avoid cognitive overload in high-stakes settlement operations
 */

import { useState } from 'react';
import { 
  CheckCircleIcon, 
  ClockIcon,
  DocumentCheckIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline';
import { Button2040 } from '@/components/2040/InteractionComponents';

interface Settlement {
  id: string;
  tradeId: string;
  buyer: string;
  seller: string;
  amount: number;
  status: 'pending' | 'processing' | 'settled' | 'failed';
  scheduledDate: Date;
  completedDate?: Date;
}

export function ClearingSettlementPage() {
  const [settlements] = useState<Settlement[]>([
    {
      id: 'ST001',
      tradeId: 'TR2024-0156',
      buyer: 'ABC Textiles Ltd',
      seller: 'Global Cotton Corp',
      amount: 2847500,
      status: 'settled',
      scheduledDate: new Date('2024-12-05T10:00:00'),
      completedDate: new Date('2024-12-05T10:02:15'),
    },
    {
      id: 'ST002',
      tradeId: 'TR2024-0157',
      buyer: 'Prime Traders',
      seller: 'Elite Commodities',
      amount: 1234000,
      status: 'processing',
      scheduledDate: new Date('2024-12-05T14:00:00'),
    },
    {
      id: 'ST003',
      tradeId: 'TR2024-0158',
      buyer: 'XYZ Manufacturing',
      seller: 'Cotton Direct Ltd',
      amount: 3456000,
      status: 'pending',
      scheduledDate: new Date('2024-12-06T09:00:00'),
    },
  ]);

  const stats = [
    { label: 'Today Settled', value: '₹12.4Cr', icon: CheckCircleIcon, color: 'emerald' },
    { label: 'Pending', value: '₹8.2Cr', icon: ClockIcon, color: 'sun' },
    { label: 'Processing', value: '₹1.2Cr', icon: DocumentCheckIcon, color: 'saturn' },
    { label: 'Success Rate', value: '99.8%', icon: CurrencyDollarIcon, color: 'emerald' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'settled':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'processing':
        return 'bg-saturn-50 text-saturn-700 border-saturn-200';
      case 'pending':
        return 'bg-sun-50 text-sun-700 border-sun-200';
      case 'failed':
        return 'bg-mars-50 text-mars-700 border-mars-200';
      default:
        return 'bg-pearl-100 text-saturn-700 border-pearl-200';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header - Calm & Minimal */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-heading font-bold text-space-900">Clearing & Settlement</h1>
          <p className="text-saturn-600 mt-1">Manage trade settlements with precision and clarity</p>
        </div>
        <Button2040 variant="primary" size="md">
          Initiate Settlement
        </Button2040>
      </div>

      {/* Stats - Clean White Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="bg-white border-2 border-saturn-100 rounded-xl p-5 hover:border-saturn-200 hover:shadow-md transition-all duration-120"
            >
              <div className="flex items-start justify-between mb-3">
                <Icon className={`w-5 h-5 text-${stat.color}-600`} />
                <span className="text-xs font-mono text-saturn-400">LIVE</span>
              </div>
              <p className="text-2xl font-heading font-bold text-space-900 font-mono">{stat.value}</p>
              <p className="text-sm text-saturn-600 mt-1">{stat.label}</p>
            </div>
          );
        })}
      </div>

      {/* Settlement Queue - Minimal Table Design */}
      <div className="bg-white border-2 border-saturn-100 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b-2 border-saturn-100 bg-saturn-50/30">
          <h2 className="text-lg font-heading font-bold text-space-900">Settlement Queue</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-pearl-50 border-b-2 border-saturn-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Settlement ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Trade ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Buyer
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Seller
                </th>
                <th className="px-6 py-3 text-right text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Amount
                </th>
                <th className="px-6 py-3 text-center text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Scheduled
                </th>
                <th className="px-6 py-3 text-right text-xs font-bold text-space-900 uppercase tracking-wider font-heading">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-saturn-100">
              {settlements.map((settlement) => (
                <tr
                  key={settlement.id}
                  className="hover:bg-saturn-50/20 transition-colors duration-120"
                >
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm font-medium text-space-900">
                      {settlement.id}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm text-saturn-700">
                      {settlement.tradeId}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-space-900">{settlement.buyer}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-space-900">{settlement.seller}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono text-sm font-bold text-space-900">
                      ₹{(settlement.amount / 100000).toFixed(2)}L
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-center">
                      <span
                        className={`px-3 py-1 text-xs font-bold rounded-full border ${getStatusColor(
                          settlement.status
                        )}`}
                      >
                        {settlement.status.toUpperCase()}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <ClockIcon className="w-4 h-4 text-saturn-400" />
                      <span className="text-sm font-mono text-saturn-700">
                        {settlement.scheduledDate.toLocaleString('en-IN', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-sm text-saturn-600 hover:text-space-900 font-medium transition-colors duration-120">
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Settlement Process - Step Indicator */}
      <div className="bg-white border-2 border-saturn-100 rounded-xl p-6">
        <h3 className="text-lg font-heading font-bold text-space-900 mb-6">Settlement Process</h3>
        
        <div className="flex items-center justify-between">
          {['Validation', 'Clearing', 'Confirmation', 'Settlement', 'Reconciliation'].map(
            (step, index) => (
              <div key={step} className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-120 ${
                    index < 3
                      ? 'bg-emerald-500 text-white shadow-md'
                      : index === 3
                      ? 'bg-saturn-500 text-white shadow-md'
                      : 'bg-pearl-200 text-saturn-500'
                  }`}
                >
                  {index < 3 ? (
                    <CheckCircleIcon className="w-5 h-5" />
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </div>
                <span className="text-xs text-saturn-700 mt-2 font-medium">{step}</span>
                {index < 4 && (
                  <div
                    className={`absolute w-full h-0.5 top-5 left-1/2 -z-10 ${
                      index < 3 ? 'bg-emerald-500' : 'bg-pearl-200'
                    }`}
                    style={{ width: 'calc(100% - 40px)' }}
                  />
                )}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
