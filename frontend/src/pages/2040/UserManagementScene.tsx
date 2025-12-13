import React from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { VolumetricTable, VolumetricBadge } from '../../components/2040/VolumetricTable';
import { AIInsightBar } from '../../components/2040/AIInsightBar';

export default function UserManagementScene() {
  const users = [
    { id: '1', name: 'Admin User', email: 'admin@rnrl.com', role: 'admin', status: 'active' },
    { id: '2', name: 'Trade Manager', email: 'trade@rnrl.com', role: 'manager', status: 'active' },
  ];

  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
          Internal User Management
        </h1>
        <p className="text-sm text-pearl-300">
          Manage internal users, roles, and permissions
        </p>
      </HoloPanel>

      <HoloPanel theme="pearl" className="p-6">
        <VolumetricTable
          data={users}
          columns={[
            { key: 'name', label: 'Name' },
            { key: 'email', label: 'Email' },
            { key: 'role', label: 'Role', width: '120px' },
            {
              key: 'status',
              label: 'Status',
              width: '120px',
              render: (value) => <VolumetricBadge status={value}>{value.toUpperCase()}</VolumetricBadge>,
            },
          ]}
          keyExtractor={(row) => row.id}
        />
      </HoloPanel>

      <AIInsightBar module="users" context={{ users }} />
    </div>
  );
}
