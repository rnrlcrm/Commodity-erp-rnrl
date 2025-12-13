import { motion } from 'framer-motion';
import clsx from 'clsx';
import { useState } from 'react';
import type { LucideIcon } from 'lucide-react';

interface NeonInputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  icon?: LucideIcon;
  aiSuggestion?: string;
  type?: string;
}

export function NeonInputField({
  label,
  value,
  onChange,
  placeholder,
  icon: Icon,
  aiSuggestion,
  type = 'text'
}: Readonly<NeonInputFieldProps>) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <label className="mb-2 block uppercase tracking-[0.2em] text-saturn-200/70">{label}</label>

      <div className="relative">
        {Icon ? (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-saturn-300/60">
            <Icon className="h-5 w-5" />
          </div>
        ) : null}

        <motion.input
          type={type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className={clsx(
            'w-full rounded-2xl border px-4 py-4 text-pearl-100 backdrop-blur-glass transition-all duration-300',
            'bg-pearl-100/5 border-pearl-500/20 placeholder:text-pearl-300/40',
            Icon && 'pl-12'
          )}
          animate={{
            borderColor: isFocused ? 'rgba(96,165,250,0.6)' : 'rgba(148,163,184,0.2)',
            boxShadow: isFocused ? '0 0 24px rgba(96,165,250,0.4)' : '0 0 12px rgba(148,163,184,0.2)'
          }}
        />

        {aiSuggestion && !value ? (
          <motion.div
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
          >
            <span className="flex items-center gap-2 italic text-sun-300/60">
              <span className="h-2 w-2 rounded-full bg-sun-400 animate-holo-pulse" />
              AI: {aiSuggestion}
            </span>
          </motion.div>
        ) : null}
      </div>
    </div>
  );
}
