import React from 'react';
import { HoloPanel } from '../../components/2040/HoloPanel';
import { AIInsightBar } from '../../components/2040/AIInsightBar';
import { motion } from 'framer-motion';

export default function AuditScene() {
  const events = [
    { id: '1', type: 'trade', action: 'Trade executed', user: 'system', time: '2 min ago' },
    { id: '2', type: 'user', action: 'User login', user: 'admin@rnrl.com', time: '5 min ago' },
    { id: '3', type: 'document', action: 'Document uploaded', user: 'trade@rnrl.com', time: '12 min ago' },
  ];

  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
          Audit Timeline Stream
        </h1>
        <p className="text-sm text-pearl-300">
          Real-time audit trail, compliance monitoring, and event timeline
        </p>
      </HoloPanel>

      <HoloPanel theme="pearl" className="p-6">
        <h2 className="text-xl font-heading text-pearl-50 mb-4">Recent Events</h2>
        
        <div className="space-y-3">
          {events.map((event, index) => (
            <motion.div
              key={event.id}
              className="hologlass-pearl rounded-lg p-4 flex items-center gap-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="w-2 h-2 bg-saturn-400 rounded-full" />
              <div className="flex-1">
                <div className="text-sm text-pearl-100">{event.action}</div>
                <div className="text-xs text-pearl-400 mt-1">{event.user}</div>
              </div>
              <div className="text-xs text-pearl-400">{event.time}</div>
            </motion.div>
          ))}
        </div>
      </HoloPanel>

      <AIInsightBar module="audit" context={{ events }} />
    </div>
  );
}
