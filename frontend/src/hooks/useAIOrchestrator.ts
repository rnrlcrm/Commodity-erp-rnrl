import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  AIContextState,
  AIPrediction,
  AISuggestion,
  AIAutomation,
  AIInsight,
} from '../types/2040.types';

// AI Worker for background processing
let aiWorker: Worker | null = null;

if (typeof globalThis !== 'undefined' && (globalThis as any).Worker) {
  aiWorker = new Worker(
    new URL('../workers/aiOrchestrator.worker.ts', import.meta.url),
    { type: 'module' }
  );
}

interface AIOrchestratorConfig {
  module: string;
  context: Record<string, any>;
  enablePredictions?: boolean;
  enableSuggestions?: boolean;
  enableAutomations?: boolean;
  enableInsights?: boolean;
}

export function useAIOrchestrator(config: AIOrchestratorConfig) {
  const [aiState, setAIState] = useState<AIContextState>({
    predictions: [],
    suggestions: [],
    automations: [],
    insights: [],
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const workerRef = useRef(aiWorker);

  // Initialize AI orchestrator for module
  useEffect(() => {
    if (!workerRef.current) return;

    const handleWorkerMessage = (e: MessageEvent) => {
      const { type, data } = e.data;

      switch (type) {
        case 'prediction':
          setAIState((prev) => ({
            ...prev,
            predictions: [...prev.predictions, data as AIPrediction],
          }));
          break;

        case 'suggestion':
          setAIState((prev) => ({
            ...prev,
            suggestions: [...prev.suggestions, data as AISuggestion],
          }));
          break;

        case 'automation': {
          setAIState((prev) => {
            const updated = [] as AIAutomation[];
            for (const auto of prev.automations) {
              updated.push(auto.id === (data as AIAutomation).id ? (data as AIAutomation) : auto);
            }
            return { ...prev, automations: updated };
          });
          break;
        }

        case 'insight':
          setAIState((prev) => ({
            ...prev,
            insights: [...prev.insights, data as AIInsight],
          }));
          break;

        case 'processing':
          setIsProcessing(data.processing);
          break;
      }
    };

    workerRef.current.addEventListener('message', handleWorkerMessage);

    // Initialize worker with config
    workerRef.current.postMessage({
      type: 'init',
      config,
    });

    return () => {
      workerRef.current?.removeEventListener('message', handleWorkerMessage);
    };
  }, [config.module, config.context]);

  // Accept suggestion
  const acceptSuggestion = useCallback((id: string) => {
    setAIState((prev) => ({
      ...prev,
      suggestions: prev.suggestions.filter((s) => s.id !== id),
    }));
    
    const suggestion = aiState.suggestions.find((s) => s.id === id);
    if (suggestion?.acceptAction) {
      suggestion.acceptAction();
    }
  }, [aiState.suggestions]);

  // Reject suggestion
  const rejectSuggestion = useCallback((id: string) => {
    setAIState((prev) => ({
      ...prev,
      suggestions: prev.suggestions.filter((s) => s.id !== id),
    }));
    
    const suggestion = aiState.suggestions.find((s) => s.id === id);
    if (suggestion?.rejectAction) {
      suggestion.rejectAction();
    }
  }, [aiState.suggestions]);

  // Trigger automation
  const triggerAutomation = useCallback((automation: Omit<AIAutomation, 'id' | 'status' | 'progress'>) => {
    const id = `auto-${Date.now()}`;
    const newAutomation: AIAutomation = {
      ...automation,
      id,
      status: 'pending',
      progress: 0,
    };

    setAIState((prev) => ({
      ...prev,
      automations: [...prev.automations, newAutomation],
    }));

    workerRef.current?.postMessage({
      type: 'run-automation',
      automation: newAutomation,
    });

    return id;
  }, []);

  // Request AI insight
  const requestInsight = useCallback((query: string) => {
    workerRef.current?.postMessage({
      type: 'request-insight',
      query,
      context: config.context,
    });
  }, [config.context]);

  // Clear old predictions/insights
  const clearOldData = useCallback((ageMinutes: number = 30) => {
    const cutoff = Date.now() - ageMinutes * 60 * 1000;
    setAIState((prev) => ({
      ...prev,
      predictions: prev.predictions.filter((p) => (p as any)?.timestamp > cutoff),
      insights: prev.insights.filter((i) => (i as any)?.timestamp > cutoff),
    }));
  }, []);

  return {
    aiState,
    isProcessing,
    acceptSuggestion,
    rejectSuggestion,
    triggerAutomation,
    requestInsight,
    clearOldData,
  };
}

// Hook for AI explanations
export function useAIExplain() {
  const [explanation, setExplanation] = useState<string | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);

  const explain = useCallback(async (target: string, context: any) => {
    setIsExplaining(true);
    
    // Simulate AI explanation generation
    // In production, this would call your AI service
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    setExplanation(
      `AI Analysis: ${target} shows patterns based on ${JSON.stringify(context).substring(0, 100)}...`
    );
    setIsExplaining(false);
  }, []);

  const clearExplanation = useCallback(() => {
    setExplanation(null);
  }, []);

  return { explanation, isExplaining, explain, clearExplanation };
}
