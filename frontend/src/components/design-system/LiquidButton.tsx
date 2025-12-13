import { motion } from 'framer-motion';
import clsx from 'clsx';
import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

interface LiquidButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  icon?: LucideIcon;
  disabled?: boolean;
}

export function LiquidButton({
  children,
  onClick,
  variant = 'primary',
  icon: Icon,
  disabled = false
}: Readonly<LiquidButtonProps>) {
  function getVariantClasses() {
    switch (variant) {
      case 'primary':
        return 'bg-gradient-to-r from-sun-400 to-sun-500 hover:from-sun-300 hover:to-sun-400 shadow-[0_0_24px_rgba(251,191,36,0.5)] hover:shadow-[0_0_36px_rgba(251,191,36,0.7)]';
      case 'secondary':
        return 'bg-gradient-to-r from-saturn-400 to-saturn-500 hover:from-saturn-300 hover:to-saturn-400 shadow-[0_0_24px_rgba(59,130,246,0.5)] hover:shadow-[0_0_36px_rgba(59,130,246,0.7)]';
      case 'danger':
        return 'bg-gradient-to-r from-mars-400 to-mars-500 hover:from-mars-300 hover:to-mars-400 shadow-[0_0_24px_rgba(239,68,68,0.5)] hover:shadow-[0_0_36px_rgba(239,68,68,0.7)]';
      default:
        return '';
    }
  }

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'relative flex items-center justify-center gap-3 overflow-hidden rounded-2xl px-8 py-4 uppercase tracking-[0.1em] text-space-900',
        'disabled:cursor-not-allowed disabled:opacity-50',
        getVariantClasses()
      )}
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
    >
      <motion.div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
        animate={{ x: ['-200%', '200%'] }}
        transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
      />

      {Icon ? <Icon className="relative z-10 h-5 w-5" /> : null}
      <span className="relative z-10">{children}</span>
    </motion.button>
  );
}
