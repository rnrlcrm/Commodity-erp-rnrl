import React, { useEffect, useMemo, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { BACKOFFICE_MODULES } from '../types/2040.types';
import { useSceneStore } from '../store/sceneStore';
import { WorkspaceDock, CommandHalo } from '../components/2040';
import { CompanyLogo } from '@/components/common/CompanyLogo';

export const Layout2040: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { motionPreferences, setMotionPreferences } = useSceneStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const currentModule = BACKOFFICE_MODULES.find((m) =>
    location.pathname.startsWith(m.path)
  );

  const dockItems = useMemo(() => BACKOFFICE_MODULES.map(m => ({ key: m.path, label: m.name })), []);
  const [commandOpen, setCommandOpen] = useState(false);

  // Keyboard shortcut: Cmd/Ctrl + Shift + Space to toggle Command Halo
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const isCmd = e.metaKey || e.ctrlKey;
      if (isCmd && e.shiftKey && e.code === 'Space') {
        e.preventDefault();
        setCommandOpen((v) => !v);
      }
      if (e.code === 'Escape') setCommandOpen(false);
    };
    globalThis.addEventListener?.('keydown', handler);
    return () => globalThis.removeEventListener?.('keydown', handler);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-space-900 via-space-800 to-space-900 relative overflow-hidden">
      {/* Background Effect — Aurora Radial Gradient Blobs */}
      <div className="absolute w-[900px] h-[900px] rounded-full 
    bg-[radial-gradient(circle,rgba(59,130,246,0.28),rgba(59,130,246,0.1),rgba(59,130,246,0))]
    blur-[80px] mix-blend-screen opacity-30 pointer-events-none -top-40 -left-40"></div>
      <div className="absolute w-[1100px] h-[1100px] rounded-full 
    bg-[radial-gradient(circle,rgba(251,191,36,0.22),rgba(251,191,36,0.05),rgba(251,191,36,0))]
    blur-[90px] mix-blend-screen opacity-25 pointer-events-none -bottom-40 right-0"></div>

      {/* Holographic Sidebar */}
      <motion.aside
        className={`
          fixed left-0 top-0 bottom-0 z-holo-elevated
          bg-space-700/60 backdrop-blur-glass border-r border-saturn-500/20
          transition-all duration-400 shadow-[0_0_50px_rgba(37,99,235,0.1)]
          ${sidebarCollapsed ? 'w-20' : 'w-64'}
        `}
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
      >
        {/* Logo */}
        <div className="p-6 border-b border-saturn-500/20">
          <motion.div className="flex items-center gap-3" whileHover={{ scale: 1.02 }}>
            <CompanyLogo
              size={sidebarCollapsed ? 'sm' : 'md'}
              className="drop-shadow-[0_0_24px_rgba(59,130,246,0.35)]"
            />
            {!sidebarCollapsed && (
              <div>
                <div className="text-sm font-heading text-pearl-50 text-glow-saturn">Back Office</div>
                <div className="text-xs text-pearl-400 font-mono">2040 Control Center</div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {BACKOFFICE_MODULES.map((module) => {
            const isActive = location.pathname.startsWith(module.path);
            
            return (
              <motion.button
                key={module.id}
                onClick={() => navigate(module.path)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-xl
                  transition-all relative group transform-gpu
                  ${
                    isActive
                      ? 'bg-saturn-500/20 text-saturn-300 shadow-[0_0_20px_rgba(59,130,246,0.3)] border border-saturn-500/30'
                      : 'text-pearl-300 hover:bg-pearl-500/10 hover:shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                  }
                `}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
              >
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-saturn-400 rounded-r-full"
                    layoutId="activeIndicator"
                  />
                )}

                <span className="text-lg">
                  {module.icon === 'settings' && '⚙️'}
                  {module.icon === 'users' && '👥'}
                  {module.icon === 'building' && '🏢'}
                  {module.icon === 'chart' && '📊'}
                  {module.icon === 'check-circle' && '✓'}
                  {module.icon === 'truck' && '🚚'}
                  {module.icon === 'package' && '📦'}
                  {module.icon === 'dollar' && '💰'}
                  {module.icon === 'alert-triangle' && '⚠️'}
                  {module.icon === 'clock' && '🕐'}
                  {module.icon === 'file' && '📄'}
                </span>

                {!sidebarCollapsed && (
                  <span className="text-sm flex-1 text-left">{module.name}</span>
                )}

                {/* Real-time indicator */}
                {isActive && !sidebarCollapsed && (
                  <motion.div
                    className="w-2 h-2 bg-saturn-400 rounded-full"
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  />
                )}
              </motion.button>
            );
          })}
        </nav>

        {/* Bottom Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-pearl-border">
          <motion.button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="w-full px-4 py-2 text-sm text-pearl-300 hover:text-pearl-100 rounded-lg hover:bg-pearl-500/10 transition-colors"
            whileHover={{ scale: 1.05 }}
          >
            {sidebarCollapsed ? '→' : '←'}
          </motion.button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main
        className={`
          transition-all duration-400
          ${sidebarCollapsed ? 'ml-20' : 'ml-64'}
        `}
      >
        {/* Top Bar */}
        <div className="sticky top-0 z-holo-elevated hologlass-pearl border-b border-pearl-border backdrop-blur-holo">
          <div className="px-6 py-4 flex items-center justify-between">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm">
              <span className="text-pearl-400">2040</span>
              <span className="text-pearl-600">/</span>
              <span className="text-pearl-200">{currentModule?.name || 'Dashboard'}</span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {/* Motion Preferences Toggle */}
              <motion.button
                onClick={() =>
                  setMotionPreferences({
                    reducedMotion: !motionPreferences.reducedMotion,
                  })
                }
                className={`
                  px-3 py-1.5 text-xs rounded-lg border transition-colors
                  ${
                    motionPreferences.reducedMotion
                      ? 'bg-pearl-500/20 text-pearl-300 border-pearl-500/40'
                      : 'bg-saturn-500/10 text-saturn-300 border-saturn-500/20'
                  }
                `}
                whileHover={{ scale: 1.05 }}
                title="Toggle reduced motion"
              >
                {motionPreferences.reducedMotion ? '⏸' : '▶️'}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Command Halo */}
      <CommandHalo isOpen={commandOpen} onClose={() => setCommandOpen(false)} />

      {/* Workspace Dock */}
      <WorkspaceDock
        items={dockItems}
        active={currentModule?.path || '/2040/trade-desk'}
        onSelect={(key) => navigate(key)}
      />

      {/* Keyboard Shortcut Hint */}
      <motion.div
        className="fixed bottom-6 left-6 text-xs text-pearl-400 hologlass-pearl px-3 py-2 rounded-lg"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        Press <kbd className="px-2 py-1 bg-pearl-500/20 rounded">⌘+Shift+Space</kbd> for Command Halo
      </motion.div>
    </div>
  );
};
