import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

type InsightLevel = 'info' | 'warning' | 'critical';

export interface AIInsight {
  id: string;
  label: string;
  detail?: string;
  level?: InsightLevel;
  icon?: ReactNode;
}

const LEVEL_STYLES: Record<InsightLevel, string> = {
  info: 'from-saturn-300/20 via-saturn-300/10 to-saturn-300/0 border-saturn-300/20 text-saturn-100',
  warning: 'from-sun-300/20 via-sun-300/10 to-sun-300/0 border-sun-300/20 text-sun-200',
  critical: 'from-mars-400/25 via-mars-400/10 to-mars-400/0 border-mars-400/25 text-mars-300'
};

export interface AIInsightBarProps {
  insights: AIInsight[];
  className?: string;
}

export function AIInsightBar({ insights, className }: Readonly<AIInsightBarProps>) {
  return (
    <motion.div
      className={clsx('flex flex-col gap-3', className)}
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      {insights.map((insight) => {
        const level = insight.level ?? 'info';
        const levelClasses = LEVEL_STYLES[level];

        return (
          <motion.div
            key={insight.id}
            className={clsx(
              'group relative flex items-center gap-4 overflow-hidden rounded-3xl border px-5 py-4 backdrop-blur-glass',
              'bg-space-900/40 shadow-[0_12px_36px_rgba(5,10,20,0.35)]'
            )}
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
          >
            <span
              aria-hidden
              className={clsx('absolute inset-0 bg-gradient-to-br opacity-70', levelClasses)}
            />
            <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-black/20 text-sm">
              {insight.icon ?? 'AI'}
            </span>
            <div className="relative z-10 flex flex-1 flex-col gap-1 text-left">
              <span className="text-xs uppercase tracking-[0.26em] text-pearl-50">{insight.label}</span>
              {insight.detail ? (
                <span className="text-[0.65rem] tracking-[0.18em] text-pearl-200/70">{insight.detail}</span>
              ) : null}
            </div>
            <motion.span
              aria-hidden
              className="relative z-10 h-2 w-2 rounded-full bg-white/80"
              animate={{ scale: [1, 1.2, 1], opacity: [0.8, 1, 0.8] }}
              transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
            />
          </motion.div>
        );
      })}
    </motion.div>
  );
}
