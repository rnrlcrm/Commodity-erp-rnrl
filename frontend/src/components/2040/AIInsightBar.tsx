import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAIOrchestrator } from '../../hooks/useAIOrchestrator';
import type { AISuggestion } from '../../types/2040.types';

interface AIInsightBarProps {
  module: string;
  context: Record<string, any>;
}

export const AIInsightBar: React.FC<AIInsightBarProps> = ({ module, context }) => {
  const { aiState, isProcessing, acceptSuggestion, rejectSuggestion } = useAIOrchestrator({
    module,
    context,
    enableSuggestions: true,
    enableInsights: true,
  });

  const [expandedSuggestion, setExpandedSuggestion] = useState<string | null>(null);

  if (aiState.suggestions.length === 0 && !isProcessing) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 left-6 md:left-auto md:w-96 z-ai-insight">
      <AnimatePresence mode="popLayout">
        {/* Processing indicator */}
        {isProcessing && (
          <motion.div
            className="ai-insight-bar mb-2 flex items-center gap-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            <div className="w-8 h-8 relative">
              <motion.div
                className="absolute inset-0 border-2 border-saturn-400 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
              />
              <motion.div
                className="absolute inset-2 bg-saturn-400/20 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium text-saturn-300">AI Processing</div>
              <div className="text-xs text-pearl-400">Analyzing context...</div>
            </div>
          </motion.div>
        )}

        {/* Suggestions */}
        {aiState.suggestions.map((suggestion) => (
          <motion.div
            key={suggestion.id}
            className="ai-insight-bar mb-2"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
            layout
          >
            <AIInsightCard
              suggestion={suggestion}
              isExpanded={expandedSuggestion === suggestion.id}
              onToggleExpand={() =>
                setExpandedSuggestion(
                  expandedSuggestion === suggestion.id ? null : suggestion.id
                )
              }
              onAccept={() => acceptSuggestion(suggestion.id)}
              onReject={() => rejectSuggestion(suggestion.id)}
            />
          </motion.div>
        ))}

        {/* Insights */}
        {aiState.insights.slice(0, 2).map((insight) => (
          <motion.div
            key={insight.id}
            className="hologlass-saturn rounded-holo-sm p-3 mb-2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-saturn-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-xs">💡</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-saturn-300 mb-1">
                  {insight.title}
                </div>
                <div className="text-xs text-pearl-300 line-clamp-2">
                  {insight.description}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

const AIInsightCard: React.FC<{
  suggestion: AISuggestion;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onAccept: () => void;
  onReject: () => void;
}> = ({ suggestion, isExpanded, onToggleExpand, onAccept, onReject }) => {
  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-saturn-500/20 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">🤖</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-saturn-200 mb-1">
            AI Suggestion
          </div>
          <div className="text-xs text-pearl-300">{suggestion.action}</div>
        </div>
        <button
          onClick={onToggleExpand}
          className="text-xs text-pearl-400 hover:text-pearl-200 transition-colors"
        >
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {/* Expanded details */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="pt-2 space-y-2 text-xs">
              <div>
                <span className="text-pearl-400">Reason:</span>
                <span className="text-pearl-200 ml-2">{suggestion.reason}</span>
              </div>
              <div>
                <span className="text-pearl-400">Impact:</span>
                <span className="text-pearl-200 ml-2">{suggestion.impact}</span>
              </div>
              <div>
                <span className="text-pearl-400">Confidence:</span>
                <span className="text-saturn-300 ml-2">
                  {(suggestion.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <motion.button
          onClick={onAccept}
          className="flex-1 px-3 py-2 bg-saturn-500/20 hover:bg-saturn-500/30 text-saturn-300 text-xs rounded-lg transition-colors border border-saturn-500/40"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Accept
        </motion.button>
        <motion.button
          onClick={onReject}
          className="flex-1 px-3 py-2 bg-pearl-500/10 hover:bg-pearl-500/20 text-pearl-300 text-xs rounded-lg transition-colors border border-pearl-500/20"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Dismiss
        </motion.button>
      </div>
    </div>
  );
};
