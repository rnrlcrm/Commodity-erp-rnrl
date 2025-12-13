import { motion } from 'framer-motion';
import clsx from 'clsx';
import type { ReactNode } from 'react';

interface HoloPanelProps {
  title?: string;
  accent?: 'sun' | 'saturn' | 'mars';
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
}

export function HoloPanel({ title, accent = 'saturn', children, footer, className }: Readonly<HoloPanelProps>) {
  return (
    <motion.section
      className={clsx(
        'relative isolate overflow-hidden rounded-4xl border backdrop-blur-glass',
        'bg-pearl-100/5 border-pearl-500/20 shadow-[0_0_48px_rgba(148,163,184,0.25)]',
        'px-10 py-8 flex flex-col gap-6',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{
        y: -6,
        boxShadow:
          accent === 'saturn'
            ? '0 0 60px rgba(96,165,250,0.35)'
            : accent === 'sun'
              ? '0 0 60px rgba(251,191,36,0.35)'
              : '0 0 60px rgba(239,68,68,0.35)'
      }}
      transition={{ type: 'spring', stiffness: 90, damping: 18 }}
    >
      <div className="pointer-events-none absolute inset-0 opacity-30" aria-hidden>
        <div
          className={clsx(
            'absolute inset-x-0 top-0 h-px',
            accent === 'saturn' && 'bg-gradient-to-r from-saturn-200/0 via-saturn-300/70 to-saturn-200/0',
            accent === 'sun' && 'bg-gradient-to-r from-sun-200/0 via-sun-300/70 to-sun-200/0',
            accent === 'mars' && 'bg-gradient-to-r from-mars-300/0 via-mars-400/70 to-mars-300/0'
          )}
        />
      </div>
      {title ? (
        <header className="flex items-center justify-between">
          <h2 className="tracking-[0.2em] text-saturn-100 drop-shadow-[0_0_14px_rgba(96,165,250,0.55)] uppercase">
            {title}
          </h2>
        </header>
      ) : null}
      <div className="flex-1 min-h-0">{children}</div>
      {footer ? (
        <footer className="pt-4 border-t border-pearl-500/10 text-pearl-100/80">
          {footer}
        </footer>
      ) : null}
    </motion.section>
  );
}
