import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSceneStore } from '../../store/sceneStore';

interface VolumetricTableProps<T> {
  data: T[];
  columns: {
    key: keyof T;
    label: string;
    render?: (value: any, row: T) => React.ReactNode;
    width?: string;
  }[];
  onRowClick?: (row: T) => void;
  onRowHover?: (row: T | null) => void;
  keyExtractor: (row: T) => string;
  theme?: 'saturn' | 'sun' | 'pearl';
}

export function VolumetricTable<T extends Record<string, any>>({
  data,
  columns,
  onRowClick,
  onRowHover,
  keyExtractor,
  theme = 'pearl',
}: VolumetricTableProps<T>) {
  const { motionPreferences } = useSceneStore();
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  const handleRowHover = (rowKey: string | null, row: T | null) => {
    setHoveredRow(rowKey);
    onRowHover?.(row);
  };

  const getRowGlow = () => {
    switch (theme) {
      case 'saturn':
        return 'hover:shadow-holo';
      case 'sun':
        return 'hover:shadow-holo-sun';
      default:
        return 'hover:shadow-depth-2';
    }
  };

  return (
    <div className="w-full overflow-x-auto">
      {/* Header */}
      <div className="flex gap-2 mb-4 px-4 py-3 hologlass-pearl rounded-holo-sm">
        {columns.map((column) => (
          <div
            key={String(column.key)}
            className="font-mono text-xs uppercase tracking-wider text-pearl-300"
            style={{ width: column.width || 'auto', flex: column.width ? undefined : 1 }}
          >
            {column.label}
          </div>
        ))}
      </div>

      {/* Body */}
      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {data.map((row, index) => {
            const rowKey = keyExtractor(row);
            const isHovered = hoveredRow === rowKey;

            return (
              <motion.div
                key={rowKey}
                className={`
                  volumetric-row
                  flex gap-2 px-4 py-3 cursor-pointer
                  ${getRowGlow()}
                  ${isHovered ? 'bg-white/10' : ''}
                `}
                initial={motionPreferences.reducedMotion ? false : { opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{
                  type: 'spring',
                  stiffness: 300,
                  damping: 30,
                  delay: index * 0.02,
                }}
                whileHover={
                  !motionPreferences.disableVolumetric
                    ? {
                        scale: 1.01,
                        z: 10,
                        transition: { type: 'spring', stiffness: 400 },
                      }
                    : undefined
                }
                onClick={() => onRowClick?.(row)}
                onHoverStart={() => handleRowHover(rowKey, row)}
                onHoverEnd={() => handleRowHover(null, null)}
                layout
              >
                {columns.map((column) => (
                  <div
                    key={String(column.key)}
                    className="text-sm text-pearl-100"
                    style={{ width: column.width || 'auto', flex: column.width ? undefined : 1 }}
                  >
                    {column.render
                      ? column.render(row[column.key], row)
                      : String(row[column.key] ?? '')}
                  </div>
                ))}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Empty state */}
      {data.length === 0 && (
        <motion.div
          className="text-center py-12 text-pearl-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="text-4xl mb-2">∅</div>
          <div className="text-sm">No data to display</div>
        </motion.div>
      )}
    </div>
  );
}

// Utility component for status badges in tables
export const VolumetricBadge: React.FC<{
  status: 'active' | 'pending' | 'completed' | 'failed' | 'warning';
  children: React.ReactNode;
}> = ({ status, children }) => {
  const colors = {
    active: 'bg-saturn-500/20 text-saturn-300 border-saturn-500/40',
    pending: 'bg-sun-500/20 text-sun-300 border-sun-500/40',
    completed: 'bg-green-500/20 text-green-300 border-green-500/40',
    failed: 'bg-mars-500/20 text-mars-300 border-mars-500/40',
    warning: 'bg-sun-500/20 text-sun-300 border-sun-500/40',
  };

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono
        border backdrop-blur-sm
        ${colors[status]}
      `}
    >
      {children}
    </span>
  );
};
