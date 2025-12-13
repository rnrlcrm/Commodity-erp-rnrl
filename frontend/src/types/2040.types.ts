// 2040 Design System Types
export interface HoloTheme {
  palette: 'saturn' | 'sun' | 'mars' | 'pearl' | 'space';
  intensity: 'subtle' | 'normal' | 'strong';
  glow: boolean;
}

export interface VolumetricTransform {
  translateZ: number;
  rotateX: number;
  rotateY: number;
  scale: number;
}

export interface SceneMemory {
  id: string;
  name: string;
  cameraAngle: { x: number; y: number; z: number };
  pinnedPanels: string[];
  activeFilters: Record<string, any>;
  aiContext: AIContextState;
  timestamp: number;
}

export interface AIContextState {
  predictions: AIPrediction[];
  suggestions: AISuggestion[];
  automations: AIAutomation[];
  insights: AIInsight[];
}

export interface AIPrediction {
  id: string;
  type: 'risk' | 'opportunity' | 'trend' | 'anomaly';
  confidence: number;
  message: string;
  data: any;
  timestamp: number;
}

export interface AISuggestion {
  id: string;
  module: string;
  action: string;
  reason: string;
  impact: string;
  confidence: number;
  acceptAction: () => void;
  rejectAction: () => void;
}

export interface AIAutomation {
  id: string;
  module: string;
  trigger: string;
  action: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
}

export interface AIInsight {
  id: string;
  category: 'optimization' | 'compliance' | 'efficiency' | 'risk';
  title: string;
  description: string;
  actionable: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface RealtimeChannel {
  channel: string;
  topic: string;
  handler: (data: any) => void;
}

export interface ModuleScene {
  id: string;
  name: string;
  icon: string;
  path: string;
  aiOrchestrator: string;
  realtimeChannels: string[];
}

// Back Office Modules
export const BACKOFFICE_MODULES: ModuleScene[] = [
  {
    id: 'settings',
    name: 'Settings',
    icon: 'settings',
    path: '/2040/settings',
    aiOrchestrator: 'settings',
    realtimeChannels: ['settings.config', 'settings.sync'],
  },
  {
    id: 'user-management',
    name: 'Internal User Management',
    icon: 'users',
    path: '/2040/users',
    aiOrchestrator: 'users',
    realtimeChannels: ['users.activities', 'users.permissions'],
  },
  {
    id: 'partner-management',
    name: 'Business Partner Management',
    icon: 'building',
    path: '/2040/partners',
    aiOrchestrator: 'partners',
    realtimeChannels: ['partners.kyc', 'partners.credit'],
  },
  {
    id: 'trade-desk',
    name: 'Trade Desk (Back Office Ops)',
    icon: 'chart',
    path: '/2040/trade-desk',
    aiOrchestrator: 'trade-desk',
    realtimeChannels: ['trade.ticks', 'trade.executions', 'trade.reconciliation'],
  },
  {
    id: 'quality',
    name: 'Quality Management',
    icon: 'check-circle',
    path: '/2040/quality',
    aiOrchestrator: 'quality',
    realtimeChannels: ['quality.inspections', 'quality.reports'],
  },
  {
    id: 'logistics',
    name: 'Logistics',
    icon: 'truck',
    path: '/2040/logistics',
    aiOrchestrator: 'logistics',
    realtimeChannels: ['logistics.shipments', 'logistics.tracking'],
  },
  {
    id: 'delivery',
    name: 'Delivery Management',
    icon: 'package',
    path: '/2040/delivery',
    aiOrchestrator: 'delivery',
    realtimeChannels: ['delivery.schedules', 'delivery.confirmations'],
  },
  {
    id: 'accounts',
    name: 'Accounts & Settlement',
    icon: 'dollar',
    path: '/2040/accounts',
    aiOrchestrator: 'accounts',
    realtimeChannels: ['accounts.transactions', 'accounts.reconciliation'],
  },
  {
    id: 'disputes',
    name: 'Dispute Management',
    icon: 'alert-triangle',
    path: '/2040/disputes',
    aiOrchestrator: 'disputes',
    realtimeChannels: ['disputes.cases', 'disputes.resolutions'],
  },
  {
    id: 'audit',
    name: 'Audit Timeline Stream',
    icon: 'clock',
    path: '/2040/audit',
    aiOrchestrator: 'audit',
    realtimeChannels: ['audit.events', 'audit.compliance'],
  },
  {
    id: 'documents',
    name: 'Document Intelligence System',
    icon: 'file',
    path: '/2040/documents',
    aiOrchestrator: 'documents',
    realtimeChannels: ['documents.ocr', 'documents.classification'],
  },
];

// Keyboard shortcuts for Command Halo
export const COMMAND_SHORTCUTS = {
  OPEN_HALO: 'Meta+Shift+Space',
  QUICK_SEARCH: 'Meta+K',
  AI_ASSIST: 'Meta+Shift+A',
  SAVE_SCENE: 'Meta+S',
  TOGGLE_AI: 'Meta+Shift+I',
};

// Motion reduction preferences
export interface MotionPreferences {
  reducedMotion: boolean;
  disableVolumetric: boolean;
  simplifyGlow: boolean;
}
