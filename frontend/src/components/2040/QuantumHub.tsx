/**
 * Quantum Hub - Right AI Assist Panel
 * Features: Quantum neon glow rings, fractal visualizations, AI predictions, anomaly detection
 */

import { useState, useEffect, useRef } from 'react';
import { 
  SparklesIcon, 
  ExclamationTriangleIcon,
  ChartBarIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface AnomalyAlert {
  id: string;
  type: 'fraud' | 'risk' | 'opportunity';
  message: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: Date;
}

interface AIPrediction {
  id: string;
  title: string;
  prediction: string;
  confidence: number;
  icon: string;
}

export function QuantumHub({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [anomalies] = useState<AnomalyAlert[]>([
    {
      id: '1',
      type: 'fraud',
      message: 'Unusual trading pattern detected in cotton futures',
      severity: 'high',
      timestamp: new Date(),
    },
    {
      id: '2',
      type: 'opportunity',
      message: 'Price arbitrage opportunity identified',
      severity: 'medium',
      timestamp: new Date(Date.now() - 300000),
    },
  ]);

  const [predictions] = useState<AIPrediction[]>([
    {
      id: '1',
      title: 'Market Trend',
      prediction: 'Cotton prices expected to rise 2.4% this week',
      confidence: 87,
      icon: '📈',
    },
    {
      id: '2',
      title: 'Risk Assessment',
      prediction: 'Low volatility period ahead - ideal for settlements',
      confidence: 92,
      icon: '🛡️',
    },
    {
      id: '3',
      title: 'Partner Insight',
      prediction: '3 high-value partners likely to increase volume',
      confidence: 78,
      icon: '🎯',
    },
  ]);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Quantum fractal visualization
  useEffect(() => {
    if (!canvasRef.current || !isOpen) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrame: number;
    let time = 0;

    const drawQuantumField = () => {
      const width = canvas.width;
      const height = canvas.height;
      
      // Clear with dark background
      ctx.fillStyle = 'rgba(10, 10, 30, 0.95)';
      ctx.fillRect(0, 0, width, height);
      
      // Draw quantum rings
      const centerX = width / 2;
      const centerY = height / 2;
      
      for (let i = 0; i < 5; i++) {
        const radius = 20 + i * 25 + Math.sin(time + i) * 5;
        const opacity = 0.3 - i * 0.04;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(139, 92, 246, ${opacity})`;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Neon glow effect
        ctx.shadowBlur = 15;
        ctx.shadowColor = 'rgba(139, 92, 246, 0.5)';
        ctx.stroke();
        ctx.shadowBlur = 0;
      }
      
      // Draw fractal particles
      for (let i = 0; i < 30; i++) {
        const angle = (i / 30) * Math.PI * 2 + time * 0.5;
        const distance = 60 + Math.sin(time * 2 + i) * 20;
        const x = centerX + Math.cos(angle) * distance;
        const y = centerY + Math.sin(angle) * distance;
        
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(251, 146, 60, ${0.6 - (i % 3) * 0.2})`;
        ctx.fill();
        
        // Particle glow
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(251, 146, 60, 0.8)';
        ctx.fill();
        ctx.shadowBlur = 0;
      }
      
      time += 0.02;
      animationFrame = requestAnimationFrame(drawQuantumField);
    };

    drawQuantumField();

    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [isOpen]); // Only re-run when isOpen changes

  if (!isOpen) return null;

  return (
    <div 
      className="fixed right-0 top-14 bottom-8 w-full md:w-96 xl:w-80 bg-gradient-to-b from-space-900 via-space-800 to-space-900 border-l border-saturn-700/30 shadow-2xl z-30 overflow-y-auto transition-transform duration-300 ease-in-out"
      role="complementary"
      aria-label="Quantum Hub Panel"
    >
      {/* Header */}
      <div className="sticky top-0 bg-space-900/95 backdrop-blur-xl border-b border-saturn-700/30 p-4 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <SparklesIcon className="w-6 h-6 text-sun-400" />
              <div className="absolute inset-0 animate-pulse-ring">
                <SparklesIcon className="w-6 h-6 text-sun-400 opacity-50" />
              </div>
            </div>
            <h2 className="font-heading text-lg font-bold text-white">Quantum Hub</h2>
            <span className="text-xs bg-sun-500/20 text-sun-400 px-2 py-0.5 rounded-full border border-sun-500/30 font-mono">
              LIVE
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-mars-500/20 rounded-lg transition-all duration-120 group"
            title="Close Quantum Hub"
            aria-label="Close Quantum Hub"
          >
            <XMarkIcon className="w-5 h-5 text-saturn-400 group-hover:text-white" />
          </button>
        </div>
      </div>

      {/* Quantum Visualization */}
      <div className="p-4">
        <div className="relative rounded-xl overflow-hidden border border-saturn-700/50 bg-space-900">
          <canvas
            ref={canvasRef}
            width={300}
            height={180}
            className="w-full h-auto"
          />
          <div className="absolute top-2 left-2 text-xs text-saturn-400 font-mono bg-space-900/80 px-2 py-1 rounded">
            Neural Field Active
          </div>
        </div>
      </div>

      {/* Anomaly Alerts */}
      <div className="px-4 pb-4">
        <div className="flex items-center gap-2 mb-3">
          <ExclamationTriangleIcon className="w-5 h-5 text-mars-400" />
          <h3 className="font-heading text-sm font-bold text-white">Anomaly Detection</h3>
          <span className="text-xs text-mars-400 font-mono">{anomalies.length}</span>
        </div>
        
        <div className="space-y-2">
          {anomalies.map((anomaly) => (
            <div
              key={anomaly.id}
              className={`relative p-3 rounded-xl border transition-all duration-120 hover:scale-[1.02] ${
                anomaly.severity === 'high'
                  ? 'bg-mars-950/50 border-mars-500/50 hover:border-mars-400'
                  : 'bg-sun-950/30 border-sun-500/30 hover:border-sun-400'
              }`}
            >
              {/* Neural pulse indicator for high severity */}
              {anomaly.severity === 'high' && (
                <div className="absolute -top-1 -right-1">
                  <div className="w-3 h-3 bg-mars-500 rounded-full animate-neural-pulse" />
                  <div className="absolute inset-0 w-3 h-3 bg-mars-400 rounded-full animate-pulse-ring" />
                </div>
              )}
              
              <div className="flex items-start gap-2">
                <div className={`mt-0.5 w-2 h-2 rounded-full ${
                  anomaly.severity === 'high' ? 'bg-mars-500' : 'bg-sun-500'
                }`} />
                <div className="flex-1">
                  <p className="text-sm text-white font-medium">{anomaly.message}</p>
                  <p className="text-xs text-saturn-400 mt-1 font-mono">
                    {anomaly.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Predictions */}
      <div className="px-4 pb-4">
        <div className="flex items-center gap-2 mb-3">
          <ChartBarIcon className="w-5 h-5 text-saturn-400" />
          <h3 className="font-heading text-sm font-bold text-white">AI Predictions</h3>
        </div>
        
        <div className="space-y-2">
          {predictions.map((pred) => (
            <div
              key={pred.id}
              className="p-3 rounded-xl bg-saturn-950/30 border border-saturn-700/40 hover:border-saturn-500/60 transition-all duration-120 hover-soft-bloom cursor-pointer group"
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl group-hover:scale-110 transition-transform duration-120">
                  {pred.icon}
                </span>
                <div className="flex-1">
                  <p className="text-xs text-saturn-400 font-medium mb-1">{pred.title}</p>
                  <p className="text-sm text-white font-medium">{pred.prediction}</p>
                  
                  {/* Confidence bar */}
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-space-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-saturn-500 to-sun-500 rounded-full transition-all duration-500"
                        style={{ width: `${pred.confidence}%` }}
                      />
                    </div>
                    <span className="text-xs text-sun-400 font-mono font-bold">
                      {pred.confidence}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="px-4 pb-6">
        <div className="p-3 rounded-xl bg-space-800/50 border border-saturn-700/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-saturn-400 font-medium">Neural Network</span>
            <span className="text-xs text-emerald-400 font-mono">Online</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-saturn-400 font-medium">Quantum Processing</span>
            <span className="text-xs text-emerald-400 font-mono">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
