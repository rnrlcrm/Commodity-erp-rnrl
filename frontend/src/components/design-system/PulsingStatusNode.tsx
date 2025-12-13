import clsx from 'clsx';
import { motion } from 'framer-motion';

interface PulsingStatusNodeProps {
  status: 'active' | 'warning' | 'critical' | 'offline' | 'processing';
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function PulsingStatusNode({ status, label, size = 'md' }: Readonly<PulsingStatusNodeProps>) {
  function getSizeClass() {
    switch (size) {
      case 'sm':
        return 'h-2 w-2';
      case 'lg':
        return 'h-4 w-4';
      default:
        return 'h-3 w-3';
    }
  }

  function getStatusClasses() {
    switch (status) {
      case 'active':
        return {
          bg: 'bg-buy-light',
          shadow: 'shadow-[0_0_18px_rgba(134,239,172,0.75)]',
          text: 'text-buy-light'
        } as const;
      case 'warning':
        return {
          bg: 'bg-sun-400',
          shadow: 'shadow-[0_0_18px_rgba(251,191,36,0.75)]',
          text: 'text-sun-400'
        } as const;
      case 'critical':
        return {
          bg: 'bg-mars-400',
          shadow: 'shadow-[0_0_18px_rgba(239,68,68,0.75)]',
          text: 'text-mars-400'
        } as const;
      case 'offline':
        return {
          bg: 'bg-pearl-500',
          shadow: 'shadow-[0_0_12px_rgba(148,163,184,0.5)]',
          text: 'text-pearl-500'
        } as const;
      case 'processing':
        return {
          bg: 'bg-saturn-400',
          shadow: 'shadow-[0_0_18px_rgba(59,130,246,0.75)]',
          text: 'text-saturn-400'
        } as const;
      default:
        return {
          bg: 'bg-pearl-500',
          shadow: 'shadow-[0_0_12px_rgba(148,163,184,0.5)]',
          text: 'text-pearl-500'
        } as const;
    }
  }

  const classes = getStatusClasses();

  return (
    <div className="flex items-center gap-2">
      <motion.div
        className={clsx('rounded-full', getSizeClass(), classes.bg, classes.shadow, status !== 'offline' && 'animate-holo-pulse')}
        animate=
          {status === 'processing'
            ? {
                scale: [1, 1.2, 1],
                opacity: [1, 0.8, 1]
              }
            : undefined}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
      {label ? <span className={clsx('uppercase tracking-[0.1em]', classes.text)}>{label}</span> : null}
    </div>
  );
}
