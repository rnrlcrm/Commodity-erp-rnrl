import React, { useState } from 'react';
import { HoloPanel, HoloCard } from '../../components/2040/HoloPanel';
import { AIInsightBar } from '../../components/2040/AIInsightBar';
import { useRealtimeChannel } from '../../hooks/useRealtime';
import { motion, AnimatePresence } from 'framer-motion';

interface Document {
  id: string;
  name: string;
  type: string;
  status: 'processing' | 'completed' | 'failed';
  confidence: number;
  extractedData: Record<string, any>;
  timestamp: Date;
}

export const DocumentIntelligenceScene: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: '1',
      name: 'Invoice_2040_001.pdf',
      type: 'invoice',
      status: 'completed',
      confidence: 0.95,
      extractedData: { amount: 125000, currency: 'USD', vendor: 'Acme Corp' },
      timestamp: new Date(),
    },
    {
      id: '2',
      name: 'BillOfLading_2040_045.pdf',
      type: 'bill_of_lading',
      status: 'processing',
      confidence: 0,
      extractedData: {},
      timestamp: new Date(),
    },
  ]);

  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  // Realtime subscriptions
  useRealtimeChannel('documents.ocr', (data) => {
    console.log('OCR update:', data);
  });

  useRealtimeChannel('documents.classification', (data) => {
    console.log('Classification update:', data);
  });

  return (
    <div className="min-h-screen bg-space-500 p-6 space-y-6">
      {/* Header */}
      <HoloPanel theme="saturn" intensity="strong" className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading text-pearl-50 mb-2 text-glow-saturn">
              Document Intelligence System
            </h1>
            <p className="text-sm text-pearl-300">
              AI-powered OCR, classification, and data extraction
            </p>
          </div>
          <motion.button
            className="px-4 py-2 bg-sun-500/20 hover:bg-sun-500/30 text-sun-300 rounded-lg border border-sun-500/40 text-sm font-medium transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            + Upload Documents
          </motion.button>
        </div>
      </HoloPanel>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Processed Today', value: '248', icon: '📄' },
          { label: 'Avg Confidence', value: '94.2%', icon: '🎯' },
          { label: 'Processing Queue', value: '12', icon: '⏳' },
          { label: 'Failed Extractions', value: '3', icon: '❌' },
        ].map((stat) => (
          <HoloCard key={stat.label} theme="pearl">
            <div className="flex items-center gap-3">
              <div className="text-3xl">{stat.icon}</div>
              <div className="flex-1">
                <div className="text-xs text-pearl-400 mb-1">{stat.label}</div>
                <div className="text-2xl font-heading text-pearl-50">{stat.value}</div>
              </div>
            </div>
          </HoloCard>
        ))}
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document List */}
        <HoloPanel theme="pearl" className="p-6">
          <h2 className="text-xl font-heading text-pearl-50 mb-4">Recent Documents</h2>
          
          <div className="space-y-3">
            {documents.map((doc) => (
              <motion.div
                key={doc.id}
                className={`
                  hologlass-pearl rounded-holo p-4 cursor-pointer transition-all
                  ${selectedDoc?.id === doc.id ? 'ring-2 ring-saturn-400' : ''}
                `}
                whileHover={{ scale: 1.02, y: -2 }}
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-pearl-100 truncate">
                      {doc.name}
                    </div>
                    <div className="text-xs text-pearl-400 capitalize mt-1">
                      {doc.type.replace('_', ' ')}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {doc.status === 'completed' && (
                      <span className="text-green-400">✓</span>
                    )}
                    {doc.status === 'processing' && (
                      <motion.div
                        className="w-4 h-4 border-2 border-saturn-400 border-t-transparent rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                      />
                    )}
                    {doc.status === 'failed' && (
                      <span className="text-mars-400">✗</span>
                    )}
                  </div>
                </div>

                {doc.status === 'completed' && (
                  <div className="mt-3 pt-3 border-t border-pearl-700">
                    <div className="text-xs text-pearl-400 mb-1">Confidence</div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-pearl-800 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-saturn-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${doc.confidence * 100}%` }}
                          transition={{ delay: 0.3, duration: 0.8 }}
                        />
                      </div>
                      <span className="text-xs font-mono text-saturn-300">
                        {(doc.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </HoloPanel>

        {/* Document Viewer */}
        <HoloPanel theme="saturn" className="p-6">
          <h2 className="text-xl font-heading text-pearl-50 mb-4">
            {selectedDoc ? 'Extracted Data' : 'Document Preview'}
          </h2>

          <AnimatePresence mode="wait">
            {selectedDoc ? (
              <motion.div
                key={selectedDoc.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                {/* Document Hologram Visualization */}
                <div className="aspect-[3/4] hologlass rounded-holo flex items-center justify-center mb-4">
                  <div className="text-center">
                    <div className="text-6xl mb-4">📄</div>
                    <div className="text-sm text-pearl-300">{selectedDoc.name}</div>
                  </div>
                </div>

                {/* Extracted Fields */}
                {selectedDoc.status === 'completed' && (
                  <div className="space-y-3">
                    <div className="text-sm font-medium text-saturn-300 mb-2">
                      Extracted Fields
                    </div>
                    {Object.entries(selectedDoc.extractedData).map(([key, value]) => (
                      <div
                        key={key}
                        className="hologlass-pearl rounded-lg p-3 flex justify-between items-center"
                      >
                        <span className="text-xs text-pearl-400 capitalize">
                          {key.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-pearl-100 font-medium">
                          {String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex items-center justify-center text-pearl-400"
              >
                <div className="text-center">
                  <div className="text-4xl mb-4">📋</div>
                  <div className="text-sm">Select a document to view details</div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </HoloPanel>
      </div>

      {/* AI Insight Bar */}
      <AIInsightBar module="documents" context={{ documents, selectedDoc }} />
    </div>
  );
};
