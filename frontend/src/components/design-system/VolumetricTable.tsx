import clsx from 'clsx';
import { motion } from 'framer-motion';
import { PulsingStatusNode } from './PulsingStatusNode';

export interface VolumetricRow {
  id: string;
  asset: string;
  region: string;
  exposure: string;
  delta: string;
  status: 'active' | 'warning' | 'critical' | 'offline' | 'processing';
  supervisor: string;
}

export interface VolumetricTableProps {
  rows: VolumetricRow[];
  className?: string;
}

export function VolumetricTable({ rows, className }: Readonly<VolumetricTableProps>) {
  return (
    <motion.div
      className={clsx('flex flex-col gap-4', className)}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <div className="flex items-center justify-between rounded-3xl border border-pearl-300/10 bg-white/5 px-6 py-4 text-[0.65rem] uppercase tracking-[0.26em] text-pearl-300/70">
        <span className="w-36">Asset</span>
        <span className="w-24">Region</span>
        <span className="w-24 text-right">Exposure</span>
        <span className="w-24 text-right">Δ Drift</span>
        <span className="w-28 text-right">Supervisor</span>
      </div>
      {rows.map((row, index) => (
        <motion.div
          key={row.id}
          className="relative flex items-center justify-between gap-4 rounded-3xl border border-pearl-300/10 bg-space-900/40 px-6 py-4 shadow-[0_18px_48px_rgba(5,10,20,0.45)] backdrop-blur-glass holo-transform-gpu"
          style={{ transformStyle: 'preserve-3d' }}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: 'easeOut', delay: index * 0.04 }}
          whileHover={{ y: -6, scale: 1.01 }}
        >
          <div className="flex w-36 items-center gap-3 text-sm tracking-[0.16em] text-pearl-100/90">
            <PulsingStatusNode status={row.status} size="md" />
            <span>{row.asset}</span>
          </div>
          <div className="w-24 text-xs tracking-[0.18em] text-pearl-200/70">{row.region}</div>
          <div className="w-24 text-right text-xs tracking-[0.2em] text-pearl-100/80">{row.exposure}</div>
          <div
            className={clsx(
              'w-24 text-right text-xs tracking-[0.2em]',
              row.delta.startsWith('-') ? 'text-mars-300' : 'text-sun-300'
            )}
          >
            {row.delta}
          </div>
          <div className="w-28 text-right text-xs tracking-[0.2em] text-pearl-200/70">{row.supervisor}</div>
        </motion.div>
      ))}
    </motion.div>
  );
}
