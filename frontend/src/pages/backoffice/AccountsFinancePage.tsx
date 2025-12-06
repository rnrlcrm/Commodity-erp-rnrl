/**
 * Accounts & Finance Module
 * Style: Ledger-centric, neutral theme
 * Purpose: Respect financial focus with clean numbers-first design
 */

import { useState } from 'react';
import { 
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  DocumentTextIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';

interface Transaction {
  id: string;
  date: Date;
  type: 'debit' | 'credit';
  category: string;
  description: string;
  amount: number;
  balance: number;
  reference: string;
}

interface Account {
  name: string;
  number: string;
  balance: number;
  currency: string;
}

export function AccountsFinancePage() {
  const [accounts] = useState<Account[]>([
    { name: 'Operating Account', number: 'ACC-2024-001', balance: 45678900, currency: 'INR' },
    { name: 'Settlement Account', number: 'ACC-2024-002', balance: 23456780, currency: 'INR' },
    { name: 'Reserve Fund', number: 'ACC-2024-003', balance: 12345670, currency: 'INR' },
  ]);

  const [transactions] = useState<Transaction[]>([
    {
      id: 'TXN001',
      date: new Date('2024-12-05T14:30:00'),
      type: 'credit',
      category: 'Trade Settlement',
      description: 'Settlement received - TR2024-0156',
      amount: 2847500,
      balance: 45678900,
      reference: 'ST001',
    },
    {
      id: 'TXN002',
      date: new Date('2024-12-05T13:15:00'),
      type: 'debit',
      category: 'Trade Payment',
      description: 'Payment to Global Cotton Corp',
      amount: 1234000,
      balance: 42831400,
      reference: 'ST002',
    },
    {
      id: 'TXN003',
      date: new Date('2024-12-05T10:45:00'),
      type: 'credit',
      category: 'Commission',
      description: 'Brokerage commission - Multiple trades',
      amount: 156700,
      balance: 44065400,
      reference: 'COM-124',
    },
    {
      id: 'TXN004',
      date: new Date('2024-12-05T09:20:00'),
      type: 'debit',
      category: 'Operating Expense',
      description: 'Platform maintenance fee',
      amount: 45000,
      balance: 43908700,
      reference: 'EXP-089',
    },
  ]);

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header - Professional Financial */}
      <div className="bg-gradient-to-r from-space-900 to-space-800 rounded-xl p-6 border border-saturn-700/30">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-bold text-white">Accounts & Finance</h1>
            <p className="text-saturn-300 mt-1 font-mono">
              Financial Period: FY 2024-25 • As of {new Date().toLocaleDateString('en-IN')}
            </p>
          </div>
          <div className="flex items-center gap-2 bg-emerald-500/20 text-emerald-400 px-4 py-2 rounded-lg border border-emerald-500/30">
            <DocumentTextIcon className="w-5 h-5" />
            <span className="font-heading font-bold">Books Balanced</span>
          </div>
        </div>
      </div>

      {/* Account Cards - Ledger Style */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {accounts.map((account) => (
          <div
            key={account.number}
            className="bg-white border-2 border-space-200 rounded-xl p-6 hover:border-saturn-400 hover:shadow-xl transition-all duration-120"
          >
            <div className="flex items-start justify-between mb-4">
              <CurrencyDollarIcon className="w-6 h-6 text-emerald-600" />
              <span className="text-xs font-mono text-saturn-500">{account.number}</span>
            </div>
            <h3 className="font-heading font-bold text-space-900 mb-2">{account.name}</h3>
            <p className="text-3xl font-mono font-bold text-space-900">
              {formatAmount(account.balance)}
            </p>
            <p className="text-xs text-saturn-600 mt-1 font-mono">{account.currency}</p>
          </div>
        ))}
      </div>

      {/* Financial Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Credits', value: '₹42.8Cr', change: '+12.4%', trend: 'up' },
          { label: 'Total Debits', value: '₹28.3Cr', change: '+8.2%', trend: 'up' },
          { label: 'Net Position', value: '₹14.5Cr', change: '+24.1%', trend: 'up' },
          { label: 'Pending', value: '₹2.1Cr', change: '-5.3%', trend: 'down' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white border-2 border-space-200 rounded-xl p-5 hover:shadow-md transition-shadow duration-120"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-saturn-600 uppercase">{stat.label}</span>
              <div className={`flex items-center gap-1 text-xs font-bold ${
                stat.trend === 'up' ? 'text-emerald-600' : 'text-mars-600'
              }`}>
                {stat.trend === 'up' ? (
                  <ArrowTrendingUpIcon className="w-3 h-3" />
                ) : (
                  <ArrowTrendingDownIcon className="w-3 h-3" />
                )}
                <span>{stat.change}</span>
              </div>
            </div>
            <p className="text-2xl font-mono font-bold text-space-900">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Transaction Ledger */}
      <div className="bg-white border-2 border-space-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b-2 border-space-200 bg-space-50">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-heading font-bold text-space-900">Transaction Ledger</h2>
            <button className="text-sm text-saturn-600 hover:text-space-900 font-medium transition-colors duration-120">
              Export to Excel
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-space-50 border-b-2 border-space-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase font-mono">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase font-mono">
                  TXN ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase font-mono">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-bold text-space-900 uppercase font-mono">
                  Category
                </th>
                <th className="px-6 py-3 text-right text-xs font-bold text-space-900 uppercase font-mono">
                  Debit
                </th>
                <th className="px-6 py-3 text-right text-xs font-bold text-space-900 uppercase font-mono">
                  Credit
                </th>
                <th className="px-6 py-3 text-right text-xs font-bold text-space-900 uppercase font-mono">
                  Balance
                </th>
                <th className="px-6 py-3 text-center text-xs font-bold text-space-900 uppercase font-mono">
                  Ref
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-200">
              {transactions.map((txn) => (
                <tr key={txn.id} className="hover:bg-space-50 transition-colors duration-120">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <CalendarIcon className="w-4 h-4 text-saturn-500" />
                      <span className="font-mono text-xs text-space-900">
                        {txn.date.toLocaleDateString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm font-medium text-space-900">{txn.id}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-space-900">{txn.description}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs font-medium bg-saturn-100 text-saturn-700 rounded">
                      {txn.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {txn.type === 'debit' ? (
                      <span className="font-mono text-sm font-bold text-mars-700">
                        {formatAmount(txn.amount)}
                      </span>
                    ) : (
                      <span className="font-mono text-sm text-saturn-400">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {txn.type === 'credit' ? (
                      <span className="font-mono text-sm font-bold text-emerald-700">
                        {formatAmount(txn.amount)}
                      </span>
                    ) : (
                      <span className="font-mono text-sm text-saturn-400">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono text-sm font-bold text-space-900">
                      {formatAmount(txn.balance)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="font-mono text-xs text-saturn-600">{txn.reference}</span>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-space-100 border-t-2 border-space-300">
              <tr>
                <td colSpan={4} className="px-6 py-4 text-right font-bold text-space-900">
                  Closing Balance:
                </td>
                <td className="px-6 py-4 text-right font-mono font-bold text-mars-700">
                  {formatAmount(1279000)}
                </td>
                <td className="px-6 py-4 text-right font-mono font-bold text-emerald-700">
                  {formatAmount(3004200)}
                </td>
                <td className="px-6 py-4 text-right font-mono font-bold text-space-900 text-lg">
                  {formatAmount(45678900)}
                </td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}
