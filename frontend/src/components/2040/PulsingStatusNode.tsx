import { motion } from 'framer-motion';

interface Props {
  status: 'ok' | 'warn' | 'alert' | 'idle';
  label?: string;
}

const colorMap = {
  ok: 'bg-buy-light',
  warn: 'bg-sun-400',
  alert: 'bg-mars-500',
  idle: 'bg-pearl-500',
};

export function PulsingStatusNode({ status, label }: Readonly<Props>) {
  const base = colorMap[status];
  return (
    <div className="relative w-6 h-6">
      <motion.span
        className={`absolute inset-0 rounded-full ${base}`}
        initial={{ scale: 0.9, opacity: 0.9 }}
        animate={{ scale: [0.9, 1.15, 0.9], opacity: [0.9, 0.7, 0.9] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      />
      <span className="absolute inset-0 rounded-full ring-2 ring-white/30" />
      {label && (
        <span className="ml-8 text-xs text-pearl-100">{label}</span>
      )}
    </div>
  );
}

export default PulsingStatusNode;