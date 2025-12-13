import { motion } from "framer-motion";
import clsx from "clsx";
import { useState } from "react";
import { LucideIcon } from "lucide-react";

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
  type = "text"
}: NeonInputFieldProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <label className="block mb-2 uppercase tracking-[0.2em] text-saturn-200/70">
        {label}
      </label>
      
      <div className="relative">
        {Icon && (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-saturn-300/60">
            <Icon className="w-5 h-5" />
          </div>
        )}
        
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className={clsx(
            "w-full py-3 rounded-xl transition-all bg-space-800/40 backdrop-blur-glass text-pearl-100 placeholder-pearl-500 font-body",
            "border border-saturn-500/20 hover:border-saturn-500/30",
            Icon ? "pl-12 pr-4" : "px-4",
            isFocused && "border-saturn-400/60 shadow-[0_0_20px_rgba(59,130,246,0.3)]",
            "focus:outline-none focus:ring-0"
          )}
        />
        
        {aiSuggestion && isFocused && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-saturn-300/60 pointer-events-none"
          >
            <span className="text-sm">{aiSuggestion}</span>
          </motion.div>
        )}
      </div>
    </div>
  );
}
