/**
 * User & Access Management Module
 * Style: Card grid + profile holograms
 * Purpose: Identity-centric visual design
 */

import { useState } from 'react';
import { 
  UserCircleIcon,
  ShieldCheckIcon,
  KeyIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

interface User {
  id: string;
  name: string;
  role: string;
  email: string;
  status: 'active' | 'inactive' | 'pending';
  lastLogin: Date;
  permissions: string[];
  avatar: string;
}

export function UserManagementPage() {
  const [users] = useState<User[]>([
    {
      id: 'U001',
      name: 'Rajkumar Rungta',
      role: 'Director',
      email: 'rajkumar@rnrl.com',
      status: 'active',
      lastLogin: new Date('2024-12-05T14:30:00'),
      permissions: ['All Access', 'Trade Approval', 'System Admin'],
      avatar: 'RK',
    },
    {
      id: 'U002',
      name: 'Naman Rungta',
      role: 'Operations Manager',
      email: 'naman@rnrl.com',
      status: 'active',
      lastLogin: new Date('2024-12-05T13:15:00'),
      permissions: ['Trade Management', 'Settlement', 'Reports'],
      avatar: 'NR',
    },
    {
      id: 'U003',
      name: 'Lekha Rungta',
      role: 'Compliance Officer',
      email: 'lekha@rnrl.com',
      status: 'active',
      lastLogin: new Date('2024-12-05T09:45:00'),
      permissions: ['Compliance', 'Audit', 'Partner Verification'],
      avatar: 'LR',
    },
    {
      id: 'U004',
      name: 'Trade Analyst',
      role: 'Analyst',
      email: 'analyst@rnrl.com',
      status: 'pending',
      lastLogin: new Date('2024-12-04T16:20:00'),
      permissions: ['Read Only'],
      avatar: 'TA',
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'border-emerald-400 bg-emerald-500/10';
      case 'pending':
        return 'border-sun-400 bg-sun-500/10';
      default:
        return 'border-saturn-400 bg-saturn-500/10';
    }
  };

  const getAvatarGradient = (index: number) => {
    const gradients = [
      'from-sun-400 via-saturn-500 to-mars-500',
      'from-saturn-400 via-sun-500 to-emerald-500',
      'from-mars-400 via-sun-500 to-saturn-500',
      'from-emerald-400 via-saturn-500 to-sun-500',
    ];
    return gradients[index % gradients.length];
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-heading font-bold text-space-900">User & Access Management</h1>
          <p className="text-saturn-600 mt-1">Manage team members and permissions</p>
        </div>
        <button className="px-6 py-3 bg-gradient-to-r from-saturn-500 to-sun-500 hover:from-saturn-600 hover:to-sun-600 text-white font-heading font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-120">
          + Add User
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Users', value: '28', icon: UserCircleIcon, color: 'saturn' },
          { label: 'Active Now', value: '12', icon: ShieldCheckIcon, color: 'emerald' },
          { label: 'Pending', value: '3', icon: ClockIcon, color: 'sun' },
          { label: 'Access Roles', value: '8', icon: KeyIcon, color: 'mars' },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="bg-white border-2 border-saturn-100 rounded-xl p-5 hover:border-saturn-200 hover:shadow-lg transition-all duration-120"
            >
              <Icon className={`w-6 h-6 text-${stat.color}-600 mb-3`} />
              <p className="text-2xl font-heading font-bold text-space-900 font-mono">{stat.value}</p>
              <p className="text-sm text-saturn-600 mt-1">{stat.label}</p>
            </div>
          );
        })}
      </div>

      {/* User Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user, index) => (
          <div
            key={user.id}
            className={`relative bg-white border-2 ${getStatusColor(
              user.status
            )} rounded-2xl p-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-120 hover-soft-bloom overflow-hidden group`}
          >
            {/* Holographic shimmer effect on hover */}
            <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 translate-x-full group-hover:translate-x-0" />
            
            <div className="relative z-10">
              {/* Profile Hologram */}
              <div className="flex items-start justify-between mb-4">
                <div className="relative">
                  {/* Holographic ring */}
                  <div
                    className={`absolute -inset-2 bg-gradient-to-br ${getAvatarGradient(
                      index
                    )} rounded-full opacity-20 blur-lg group-hover:opacity-40 transition-opacity duration-300`}
                  />
                  
                  {/* Avatar */}
                  <div
                    className={`relative w-16 h-16 rounded-full bg-gradient-to-br ${getAvatarGradient(
                      index
                    )} flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform duration-300`}
                  >
                    <span className="text-white font-heading font-bold text-lg">{user.avatar}</span>
                  </div>
                  
                  {/* Status indicator */}
                  <div
                    className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-2 border-white ${
                      user.status === 'active'
                        ? 'bg-emerald-500'
                        : user.status === 'pending'
                        ? 'bg-sun-500'
                        : 'bg-saturn-400'
                    }`}
                  />
                </div>

                <span
                  className={`px-3 py-1 text-xs font-bold rounded-full ${
                    user.status === 'active'
                      ? 'bg-emerald-100 text-emerald-700'
                      : user.status === 'pending'
                      ? 'bg-sun-100 text-sun-700'
                      : 'bg-saturn-100 text-saturn-700'
                  }`}
                >
                  {user.status.toUpperCase()}
                </span>
              </div>

              {/* User Info */}
              <div className="mb-4">
                <h3 className="text-lg font-heading font-bold text-space-900 mb-1">{user.name}</h3>
                <p className="text-sm text-saturn-600 font-medium">{user.role}</p>
                <p className="text-xs text-saturn-500 mt-1 font-mono">{user.email}</p>
              </div>

              {/* Last Login */}
              <div className="flex items-center gap-2 text-xs text-saturn-600 mb-4 pb-4 border-b border-saturn-200">
                <ClockIcon className="w-4 h-4" />
                <span className="font-mono">
                  Last login: {user.lastLogin.toLocaleString('en-IN', { 
                    month: 'short', 
                    day: 'numeric', 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>

              {/* Permissions */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <KeyIcon className="w-4 h-4 text-saturn-500" />
                  <span className="text-xs font-bold text-saturn-700">PERMISSIONS</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {user.permissions.map((perm) => (
                    <span
                      key={perm}
                      className="px-2 py-1 text-xs font-medium bg-saturn-100 text-saturn-700 rounded-lg border border-saturn-200"
                    >
                      {perm}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-4 pt-4 border-t border-saturn-200 flex gap-2">
                <button className="flex-1 px-3 py-2 text-sm font-medium text-saturn-700 hover:text-space-900 hover:bg-saturn-50 rounded-lg transition-colors duration-120">
                  Edit
                </button>
                <button className="flex-1 px-3 py-2 text-sm font-medium text-saturn-700 hover:text-space-900 hover:bg-saturn-50 rounded-lg transition-colors duration-120">
                  Manage
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Role Matrix */}
      <div className="bg-white border-2 border-saturn-100 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b-2 border-saturn-100 bg-saturn-50/30">
          <h2 className="text-lg font-heading font-bold text-space-900">Permission Matrix</h2>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-5 gap-4">
            <div className="font-heading font-bold text-space-900">Role</div>
            <div className="text-center font-heading font-bold text-space-900">Trade</div>
            <div className="text-center font-heading font-bold text-space-900">Settlement</div>
            <div className="text-center font-heading font-bold text-space-900">Reports</div>
            <div className="text-center font-heading font-bold text-space-900">Admin</div>
            
            {['Director', 'Manager', 'Analyst', 'Operator'].map((role) => (
              <>
                <div key={role} className="font-medium text-saturn-700">{role}</div>
                {[true, true, true, role === 'Director'].map((has, idx) => (
                  <div key={idx} className="text-center">
                    {has ? (
                      <CheckCircleIcon className="w-5 h-5 text-emerald-600 mx-auto" />
                    ) : (
                      <div className="w-5 h-5 border-2 border-saturn-200 rounded-full mx-auto" />
                    )}
                  </div>
                ))}
              </>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function CheckCircleIcon(props: any) {
  return (
    <svg {...props} fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
    </svg>
  );
}
