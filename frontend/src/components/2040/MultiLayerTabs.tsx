import { ReactNode, useState } from 'react';

interface TabItem {
  key: string;
  label: ReactNode;
}

interface Props {
  tabs: TabItem[];
  onChange?: (key: string) => void;
  activeKey?: string;
}

export function MultiLayerTabs({ tabs, onChange, activeKey }: Readonly<Props>) {
  const [internalActive, setInternalActive] = useState(tabs[0]?.key);
  const controlled = typeof activeKey !== 'undefined';
  const resolvedActive = controlled ? activeKey : internalActive;

  const handleSelect = (key: string) => {
    if (!controlled) {
      setInternalActive(key);
    }
    onChange?.(key);
  };
  return (
    <div className="relative p-2 rounded-xl hologlass-pearl">
      <div className="flex space-x-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => handleSelect(t.key)}
            className={`px-4 py-2 rounded-lg border transition-all ${
              resolvedActive === t.key
                ? 'bg-saturn-500/15 border-saturn-500/40 text-pearl-100 shadow-holo'
                : 'bg-pearl-50/5 border-white/10 text-pearl-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="absolute inset-0 -z-10 bg-holo-gradient rounded-xl" />
    </div>
  );
}

export default MultiLayerTabs;