/**
 * Risk Monitoring Module
 * Style: Quantum heat-mapping + AI decision glow
 * Purpose: High-attention area for real-time risk assessment
 */

import { useState, useRef, useEffect } from 'react';
import { 
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

interface RiskMetric {
  id: string;
  name: string;
  value: number;
  threshold: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  trend: 'up' | 'down' | 'stable';
}

export function RiskMonitoringPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [riskMetrics] = useState<RiskMetric[]>([
    { id: '1', name: 'Market Volatility', value: 72, threshold: 80, severity: 'medium', trend: 'up' },
    { id: '2', name: 'Credit Exposure', value: 45, threshold: 70, severity: 'low', trend: 'stable' },
    { id: '3', name: 'Settlement Risk', value: 88, threshold: 75, severity: 'critical', trend: 'up' },
    { id: '4', name: 'Counterparty Risk', value: 63, threshold: 80, severity: 'medium', trend: 'down' },
  ]);

  // Quantum heat map visualization
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrame: number;
    let time = 0;

    const drawHeatMap = () => {
      const width = canvas.width;
      const height = canvas.height;
      
      // Dark background
      ctx.fillStyle = '#0A0A1E';
      ctx.fillRect(0, 0, width, height);
      
      // Draw heat zones based on risk metrics
      riskMetrics.forEach((metric, index) => {
        const x = (index % 2) * (width / 2) + width / 4;
        const y = Math.floor(index / 2) * (height / 2) + height / 4;
        const intensity = metric.value / 100;
        const pulse = Math.sin(time + index) * 0.2 + 0.8;
        
        // Heat glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 80 * intensity * pulse);
        
        if (metric.severity === 'critical') {
          gradient.addColorStop(0, `rgba(220, 38, 38, ${intensity * 0.8})`);
          gradient.addColorStop(0.5, `rgba(220, 38, 38, ${intensity * 0.3})`);
          gradient.addColorStop(1, 'rgba(220, 38, 38, 0)');
        } else if (metric.severity === 'high') {
          gradient.addColorStop(0, `rgba(251, 146, 60, ${intensity * 0.7})`);
          gradient.addColorStop(0.5, `rgba(251, 146, 60, ${intensity * 0.2})`);
          gradient.addColorStop(1, 'rgba(251, 146, 60, 0)');
        } else if (metric.severity === 'medium') {
          gradient.addColorStop(0, `rgba(251, 191, 36, ${intensity * 0.6})`);
          gradient.addColorStop(0.5, `rgba(251, 191, 36, ${intensity * 0.2})`);
          gradient.addColorStop(1, 'rgba(251, 191, 36, 0)');
        } else {
          gradient.addColorStop(0, `rgba(34, 197, 94, ${intensity * 0.5})`);
          gradient.addColorStop(0.5, `rgba(34, 197, 94, ${intensity * 0.1})`);
          gradient.addColorStop(1, 'rgba(34, 197, 94, 0)');
        }
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, 100 * intensity * pulse, 0, Math.PI * 2);
        ctx.fill();
        
        // AI decision glow ring
        if (metric.severity === 'critical' || metric.severity === 'high') {
          ctx.beginPath();
          ctx.arc(x, y, 70 * intensity * pulse, 0, Math.PI * 2);
          ctx.strokeStyle = metric.severity === 'critical' ? '#DC2626' : '#FB923C';
          ctx.lineWidth = 3;
          ctx.shadowBlur = 20;
          ctx.shadowColor = metric.severity === 'critical' ? '#DC2626' : '#FB923C';
          ctx.stroke();
          ctx.shadowBlur = 0;
        }
      });
      
      time += 0.03;
      animationFrame = requestAnimationFrame(drawHeatMap);
    };

    drawHeatMap();

    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [riskMetrics]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'border-mars-500 bg-mars-950/50';
      case 'high':
        return 'border-sun-500 bg-sun-950/30';
      case 'medium':
        return 'border-sun-400 bg-sun-950/20';
      default:
        return 'border-emerald-500 bg-emerald-950/20';
    }
  };

  const getSeverityGlow = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'shadow-xl shadow-mars-500/50';
      case 'high':
        return 'shadow-lg shadow-sun-500/40';
      case 'medium':
        return 'shadow-md shadow-sun-400/30';
      default:
        return 'shadow-sm shadow-emerald-500/20';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header with AI Glow */}
      <div className="relative">
        <div className="absolute -inset-2 bg-gradient-to-r from-mars-500/20 via-sun-500/20 to-saturn-500/20 rounded-2xl blur-xl" />
        <div className="relative bg-gradient-to-r from-space-900 via-space-800 to-space-900 rounded-xl p-6 border border-saturn-700/50">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-heading font-bold text-white flex items-center gap-3">
                Risk Monitoring
                <span className="relative">
                  <BoltIcon className="w-8 h-8 text-sun-400" />
                  <div className="absolute inset-0 animate-pulse-ring">
                    <BoltIcon className="w-8 h-8 text-sun-400 opacity-50" />
                  </div>
                </span>
              </h1>
              <p className="text-saturn-300 mt-1">Real-time quantum risk assessment</p>
            </div>
            <div className="flex items-center gap-2 bg-emerald-500/20 text-emerald-400 px-4 py-2 rounded-lg border border-emerald-500/30">
              <ShieldCheckIcon className="w-5 h-5" />
              <span className="font-heading font-bold">System Protected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quantum Heat Map */}
      <div className="bg-gradient-to-b from-space-900 to-space-800 rounded-xl border border-saturn-700/50 overflow-hidden">
        <div className="p-4 border-b border-saturn-700/50">
          <h2 className="text-lg font-heading font-bold text-white">Quantum Risk Heat Map</h2>
          <p className="text-xs text-saturn-400 mt-1 font-mono">Live neural field visualization</p>
        </div>
        
        <div className="relative p-6">
          <canvas
            ref={canvasRef}
            width={900}
            height={400}
            className="w-full h-auto rounded-lg"
          />
          
          {/* Heat map legend */}
          <div className="absolute top-8 right-8 bg-space-900/90 backdrop-blur-sm border border-saturn-700/50 rounded-lg p-3 space-y-2">
            <p className="text-xs text-saturn-400 font-bold mb-2">SEVERITY</p>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-xs text-white font-mono">Low</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-sun-400" />
              <span className="text-xs text-white font-mono">Medium</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-sun-500" />
              <span className="text-xs text-white font-mono">High</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-mars-500 animate-neural-pulse" />
              <span className="text-xs text-white font-mono">Critical</span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Metrics Grid - AI Glow Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {riskMetrics.map((metric) => (
          <div
            key={metric.id}
            className={`relative p-5 rounded-xl border-2 ${getSeverityColor(
              metric.severity
            )} ${getSeverityGlow(metric.severity)} transition-all duration-120 hover-soft-bloom`}
          >
            {/* Neural pulse for critical items */}
            {metric.severity === 'critical' && (
              <div className="absolute -top-2 -right-2">
                <div className="w-4 h-4 bg-mars-500 rounded-full animate-neural-pulse" />
                <div className="absolute inset-0 w-4 h-4 bg-mars-400 rounded-full animate-pulse-ring" />
              </div>
            )}
            
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-heading font-bold text-white">{metric.name}</h3>
              <span
                className={`px-2 py-1 text-xs font-bold rounded-full ${
                  metric.severity === 'critical'
                    ? 'bg-mars-500 text-white'
                    : metric.severity === 'high'
                    ? 'bg-sun-500 text-white'
                    : metric.severity === 'medium'
                    ? 'bg-sun-400 text-space-900'
                    : 'bg-emerald-500 text-white'
                }`}
              >
                {metric.severity.toUpperCase()}
              </span>
            </div>

            {/* Value with quantum glow */}
            <div className="mb-4">
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-heading font-bold text-white font-mono">
                  {metric.value}
                </span>
                <span className="text-lg text-saturn-400 font-mono">/ {metric.threshold}</span>
              </div>
              <div className="mt-2 h-2 bg-space-800 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    metric.severity === 'critical'
                      ? 'bg-gradient-to-r from-mars-500 to-mars-600'
                      : metric.severity === 'high'
                      ? 'bg-gradient-to-r from-sun-500 to-sun-600'
                      : metric.severity === 'medium'
                      ? 'bg-gradient-to-r from-sun-400 to-sun-500'
                      : 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                  }`}
                  style={{ width: `${(metric.value / metric.threshold) * 100}%` }}
                />
              </div>
            </div>

            {/* Trend indicator */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-saturn-400 font-mono">TREND:</span>
              <div className="flex items-center gap-1">
                {metric.trend === 'up' ? (
                  <svg className="w-4 h-4 text-mars-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" />
                  </svg>
                ) : metric.trend === 'down' ? (
                  <svg className="w-4 h-4 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-saturn-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                )}
                <span className="text-xs text-white font-mono uppercase">{metric.trend}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Recommendations */}
      <div className="bg-gradient-to-br from-saturn-950/50 to-space-900 border border-saturn-700/50 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <ChartBarIcon className="w-6 h-6 text-sun-400" />
          <h2 className="text-lg font-heading font-bold text-white">AI Risk Recommendations</h2>
          <div className="animate-wave-ripple">
            <div className="w-2 h-2 bg-sun-400 rounded-full" />
          </div>
        </div>
        
        <div className="space-y-3">
          <div className="p-4 bg-space-900/50 border border-sun-500/30 rounded-lg hover-soft-bloom">
            <p className="text-white font-medium mb-1">⚠️ High Settlement Risk Detected</p>
            <p className="text-sm text-saturn-300">Recommend delaying 3 pending settlements until volatility decreases below 70%</p>
          </div>
          <div className="p-4 bg-space-900/50 border border-emerald-500/30 rounded-lg hover-soft-bloom">
            <p className="text-white font-medium mb-1">✅ Credit Exposure within Safe Limits</p>
            <p className="text-sm text-saturn-300">Current exposure is 45% of threshold. Safe to approve new trade requests.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
