import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { LiquidButton } from './LiquidButton';

export interface FloatingActionBarAction {
  id: string;
  label: string;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  icon?: LucideIcon;
  disabled?: boolean;
}

export interface FloatingActionBarProps {
  actions: FloatingActionBarAction[];
  className?: string;
}

export function FloatingActionBar({ actions, className }: Readonly<FloatingActionBarProps>) {
  return (
    <motion.div
      className={clsx('pointer-events-none relative mt-12 flex w-full justify-center', className)}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <motion.div
        className="pointer-events-auto flex items-center gap-4 rounded-4xl border border-pearl-300/10 bg-white/5 px-6 py-4 shadow-[0_28px_80px_rgba(5,10,20,0.55)] backdrop-blur-glass"
        whileHover={{ y: -4 }}
      >
        {actions.map(({ id, label, variant = 'primary', icon, onClick, disabled }) => (
          <LiquidButton key={id} variant={variant} icon={icon} onClick={onClick} disabled={disabled}>
            {label}
          </LiquidButton>
        ))}
      </motion.div>
    </motion.div>
  );
}
