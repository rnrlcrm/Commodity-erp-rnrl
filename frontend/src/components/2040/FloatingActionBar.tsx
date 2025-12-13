import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import clsx from "clsx";

interface Action {
  id: string;
  label: string;
  icon: LucideIcon;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";
}

interface FloatingActionBarProps {
  actions: Action[];
}

export function FloatingActionBar({ actions }: FloatingActionBarProps) {
  if (actions.length === 0) return null;

  return (
    <motion.div
      className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50"
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
    >
      <div className="flex items-center gap-3 px-6 py-4 rounded-3xl border border-saturn-500/20 bg-space-700/80 backdrop-blur-glass shadow-[0_8px_32px_rgba(37,99,235,0.3)] animate-holo-pulse">
        {actions.map((action, idx) => {
          const Icon = action.icon;
          const variant = action.variant || "secondary";
          
          return (
            <motion.button
              key={action.id}
              onClick={action.onClick}
              className={clsx(
                "flex items-center gap-2 px-6 py-3 rounded-xl transition-all font-heading transform-gpu",
                variant === "primary" && "bg-sun-400/20 text-sun-300 hover:bg-sun-400/30 border border-sun-400/30 shadow-[0_0_20px_rgba(245,158,11,0.3)] hover:shadow-[0_0_25px_rgba(245,158,11,0.4)]",
                variant === "secondary" && "bg-saturn-400/20 text-saturn-300 hover:bg-saturn-400/30 border border-saturn-400/30 shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.4)]",
                variant === "danger" && "bg-mars-400/20 text-mars-300 hover:bg-mars-400/30 border border-mars-400/30 shadow-[0_0_20px_rgba(239,68,68,0.3)] hover:shadow-[0_0_25px_rgba(239,68,68,0.4)]"
              )}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: idx * 0.05, type: "spring", stiffness: 200, damping: 15 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium uppercase tracking-[0.1em]">{action.label}</span>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
