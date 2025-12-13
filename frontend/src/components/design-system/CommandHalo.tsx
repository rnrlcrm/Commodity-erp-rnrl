import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { HoloPanel } from './HoloPanel';
import { LiquidButton } from './LiquidButton';
import { PulsingStatusNode } from './PulsingStatusNode';

export type CommandStatus = 'active' | 'standby' | 'warning' | 'critical';

export interface CommandHaloCommand {
  id: string;
  label: string;
  detail: string;
  status: CommandStatus;
  icon?: LucideIcon;
  onExecute?: () => void;
}

export interface CommandHaloTelemetry {
  id: string;
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'steady';
}

export interface CommandHaloProps {
  title?: string;
  commands: CommandHaloCommand[];
  telemetry?: CommandHaloTelemetry[];
  className?: string;
}

function getStatusCopy(status: CommandStatus) {
  switch (status) {
    case 'active':
      return { indicator: 'active', badge: 'ENGAGED' } as const;
    case 'standby':
      return { indicator: 'processing', badge: 'ON DECK' } as const;
    case 'warning':
      return { indicator: 'warning', badge: 'ELEVATED' } as const;
    case 'critical':
      return { indicator: 'critical', badge: 'OVERRIDE' } as const;
    default:
      return { indicator: 'processing', badge: 'SYNC' } as const;
  }
}

function trendGradient(trend?: CommandHaloTelemetry['trend']) {
  switch (trend) {
    case 'up':
      return 'from-buy-light/30 to-buy-light/0 text-buy-light';
    case 'down':
      return 'from-mars-400/30 to-mars-400/0 text-mars-300';
    default:
      return 'from-saturn-400/20 to-saturn-400/0 text-saturn-200';
  }
}

export function CommandHalo({ title = 'COMMAND HALO', commands, telemetry = [], className }: Readonly<CommandHaloProps>) {
  return (
    <HoloPanel title={title} accent="saturn" className={className}>
      <div className="relative overflow-hidden rounded-4xl border border-pearl-300/10 bg-space-900/40 p-6 shadow-[0_32px_96px_rgba(5,10,20,0.55)]">
        <OrbitalHalo />
        <div className="relative z-10 flex flex-col gap-8">
          <div className="grid gap-4 md:grid-cols-2">
            {commands.map((command, index) => {
              const Icon = command.icon;
              const copy = getStatusCopy(command.status);
              return (
                <motion.div
                  key={command.id}
                  className="group relative overflow-hidden rounded-3xl border border-pearl-300/10 bg-white/5 p-5 backdrop-blur-glass"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, delay: index * 0.05, ease: 'easeOut' }}
                  whileHover={{ translateY: -4 }}
                >
                  <span className="absolute inset-0 bg-gradient-to-br from-saturn-400/10 via-transparent to-sun-400/10 opacity-70" />
                  <div className="relative flex flex-col gap-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <PulsingStatusNode status={copy.indicator} size="md" />
                        <span className="text-sm uppercase tracking-[0.22em] text-pearl-50">{command.label}</span>
                      </div>
                      <span className="rounded-full border border-pearl-300/20 px-3 py-1 text-[0.6rem] uppercase tracking-[0.3em] text-saturn-200">
                        {copy.badge}
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed tracking-[0.18em] text-pearl-200/80">{command.detail}</p>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3 text-[0.7rem] uppercase tracking-[0.24em] text-pearl-100/60">
                        {Icon ? <Icon className="h-5 w-5 text-saturn-200/80" /> : null}
                        <span>{command.status.toUpperCase()}</span>
                      </div>
                      <LiquidButton variant={command.status === 'critical' ? 'danger' : 'secondary'} onClick={command.onExecute}>
                        Engage
                      </LiquidButton>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {telemetry.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {telemetry.map((item, index) => (
                <motion.div
                  key={item.id}
                  className="relative overflow-hidden rounded-3xl border border-pearl-300/10 bg-space-900/40 p-4"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.04, ease: 'easeOut' }}
                >
                  <span
                    aria-hidden
                    className={clsx('absolute inset-0 bg-gradient-to-br opacity-60', trendGradient(item.trend))}
                  />
                  <div className="relative flex flex-col gap-2">
                    <span className="text-[0.58rem] uppercase tracking-[0.28em] text-pearl-200/70">{item.label}</span>
                    <span className="text-lg tracking-[0.18em]">{item.value}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </HoloPanel>
  );
}

function OrbitalHalo() {
  return (
    <div className="pointer-events-none absolute inset-0 will-change-[transform,opacity]">
      <motion.div
        className="absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-saturn-400/20"
        animate={{ rotate: 360 }}
        transition={{ duration: 36, ease: 'linear', repeat: Infinity }}
      />
      <motion.div
        className="absolute left-1/2 top-1/2 h-[300px] w-[620px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-sun-300/15"
        animate={{ rotate: -360 }}
        transition={{ duration: 48, ease: 'linear', repeat: Infinity }}
      />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.25),rgba(2,6,23,0)_65%)]" />
    </div>
  );
}
