import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { HoloPanel } from './HoloPanel';
import { PulsingStatusNode } from './PulsingStatusNode';
import { TimelineStream, type TimelineEvent } from './TimelineStream';

export type WorkspaceStatus = 'active' | 'maintenance' | 'warning' | 'critical';

export interface WorkspaceDockModule {
  id: string;
  title: string;
  description: string;
  status: WorkspaceStatus;
  icon?: LucideIcon;
  metrics?: Array<{ id: string; label: string; value: string }>;
  activity?: TimelineEvent[];
}

export interface WorkspaceDockProps {
  modules: WorkspaceDockModule[];
  className?: string;
}

function statusToIndicator(status: WorkspaceStatus) {
  switch (status) {
    case 'active':
      return 'processing';
    case 'maintenance':
      return 'warning';
    case 'warning':
      return 'warning';
    case 'critical':
      return 'critical';
    default:
      return 'active';
  }
}

function statusChip(status: WorkspaceStatus) {
  switch (status) {
    case 'active':
      return 'bg-saturn-400/20 text-saturn-100 border-saturn-300/30';
    case 'maintenance':
      return 'bg-sun-400/20 text-sun-200 border-sun-300/30';
    case 'warning':
      return 'bg-sun-400/25 text-sun-300 border-sun-400/40';
    case 'critical':
      return 'bg-mars-400/25 text-mars-200 border-mars-400/40';
    default:
      return 'bg-saturn-400/20 text-saturn-100 border-saturn-300/30';
  }
}

export function WorkspaceDock({ modules, className }: Readonly<WorkspaceDockProps>) {
  return (
    <HoloPanel title="WORKSPACE DOCK" accent="saturn" className={className}>
      <div className="flex flex-col gap-6">
        {modules.map((module, index) => {
          const Icon = module.icon;
          const indicator = statusToIndicator(module.status);

          return (
            <motion.div
              key={module.id}
              className="relative overflow-hidden rounded-4xl border border-pearl-300/10 bg-space-900/40 p-6 shadow-[0_26px_80px_rgba(5,10,20,0.55)]"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: index * 0.06, ease: 'easeOut' }}
              whileHover={{ y: -6 }}
            >
              <span className="absolute inset-0 bg-gradient-to-br from-pearl-300/10 via-transparent to-saturn-400/10 opacity-75" />
              <div className="relative flex flex-col gap-6">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center gap-4">
                      <PulsingStatusNode status={indicator} size="md" />
                      <div className="flex items-center gap-3">
                        {Icon ? (
                          <span className="flex h-10 w-10 items-center justify-center rounded-full border border-pearl-300/15 bg-black/30 text-saturn-200">
                            <Icon className="h-5 w-5" />
                          </span>
                        ) : null}
                        <span className="text-lg uppercase tracking-[0.2em] text-pearl-50">{module.title}</span>
                      </div>
                    </div>
                    <p className="max-w-3xl text-xs leading-relaxed tracking-[0.18em] text-pearl-200/80">
                      {module.description}
                    </p>
                  </div>
                  <span
                    className={clsx(
                      'inline-flex h-9 items-center justify-center rounded-full border px-5 text-[0.58rem] uppercase tracking-[0.3em]',
                      statusChip(module.status)
                    )}
                  >
                    {module.status.toUpperCase()}
                  </span>
                </div>

                {module.metrics && module.metrics.length > 0 ? (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {module.metrics.map((metric, metricIndex) => (
                      <motion.div
                        key={metric.id}
                        className="relative overflow-hidden rounded-3xl border border-pearl-300/15 bg-white/5 p-4 backdrop-blur-glass"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: metricIndex * 0.05, ease: 'easeOut' }}
                      >
                        <span className="absolute inset-0 bg-gradient-to-br from-saturn-400/10 via-transparent to-mars-400/10 opacity-60" />
                        <div className="relative flex flex-col gap-2">
                          <span className="text-[0.58rem] uppercase tracking-[0.26em] text-pearl-200/70">{metric.label}</span>
                          <span className="text-base tracking-[0.18em] text-pearl-50">{metric.value}</span>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : null}

                {module.activity && module.activity.length > 0 ? (
                  <div className="rounded-4xl border border-pearl-300/10 bg-white/5 p-4">
                    <TimelineStream events={module.activity} />
                  </div>
                ) : null}
              </div>
            </motion.div>
          );
        })}
      </div>
    </HoloPanel>
  );
}
