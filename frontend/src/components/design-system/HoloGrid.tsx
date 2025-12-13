import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

export interface HoloGridProps {
  columns?: 1 | 2 | 3;
  gap?: 'tight' | 'loose';
  children: ReactNode;
  className?: string;
}

const COLUMN_MAP: Record<NonNullable<HoloGridProps['columns']>, string> = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 lg:grid-cols-2',
  3: 'grid-cols-1 lg:grid-cols-3'
};

const GAP_MAP: Record<NonNullable<HoloGridProps['gap']>, string> = {
  tight: 'gap-8',
  loose: 'gap-12'
};

export function HoloGrid({
  columns = 2,
  gap = 'loose',
  children,
  className
}: Readonly<HoloGridProps>) {
  return (
    <motion.div
      className={clsx('grid w-full items-start', COLUMN_MAP[columns], GAP_MAP[gap], className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}
