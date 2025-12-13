import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { BACKOFFICE_MODULES, COMMAND_SHORTCUTS } from '../../types/2040.types';
import { useSceneStore } from '../../store/sceneStore';

interface CommandHaloProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandHalo: React.FC<CommandHaloProps> = ({ isOpen, onClose }) => {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();
  const { saveScene, listScenes, loadScene } = useSceneStore();

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  const commands = [
    {
      category: 'Navigation',
      items: BACKOFFICE_MODULES.map((module) => ({
        id: `nav-${module.id}`,
        label: module.name,
        description: `Go to ${module.name}`,
        icon: module.icon,
        action: () => {
          navigate(module.path);
          onClose();
        },
      })),
    },
    {
      category: 'AI Actions',
      items: [
        {
          id: 'ai-insight',
          label: 'Request AI Insight',
          description: 'Get AI analysis of current context',
          icon: '🤖',
          action: () => {
            console.log('AI Insight requested');
            onClose();
          },
        },
        {
          id: 'ai-automate',
          label: 'Automate Task',
          description: 'Set up AI automation for repetitive tasks',
          icon: '⚡',
          action: () => {
            console.log('Automation setup');
            onClose();
          },
        },
      ],
    },
    {
      category: 'Scene Management',
      items: [
        {
          id: 'scene-save',
          label: 'Save Current Scene',
          description: 'Save workspace layout and filters',
          icon: '💾',
          action: () => {
            const scene = {
              id: `scene-${Date.now()}`,
              name: `Scene ${new Date().toLocaleString()}`,
              cameraAngle: { x: 0, y: 0, z: 0 },
              pinnedPanels: [],
              activeFilters: {},
              aiContext: {
                predictions: [],
                suggestions: [],
                automations: [],
                insights: [],
              },
              timestamp: Date.now(),
            };
            saveScene(scene);
            onClose();
          },
        },
      ],
    },
  ];

  const filteredCommands = commands.map((category) => ({
    ...category,
    items: category.items.filter(
      (item) =>
        item.label.toLowerCase().includes(search.toLowerCase()) ||
        item.description.toLowerCase().includes(search.toLowerCase())
    ),
  })).filter((category) => category.items.length > 0);

  const allFilteredItems = filteredCommands.flatMap((cat) => cat.items);

  const handleSelect = (index: number) => {
    if (allFilteredItems[index]) {
      allFilteredItems[index].action();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-space-void z-command-halo"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Command Halo */}
          <motion.div
            className="command-halo"
            initial={{ opacity: 0, scale: 0.9, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {/* Search Input */}
            <div className="p-4 border-b border-pearl-glass">
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setSelectedIndex(0);
                }}
                placeholder="Type a command or search..."
                className="w-full bg-transparent text-pearl-100 text-lg font-body outline-none placeholder-pearl-400"
                autoFocus
              />
            </div>

            {/* Commands List */}
            <div className="max-h-96 overflow-y-auto p-2">
              {filteredCommands.map((category, catIndex) => (
                <div key={category.category} className="mb-4 last:mb-0">
                  <div className="px-3 py-2 text-xs font-mono uppercase tracking-wider text-pearl-400">
                    {category.category}
                  </div>
                  <div className="space-y-1">
                    {category.items.map((item, itemIndex) => {
                      const globalIndex = filteredCommands
                        .slice(0, catIndex)
                        .reduce((acc, cat) => acc + cat.items.length, 0) + itemIndex;
                      const isSelected = globalIndex === selectedIndex;

                      return (
                        <motion.button
                          key={item.id}
                          className={`
                            w-full px-3 py-2 rounded-lg text-left flex items-center gap-3
                            transition-colors
                            ${
                              isSelected
                                ? 'bg-saturn-500/20 text-saturn-200'
                                : 'text-pearl-200 hover:bg-pearl-500/10'
                            }
                          `}
                          onClick={() => item.action()}
                          onMouseEnter={() => setSelectedIndex(globalIndex)}
                          whileHover={{ x: 4 }}
                        >
                          <span className="text-lg">{item.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium">{item.label}</div>
                            <div className="text-xs text-pearl-400 truncate">
                              {item.description}
                            </div>
                          </div>
                        </motion.button>
                      );
                    })}
                  </div>
                </div>
              ))}

              {allFilteredItems.length === 0 && (
                <div className="text-center py-8 text-pearl-400">
                  <div className="text-2xl mb-2">∅</div>
                  <div className="text-sm">No commands found</div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-pearl-glass flex items-center justify-between text-xs text-pearl-400">
              <div className="flex gap-4">
                <span className="flex items-center gap-1">
                  <kbd className="px-2 py-1 bg-pearl-500/10 rounded">↑↓</kbd>
                  Navigate
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="px-2 py-1 bg-pearl-500/10 rounded">↵</kbd>
                  Select
                </span>
              </div>
              <span className="flex items-center gap-1">
                <kbd className="px-2 py-1 bg-pearl-500/10 rounded">Esc</kbd>
                Close
              </span>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// Hook to control Command Halo
export function useCommandHalo() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        (e.metaKey || e.ctrlKey) &&
        e.shiftKey &&
        e.code === 'Space'
      ) {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((prev) => !prev),
  };
}
