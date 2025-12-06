import { useState, useEffect, useRef } from 'react';
import {
  ChartBarIcon,
  UsersIcon,
  CurrencyDollarIcon,
  ShieldCheckIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  SparklesIcon,
  ChevronRightIcon,
  LightBulbIcon,
  ChartPieIcon,
  BellAlertIcon,
  MicrophoneIcon,
  CheckCircleIcon,
  XCircleIcon,
  BoltIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';

const stats = [
  { name: 'Active Trades', value: '2,847', change: '+12%', icon: ChartBarIcon, trend: 'up' },
  { name: 'Total Partners', value: '1,284', change: '+8%', icon: UsersIcon, trend: 'up' },
  { name: 'Today\'s Volume', value: '₹42.8Cr', change: '+24%', icon: CurrencyDollarIcon, trend: 'up' },
  { name: 'Risk Score', value: '92/100', change: 'Excellent', icon: ShieldCheckIcon, trend: 'stable' },
];

const recentActivities = [
  { id: 1, title: 'New trade request from ABC Textiles', time: '2 mins ago', type: 'trade', status: 'pending' },
  { id: 2, title: 'Contract RNRL-2024-0156 approved', time: '15 mins ago', type: 'contract', status: 'success' },
  { id: 3, title: 'Partner verification completed', time: '1 hour ago', type: 'partner', status: 'success' },
  { id: 4, title: 'International shipment dispatched', time: '3 hours ago', type: 'logistics', status: 'info' },
];

const aiInsights = [
  { icon: '📈', title: 'Market Trend', message: 'Cotton prices trending up 3.2% this week', color: 'sun' },
  { icon: '🎯', title: 'Opportunity', message: '5 high-value partners ready for engagement', color: 'mars' },
  { icon: '⚡', title: 'Alert', message: 'Optimal time to close pending trades', color: 'saturn' },
];

const intelligenceAdvisories = [
  { 
    icon: ChartPieIcon, 
    type: 'Predictive Analysis', 
    message: 'Anticipated 15% increase in cotton demand over next quarter based on historical patterns',
    confidence: 87,
    priority: 'medium'
  },
  { 
    icon: LightBulbIcon, 
    type: 'Strategic Insight', 
    message: 'Optimal inventory rebalancing window detected for 12-18 Dec period',
    confidence: 92,
    priority: 'high'
  },
  { 
    icon: BellAlertIcon, 
    type: 'Risk Advisory', 
    message: 'Monitor partner creditworthiness - 3 accounts showing early warning indicators',
    confidence: 78,
    priority: 'high'
  },
];

export function DashboardPage() {
  const [advisoryPanelOpen, setAdvisoryPanelOpen] = useState(false);
  
  // 🧠 2040 Voice-First & Conversational UI
  const [voiceActive, setVoiceActive] = useState(false);
  const [voiceCommand, setVoiceCommand] = useState('');
  const [conversationHistory, setConversationHistory] = useState<Array<{role: 'user' | 'system', message: string, timestamp: Date}>>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // 🧠 Decision & Approval UI
  const [pendingApprovals, setPendingApprovals] = useState<Array<{
    id: string;
    type: 'trade' | 'risk' | 'settlement';
    title: string;
    amount: string;
    riskLevel: number;
    recommendation: 'approve' | 'reject' | 'review';
    aiConfidence: number;
    data: any;
  }>>([]);
  
  // 🧠 Quantum Visualization State
  const [quantumMode, setQuantumMode] = useState(false);
  const [riskFields, setRiskFields] = useState<Array<{x: number, y: number, intensity: number}>>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // 🧠 Gaze Control - Large Hit Zones
  const [gazeTarget, setGazeTarget] = useState<string | null>(null);
  
  // Debug gaze tracking (optional - can be removed in production)
  useEffect(() => {
    if (gazeTarget) {
      console.log('Gaze tracking:', gazeTarget);
    }
  }, [gazeTarget]);
  
  // Simulate voice recognition
  useEffect(() => {
    if (voiceActive) {
      const timeout = setTimeout(() => {
        setVoiceActive(false);
        if (voiceCommand.trim()) {
          handleVoiceCommand(voiceCommand);
        }
      }, 3000);
      return () => clearTimeout(timeout);
    }
  }, [voiceActive, voiceCommand]);
  
  // 🧠 Quantum Risk Visualization
  useEffect(() => {
    if (!quantumMode || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Animate quantum risk fields
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      riskFields.forEach(field => {
        const gradient = ctx.createRadialGradient(field.x, field.y, 0, field.x, field.y, 100);
        gradient.addColorStop(0, `rgba(255, 107, 107, ${field.intensity})`);
        gradient.addColorStop(0.5, `rgba(255, 179, 71, ${field.intensity * 0.5})`);
        gradient.addColorStop(1, 'rgba(255, 107, 107, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(field.x, field.y, 100, 0, Math.PI * 2);
        ctx.fill();
      });
      
      requestAnimationFrame(animate);
    };
    
    animate();
  }, [quantumMode, riskFields]);
  
  // Initialize quantum risk fields
  useEffect(() => {
    setRiskFields([
      { x: 200, y: 150, intensity: 0.8 },
      { x: 600, y: 250, intensity: 0.6 },
      { x: 900, y: 180, intensity: 0.9 },
    ]);
    
    // Simulate pending approvals
    setPendingApprovals([
      {
        id: 'APR-001',
        type: 'trade',
        title: 'High-value trade with XYZ Corp',
        amount: '₹12.5Cr',
        riskLevel: 4,
        recommendation: 'review',
        aiConfidence: 78,
        data: { client: 'XYZ Corp', quantity: '500 tons', delivery: '15-Jan-2025' }
      },
      {
        id: 'APR-002',
        type: 'risk',
        title: 'Credit limit increase for ABC Textiles',
        amount: '₹8.2Cr',
        riskLevel: 2,
        recommendation: 'approve',
        aiConfidence: 94,
        data: { client: 'ABC Textiles', currentLimit: '₹5Cr', requestedLimit: '₹8.2Cr' }
      },
    ]);
  }, []);
  
  const handleVoiceCommand = (command: string) => {
    setIsProcessing(true);
    setConversationHistory(prev => [...prev, { role: 'user', message: command, timestamp: new Date() }]);
    
    // Simulate AI processing
    setTimeout(() => {
      let response = '';
      
      if (command.toLowerCase().includes('unsettled') && command.includes('10')) {
        response = 'Found 3 unsettled trades over ₹10Cr with risk level 4+: Trade #2847 (₹12.5Cr, Risk 4), Trade #2891 (₹15.2Cr, Risk 5), Trade #2903 (₹11.8Cr, Risk 4). Building dynamic view...';
      } else if (command.toLowerCase().includes('ledger') || command.toLowerCase().includes('summary')) {
        const clientMatch = command.match(/client ([A-Z]+)/i);
        const client = clientMatch ? clientMatch[1] : 'XYZ Corp';
        response = `Generating ledger summary for ${client}... Total outstanding: ₹42.3Cr, Pending invoices: 12, Average payment cycle: 28 days. Risk score: 92/100. Recommend approval for new trades up to ₹15Cr.`;
      } else if (command.toLowerCase().includes('risk')) {
        response = 'Current portfolio risk: 92/100 (Excellent). 3 high-risk trades detected. Quantum visualization activated. Fraud detection neural scan: All clear. Settlement cycles: 94% on-time.';
      } else {
        response = 'Command processed. Data validated. Risk predicted. Awaiting your approval for recommended actions.';
      }
      
      setConversationHistory(prev => [...prev, { role: 'system', message: response, timestamp: new Date() }]);
      setIsProcessing(false);
      setVoiceCommand('');
    }, 1500);
  };
  
  const handleApproval = (id: string, action: 'approve' | 'reject') => {
    setPendingApprovals(prev => prev.filter(a => a.id !== id));
    setConversationHistory(prev => [...prev, {
      role: 'system',
      message: `Approval ${action === 'approve' ? 'GRANTED' : 'REJECTED'} for ${id}. ${action === 'approve' ? 'Processing trade execution...' : 'Trade cancelled and archived.'}`,
      timestamp: new Date()
    }]);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Premium Welcome Banner - 2040 Vision Enhanced */}
      <div className="relative overflow-hidden bg-gradient-to-r from-saturn-600 via-sun-500 to-saturn-700 p-8 rounded-2xl shadow-2xl shadow-saturn-500/30">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-20"></div>
        <div className="relative flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white flex items-center gap-3">
              RNRL Live Trading Hub
              <span className="relative inline-flex">
                <span className="w-2.5 h-2.5 bg-emerald-400 rounded-full shadow-lg shadow-emerald-400/50"></span>
                <span className="absolute inset-0 w-2.5 h-2.5 bg-emerald-300 rounded-full opacity-75" style={{ animation: 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite' }}></span>
              </span>
            </h2>
            <p className="text-white/95 mt-2 text-lg flex items-center gap-3">
              <span>Global Commodity Trading Platform</span>
              <span className="text-xs bg-white/25 backdrop-blur-sm px-3 py-1 rounded-full border border-white/40 font-semibold">LIVE • 2040 VISION</span>
            </p>
          </div>
          <div className="hidden lg:block glass-card bg-white/10 backdrop-blur-md border border-white/20 px-5 py-3 rounded-xl shadow-xl z-10">
            <div className="flex items-center gap-2 text-white/90">
              <ClockIcon className="w-5 h-5" />
              <div>
                <div className="text-sm font-bold tracking-wide">{new Date().toLocaleDateString('en-US', { weekday: 'long' })}</div>
                <div className="text-xs opacity-90 font-medium">{new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Premium Stats Grid - Enhanced 2040 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.name}
              className="relative p-6 glass-neo border border-saturn-200/50 rounded-2xl hover:shadow-lg hover:shadow-saturn-500/20 transition-shadow duration-200 group overflow-hidden cursor-default select-none"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Optimized hover effect */}
              <div className="absolute inset-0 bg-saturn-50/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-saturn-100/80 rounded-xl group-hover:scale-105 transition-transform duration-150 shadow-md shadow-saturn-500/15">
                    <Icon className="w-6 h-6 text-saturn-600 group-hover:text-sun-600 transition-colors duration-150" />
                  </div>
                  {stat.trend === 'up' && (
                    <div className="flex items-center gap-1 text-emerald-600 text-xs font-bold bg-emerald-50/80 px-2 py-1 rounded-lg">
                      <ArrowTrendingUpIcon className="w-3 h-3" />
                      <span>{stat.change}</span>
                    </div>
                  )}
                  {stat.trend === 'stable' && (
                    <div className="text-xs font-bold text-saturn-700 bg-saturn-100/80 px-2 py-1 rounded-lg">
                      {stat.change}
                    </div>
                  )}
                </div>
                
                <div>
                  <p className="text-sm text-saturn-600 font-medium mb-1">{stat.name}</p>
                  <p className="text-3xl font-bold text-saturn-900 group-hover:text-sun-600 transition-colors duration-500">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 🧠 2040 VOICE-FIRST CONVERSATIONAL UI - Fixed Top Right */}
      <div className="fixed top-20 right-4 md:right-6 z-40 w-full md:w-96 px-4 md:px-0">
        {/* Voice Command Button - MASSIVE HIT ZONE */}
        <button
          onClick={() => setVoiceActive(!voiceActive)}
          onMouseEnter={() => setGazeTarget('voice')}
          onMouseLeave={() => setGazeTarget(null)}
          className={`w-full min-h-[80px] glass-neo border-2 ${
            voiceActive 
              ? 'border-mars-400 bg-mars-50/80 shadow-2xl shadow-mars-500/40' 
              : 'border-sun-400/60 bg-gradient-to-br from-sun-50 to-saturn-50 hover:shadow-xl hover:shadow-sun-500/30'
          } rounded-2xl p-5 transition-all duration-150 group cursor-pointer select-none active:scale-[0.98]`}
          aria-label={voiceActive ? "Stop voice recording" : "Start voice command"}
          aria-pressed={voiceActive}
        >
          <div className="flex items-center gap-4">
            <div className={`relative p-4 rounded-2xl ${voiceActive ? 'bg-mars-500' : 'bg-sun-500 group-hover:bg-sun-600'} transition-colors duration-150 shadow-lg`}>
              <MicrophoneIcon className="w-8 h-8 text-white" />
              {voiceActive && (
                <div className="absolute inset-0 rounded-2xl border-4 border-mars-300 animate-pulse" />
              )}
            </div>
            <div className="flex-1 text-left">
              <div className="text-lg font-bold text-saturn-900">
                {voiceActive ? 'Listening...' : 'Voice Command'}
              </div>
              <div className="text-xs text-saturn-600 font-medium mt-0.5">
                {voiceActive ? 'Speak your command now' : 'Click to activate • 2040 AI'}
              </div>
            </div>
            <BoltIcon className={`w-6 h-6 ${voiceActive ? 'text-mars-600 animate-pulse' : 'text-sun-600'}`} />
          </div>
        </button>
        
        {/* Live Voice Input */}
        {voiceActive && (
          <div className="mt-3 p-5 glass-neo border-2 border-mars-400/60 rounded-2xl shadow-2xl shadow-mars-500/30 animate-fadeIn bg-white/95 backdrop-blur-xl">
            <input
              type="text"
              value={voiceCommand}
              onChange={(e) => setVoiceCommand(e.target.value)}
              placeholder="e.g., Show unsettled trades over ₹10Cr with risk above level 4"
              className="w-full px-4 py-4 bg-white border-2 border-mars-300/50 rounded-xl text-saturn-900 placeholder-saturn-400 focus:outline-none focus:ring-2 focus:ring-mars-500/60 focus:border-mars-500 transition-all duration-150 text-sm font-medium"
              autoFocus
            />
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => {
                  setVoiceActive(false);
                  if (voiceCommand.trim()) handleVoiceCommand(voiceCommand);
                }}
                className="flex-1 py-3 bg-mars-500 hover:bg-mars-600 text-white font-bold rounded-xl transition-all duration-150 active:scale-[0.98] shadow-lg shadow-mars-500/30 text-sm"
              >
                Execute Command
              </button>
              <button
                onClick={() => {
                  setVoiceActive(false);
                  setVoiceCommand('');
                }}
                className="px-4 py-3 bg-saturn-100 hover:bg-saturn-200 text-saturn-700 font-semibold rounded-xl transition-all duration-150 active:scale-[0.98] text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
        
        {/* Conversational History - Auto-expand when messages exist */}
        {conversationHistory.length > 0 && (
          <div className="mt-3 max-h-[280px] overflow-y-auto glass-neo border border-saturn-200/60 rounded-xl p-3 space-y-2 shadow-lg animate-fadeIn bg-white/90 backdrop-blur-xl">
            <div className="flex items-center justify-between pb-2 border-b border-saturn-200/60">
              <h3 className="text-xs font-bold text-saturn-700 uppercase tracking-wide">AI Conversation</h3>
              <button
                onClick={() => setConversationHistory([])}
                className="text-xs text-saturn-500 hover:text-mars-600 font-medium hover:underline transition-colors"
              >
                Clear
              </button>
            </div>
            {conversationHistory.map((msg, idx) => (
              <div key={idx} className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-sun-50/60 border border-sun-200/40' : 'bg-saturn-50/60 border border-saturn-200/40'} animate-fadeIn`}>
                <div className="flex items-start gap-2">
                  <div className={`w-6 h-6 rounded-md flex items-center justify-center ${msg.role === 'user' ? 'bg-sun-500' : 'bg-saturn-600'} shadow-sm flex-shrink-0`}>
                    <span className="text-white text-[10px] font-bold">{msg.role === 'user' ? 'U' : 'AI'}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-saturn-800 leading-relaxed">{msg.message}</p>
                    <p className="text-[10px] text-saturn-400 mt-1">{msg.timestamp.toLocaleTimeString()}</p>
                  </div>
                </div>
              </div>
            ))}
            {isProcessing && (
              <div className="p-3 bg-saturn-50/60 border border-saturn-200/40 rounded-lg animate-fadeIn">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-saturn-600 flex items-center justify-center shadow-sm">
                    <SparklesIcon className="w-4 h-4 text-white animate-pulse" />
                  </div>
                  <p className="text-xs text-saturn-700">Processing...</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 🧠 2040 DECISION & APPROVAL UI - Fixed Bottom (Above Advisory Panel) */}
      {pendingApprovals.length > 0 && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-45 w-[90%] max-w-4xl">
          <div className="glass-neo border-2 border-sun-400/80 rounded-2xl shadow-2xl shadow-sun-500/40 p-6 bg-white/95 backdrop-blur-xl animate-fadeIn">
            <div className="flex items-center justify-between mb-5 pb-4 border-b-2 border-sun-200/60">
              <h2 className="text-xl font-bold text-saturn-900 flex items-center gap-3">
                <BellAlertIcon className="w-7 h-7 text-sun-600" />
                Pending AI Recommendations
                <span className="text-sm bg-mars-100 text-mars-700 px-3 py-1 rounded-full font-bold">{pendingApprovals.length} Awaiting Decision</span>
              </h2>
            </div>
            
            <div className="space-y-4">
              {pendingApprovals.map((approval) => (
                <div key={approval.id} className="p-5 bg-gradient-to-br from-pearl-50 to-sun-50/40 border-2 border-saturn-200/60 rounded-2xl hover:shadow-lg hover:shadow-saturn-500/15 transition-all duration-150">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-bold text-saturn-900">{approval.title}</h3>
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${approval.recommendation === 'approve' ? 'bg-emerald-100 text-emerald-700' : approval.recommendation === 'reject' ? 'bg-mars-100 text-mars-700' : 'bg-sun-100 text-sun-700'}`}>
                          AI: {approval.recommendation.toUpperCase()}
                        </span>
                        <span className="text-xs bg-saturn-100 text-saturn-700 px-2.5 py-1 rounded-full font-bold">
                          {approval.aiConfidence}% Confidence
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div>
                          <p className="text-xs text-saturn-500 font-semibold mb-1">Amount</p>
                          <p className="text-lg font-bold text-saturn-900">{approval.amount}</p>
                        </div>
                        <div>
                          <p className="text-xs text-saturn-500 font-semibold mb-1">Risk Level</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-pearl-200 rounded-full overflow-hidden">
                              <div className={`h-full ${approval.riskLevel > 4 ? 'bg-mars-500' : approval.riskLevel > 2 ? 'bg-sun-500' : 'bg-emerald-500'} transition-all duration-300`} style={{ width: `${approval.riskLevel * 20}%` }} />
                            </div>
                            <span className="text-sm font-bold text-saturn-900">{approval.riskLevel}/5</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-4 p-3 bg-white/60 rounded-xl border border-saturn-200/40">
                        <p className="text-xs text-saturn-600 font-medium">
                          <span className="font-bold text-saturn-900">Details:</span> {JSON.stringify(approval.data, null, 0).slice(0, 120)}...
                        </p>
                      </div>
                    </div>
                    
                    {/* MASSIVE ACTION BUTTONS - GAZE CONTROL */}
                    <div className="flex flex-col gap-3">
                      <button
                        onClick={() => handleApproval(approval.id, 'approve')}
                        onMouseEnter={() => setGazeTarget(`approve-${approval.id}`)}
                        onMouseLeave={() => setGazeTarget(null)}
                        className="min-w-[140px] min-h-[60px] bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-xl shadow-lg shadow-emerald-500/40 hover:shadow-xl hover:shadow-emerald-500/50 transition-all duration-150 active:scale-[0.98] flex items-center justify-center gap-2 px-5"
                      >
                        <CheckCircleIcon className="w-6 h-6" />
                        <span className="text-sm">APPROVE</span>
                      </button>
                      <button
                        onClick={() => handleApproval(approval.id, 'reject')}
                        onMouseEnter={() => setGazeTarget(`reject-${approval.id}`)}
                        onMouseLeave={() => setGazeTarget(null)}
                        className="min-w-[140px] min-h-[60px] bg-mars-500 hover:bg-mars-600 text-white font-bold rounded-xl shadow-lg shadow-mars-500/40 hover:shadow-xl hover:shadow-mars-500/50 transition-all duration-150 active:scale-[0.98] flex items-center justify-center gap-2 px-5"
                      >
                        <XCircleIcon className="w-6 h-6" />
                        <span className="text-sm">REJECT</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 🧠 2040 QUANTUM VISUALIZATION TOGGLE */}
      <div className="fixed top-20 left-6 z-35">
        <button
          onClick={() => setQuantumMode(!quantumMode)}
          onMouseEnter={() => setGazeTarget('quantum')}
          onMouseLeave={() => setGazeTarget(null)}
          className={`min-h-[80px] min-w-[200px] glass-neo border-2 ${quantumMode ? 'border-mars-400 bg-mars-50/80 shadow-2xl shadow-mars-500/40' : 'border-saturn-400/60 hover:shadow-xl hover:shadow-saturn-500/30'} rounded-2xl p-5 transition-all duration-150 active:scale-[0.98] cursor-pointer select-none`}
        >
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl ${quantumMode ? 'bg-mars-500' : 'bg-saturn-500'} shadow-lg transition-colors duration-150`}>
              <EyeIcon className="w-7 h-7 text-white" />
            </div>
            <div className="text-left">
              <div className="text-sm font-bold text-saturn-900">Quantum Risk</div>
              <div className="text-xs text-saturn-600 font-medium">{quantumMode ? 'ACTIVE' : 'Activate'}</div>
            </div>
          </div>
        </button>
      </div>

      {/* Quantum Canvas Overlay */}
      {quantumMode && (
        <div className="fixed inset-0 pointer-events-none z-10">
          <canvas
            ref={canvasRef}
            width={window.innerWidth}
            height={window.innerHeight}
            className="w-full h-full opacity-60"
          />
        </div>
      )}

      {/* Content Grid - Premium 2040 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity - Enhanced */}
        <div className="p-6 glass-neo border border-saturn-200/50 rounded-2xl hover:shadow-md hover:shadow-saturn-200/40 transition-shadow duration-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-saturn-900 flex items-center gap-2">
              Recent Activity
              <span className="w-2 h-2 bg-saturn-500 rounded-full shadow-md shadow-saturn-500/50"></span>
            </h2>
            <button className="text-sm text-sun-600 hover:text-sun-700 font-semibold hover:underline transition-colors">
              View All
            </button>
          </div>
          
          <div className="space-y-3">
            {recentActivities.map((activity, index) => (
              <div
                 key={activity.id}
                 className="relative p-4 glass-card hover:glass-neo rounded-xl border border-pearl-200 hover:border-saturn-300/60 hover:shadow-md hover:shadow-saturn-500/8 transition-all duration-150 group"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="absolute inset-0 bg-saturn-50/30 opacity-0 group-hover:opacity-100 transition-opacity duration-150" />                <div className="flex items-start gap-3 relative z-10">
                  <div className={`w-2 h-2 mt-2 rounded-full shadow-md ${
                    activity.status === 'success' ? 'bg-emerald-500 shadow-emerald-500/50' :
                    activity.status === 'pending' ? 'bg-sun-500 shadow-sun-500/50' :
                    'bg-saturn-500 shadow-saturn-500/50'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-saturn-900 group-hover:text-saturn-700 transition-colors">
                      {activity.title}
                    </p>
                    <p className="text-xs text-saturn-500 mt-1 flex items-center gap-1.5">
                      <ClockIcon className="w-3 h-3" />
                      {activity.time}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Insights - Premium 2040 */}
        <div className="relative p-6 glass-neo border border-mars-300/50 rounded-2xl shadow-xl shadow-mars-500/15 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-sun-50/40 via-pearl-50/50 to-mars-50/40 opacity-70" />
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold flex items-center gap-2.5">
                <SparklesIcon className="w-6 h-6 text-sun-500" />
                <span className="bg-gradient-to-r from-saturn-700 via-sun-600 to-mars-600 bg-clip-text text-transparent">
                  AI Insights
                </span>
                <span className="w-2 h-2 bg-sun-500 rounded-full shadow-md shadow-sun-500/50"></span>
              </h2>
              <span className="text-xs bg-sun-100/80 text-sun-700 px-2.5 py-1 rounded-full font-bold">LIVE</span>
            </div>
            
            <div className="space-y-4">
              {aiInsights.map((insight, index) => (
                <div
                   key={index}
                  className="p-4 glass-card hover:glass-neo rounded-xl border border-pearl-200 hover:border-sun-300/60 hover:shadow-md hover:shadow-sun-500/8 transition-all duration-150 group"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl group-hover:scale-110 transition-transform duration-150">{insight.icon}</span>
                    <div className="flex-1">
                      <p className="text-sm font-bold text-saturn-900 mb-1">{insight.title}</p>
                      <p className="text-sm text-saturn-700">{insight.message}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-saturn-200/40">
              <button className="w-full py-3 bg-gradient-to-r from-saturn-600 to-sun-600 hover:from-saturn-700 hover:to-sun-700 text-white font-semibold rounded-xl shadow-md shadow-saturn-500/25 hover:shadow-lg hover:shadow-saturn-500/35 transition-all duration-150 active:scale-[0.98]">
                View Detailed Analytics
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions - Premium 2040 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          className="p-6 glass-neo border border-saturn-200/50 rounded-xl hover:shadow-md hover:shadow-saturn-500/15 hover:-translate-y-0.5 transition-all duration-150 group text-left cursor-pointer select-none active:scale-[0.98]"
        >
          <ChartBarIcon className="w-8 h-8 text-saturn-600 group-hover:text-saturn-700 mb-3 group-hover:scale-105 transition-all duration-150" />
          <h3 className="text-lg font-bold text-saturn-900 mb-1">New Trade</h3>
          <p className="text-sm text-saturn-600">Initiate commodity trade</p>
        </button>
        
        <button
          className="p-6 glass-neo border border-sun-200/50 rounded-xl hover:shadow-md hover:shadow-sun-500/15 hover:-translate-y-0.5 transition-all duration-150 group text-left cursor-pointer select-none active:scale-[0.98]"
        >
          <UsersIcon className="w-8 h-8 text-sun-600 group-hover:text-sun-700 mb-3 group-hover:scale-105 transition-all duration-150" />
          <h3 className="text-lg font-bold text-saturn-900 mb-1">Add Partner</h3>
          <p className="text-sm text-saturn-600">Onboard new partner</p>
        </button>
        
        <button
          className="p-6 glass-neo border border-mars-200/50 rounded-xl hover:shadow-md hover:shadow-mars-500/15 hover:-translate-y-0.5 transition-all duration-150 group text-left cursor-pointer select-none active:scale-[0.98]"
        >
          <ArrowTrendingUpIcon className="w-8 h-8 text-mars-600 group-hover:text-mars-700 mb-3 group-hover:scale-105 transition-all duration-150" />
          <h3 className="text-lg font-bold text-saturn-900 mb-1">View Reports</h3>
          <p className="text-sm text-saturn-600">Analytics & insights</p>
        </button>
      </div>

      {/* System Intelligence Advisory - Bottom-Right Fixed Panel */}
      <div className="hidden xl:block fixed bottom-10 right-6 z-35">
        {/* Collapsed State - Tab */}
        {!advisoryPanelOpen && (
          <button
            onClick={() => setAdvisoryPanelOpen(true)}
            className="flex items-center gap-3 px-5 py-3.5 bg-gradient-to-r from-saturn-700 to-saturn-600 text-white rounded-xl shadow-lg shadow-saturn-500/35 hover:shadow-xl hover:shadow-saturn-500/50 transition-all duration-150 group cursor-pointer select-none active:scale-[0.98]"
            aria-label="Open System Intelligence Advisory"
            aria-expanded={false}
          >
            <SparklesIcon className="w-5 h-5 text-sun-300" />
            <div className="text-left">
              <div className="text-sm font-bold">System Intelligence Advisory</div>
              <div className="text-xs text-saturn-200 font-medium">{intelligenceAdvisories.length} Predictive Insights</div>
            </div>
            <ChevronRightIcon className="w-4 h-4 text-saturn-300 group-hover:translate-x-1 transition-transform duration-300" />
          </button>
        )}

        {/* Expanded State - Full Panel */}
        {advisoryPanelOpen && (
          <div 
            className="w-[380px] glass-neo border border-saturn-300/50 rounded-2xl shadow-2xl shadow-saturn-500/30 overflow-hidden animate-fadeIn"
            role="dialog"
            aria-label="System Intelligence Advisory Panel"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-saturn-700 to-saturn-600 px-5 py-4 border-b border-saturn-500/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/15 rounded-lg">
                    <SparklesIcon className="w-5 h-5 text-sun-300" />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-base">System Intelligence Advisory</h3>
                    <p className="text-saturn-200 text-xs font-medium">Predictive • Silent • Stable</p>
                  </div>
                </div>
                <button
                  onClick={() => setAdvisoryPanelOpen(false)}
                  onKeyDown={(e) => e.key === 'Escape' && setAdvisoryPanelOpen(false)}
                  className="p-2 hover:bg-mars-500/30 rounded-lg transition-all duration-120 cursor-pointer select-none group"
                  title="Close Advisory Panel"
                  aria-label="Close Advisory Panel"
                >
                  <svg className="w-5 h-5 text-white group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Advisory Content */}
            <div className="max-h-[380px] overflow-y-auto p-4 space-y-3">
              {intelligenceAdvisories.map((advisory, index) => {
                const Icon = advisory.icon;
                return (
                  <div
                    key={index}
                    className={`p-4 glass-card border rounded-xl transition-all duration-150 hover:shadow-md cursor-default select-none ${
                      advisory.priority === 'high' 
                        ? 'border-mars-300/50 hover:border-mars-400/60 hover:shadow-mars-500/10' 
                        : 'border-saturn-200/50 hover:border-saturn-300/60 hover:shadow-saturn-500/10'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${
                        advisory.priority === 'high' 
                          ? 'bg-mars-100/80' 
                          : 'bg-saturn-100/80'
                      }`}>
                        <Icon className={`w-5 h-5 ${
                          advisory.priority === 'high' 
                            ? 'text-mars-600' 
                            : 'text-saturn-600'
                        }`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-xs font-bold text-saturn-900 uppercase tracking-wide">{advisory.type}</p>
                          <div className="flex items-center gap-1.5">
                            <div className="h-1.5 w-16 bg-pearl-200 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full"
                                style={{ width: `${advisory.confidence}%` }}
                              />
                            </div>
                            <span className="text-xs font-bold text-emerald-600">{advisory.confidence}%</span>
                          </div>
                        </div>
                        <p className="text-sm text-saturn-700 leading-relaxed">{advisory.message}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-saturn-200/40 bg-gradient-to-r from-pearl-50 to-saturn-50/30">
              <div className="flex items-center justify-between text-xs">
                <span className="text-saturn-600 font-medium">Last updated: Just now</span>
                <span className="text-saturn-500">Auto-refresh: 5m</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
