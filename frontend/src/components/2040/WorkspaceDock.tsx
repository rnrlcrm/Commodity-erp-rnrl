import { useMemo } from 'react';
import { Button } from './Button';

interface DockItem { key: string; label: string; icon?: React.ReactNode; }
interface Props { items: DockItem[]; active: string; onSelect: (key: string) => void; }

export function WorkspaceDock({ items, active, onSelect }: Readonly<Props>) {
  const rendered = useMemo(() => items, [items]);
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-3 rounded-2xl hologlass-pearl shadow-holo flex space-x-2 z-[90]">
      {rendered.map((item) => (
        <Button
          key={item.key}
          variant={active === item.key ? 'primary' : 'secondary'}
          className="min-w-[96px]"
          onClick={() => onSelect(item.key)}
        >
          <span className="flex items-center gap-2">
            {item.icon}
            {item.label}
          </span>
        </Button>
      ))}
    </div>
  );
}

export default WorkspaceDock;