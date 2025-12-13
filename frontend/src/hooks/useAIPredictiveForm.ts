import { useCallback, useEffect, useMemo, useState } from 'react';

interface PredictiveFieldSuggestion {
  field: string;
  value: any;
  confidence: number; // 0..1
  reason?: string;
}

interface PredictiveFormConfig<T> {
  initialValues: T;
  schema?: Record<string, any>;
  onAccept?: (values: T) => void;
  onReject?: (values: T) => void;
}

export function useAIPredictiveForm<T extends Record<string, any>>(config: PredictiveFormConfig<T>) {
  const [values, setValues] = useState<T>(config.initialValues);
  const [suggestions, setSuggestions] = useState<PredictiveFieldSuggestion[]>([]);
  const [isPredicting, setIsPredicting] = useState(false);

  // Simulate AI predictions for form fields based on schema/values
  const runPrediction = useCallback(async (payload?: Partial<T>) => {
    setIsPredicting(true);
    // Fake network/AI latency
    await new Promise((r) => setTimeout(r, 500));

    const next: PredictiveFieldSuggestion[] = Object.keys(values).map((field) => ({
      field,
      value: payload?.[field] ?? values[field],
      confidence: Math.random() * 0.5 + 0.5, // 0.5..1.0
      reason: `Predicted from context for ${field}`,
    }));
    setSuggestions(next);
    setIsPredicting(false);
  }, [values]);

  const acceptSuggestion = useCallback((field: string) => {
    const s = suggestions.find((x) => x.field === field);
    if (!s) return;
    setValues((prev) => ({ ...prev, [field]: s.value }));
    setSuggestions((prev) => prev.filter((x) => x.field !== field));
  }, [suggestions]);

  const rejectSuggestion = useCallback((field: string) => {
    setSuggestions((prev) => prev.filter((x) => x.field !== field));
  }, []);

  const acceptAll = useCallback(() => {
    setValues((prev) => {
      const merged: Record<string, any> = { ...prev };
      for (const s of suggestions) merged[s.field] = s.value;
      return merged as T;
    });
    setSuggestions([]);
    config.onAccept?.(values);
  }, [suggestions, config.onAccept, values]);

  const rejectAll = useCallback(() => {
    setSuggestions([]);
    config.onReject?.(values);
  }, [config.onReject, values]);

  const confidenceAvg = useMemo(() => {
    if (suggestions.length === 0) return 0;
    return suggestions.reduce((acc, s) => acc + s.confidence, 0) / suggestions.length;
  }, [suggestions]);

  // Auto-run initial prediction once
  useEffect(() => {
    runPrediction();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    values,
    setValues,
    suggestions,
    isPredicting,
    confidenceAvg,
    runPrediction,
    acceptSuggestion,
    rejectSuggestion,
    acceptAll,
    rejectAll,
  };
}

export type { PredictiveFieldSuggestion, PredictiveFormConfig };