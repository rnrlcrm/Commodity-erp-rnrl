import { useMemo, useState } from 'react';
import { useRealtime } from './useRealtime';

export function useVolumetricStream(channel: string) {
  const [samples, setSamples] = useState<any[]>([]);

  const { isConnected } = useRealtime({
    channels: [channel],
    onMessage: (ch, data) => {
      if (ch !== channel) return;
      const entry = { ...data, ts: Date.now() };
      setSamples((prev) => {
        const next = [...prev, entry];
        return next.slice(-200); // keep last 200 for perf
      });
    },
  });

  const stats = useMemo(() => {
    const count = samples.length;
    const last = samples[samples.length - 1];
    return { count, lastTs: last?.ts };
  }, [samples]);

  return { isConnected, samples, stats };
}