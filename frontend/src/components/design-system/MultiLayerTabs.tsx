import clsx from 'clsx';
import { motion } from 'framer-motion';
import { useState } from 'react';
import type { ReactNode } from 'react';

interface Tab {
  id: string;
  label: string;
  content: ReactNode;
  badge?: number;
}

interface MultiLayerTabsProps {
  tabs: Tab[];
}

export function MultiLayerTabs({ tabs }: Readonly<MultiLayerTabsProps>) {
  const [activeTab, setActiveTab] = useState(tabs[0]?.id ?? '');

  return (
    <div className="space-y-6">
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {tabs.map((tab, index) => {
          const isActive = activeTab === tab.id;
          return (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'relative whitespace-nowrap rounded-2xl border px-6 py-4 transition-all backdrop-blur-glass',
                isActive
                  ? 'bg-saturn-400/20 border-saturn-300/40 text-saturn-100 shadow-[0_0_24px_rgba(96,165,250,0.3)]'
                  : 'bg-pearl-100/5 border-pearl-500/20 text-pearl-300 hover:border-saturn-300/30'
              )}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ y: -2 }}
              style={{
                transformStyle: 'preserve-3d',
                transform: isActive ? 'translateZ(20px)' : 'translateZ(0px)'
              }}
            >
              {isActive ? (
                <motion.div
                  className="absolute inset-0 rounded-2xl bg-gradient-to-r from-saturn-400/20 via-saturn-300/10 to-saturn-400/20"
                  layoutId="activeTab"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              ) : null}
              <div className="relative z-10 flex items-center gap-2">
                <span className="uppercase tracking-[0.15em]">{tab.label}</span>
                {tab.badge !== undefined ? (
                  <span className="rounded-full bg-sun-400/30 px-2 py-0.5 font-mono text-sun-300">{tab.badge}</span>
                ) : null}
              </div>
            </motion.button>
          );
        })}
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </motion.div>
    </div>
  );
}
