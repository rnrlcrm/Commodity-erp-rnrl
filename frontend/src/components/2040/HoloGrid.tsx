import React from 'react';

interface HoloGridProps {
  columns?: number;
  gap?: string;
  children: React.ReactNode;
}

export function HoloGrid({ columns = 3, gap = 'gap-4', children }: Readonly<HoloGridProps>) {
  return (
    <div className={`grid ${gap}`} style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
      {children}
    </div>
  );
}

export default HoloGrid;