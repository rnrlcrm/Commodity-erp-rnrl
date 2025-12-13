import clsx from 'clsx';
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';
import { PulsingStatusNode } from './PulsingStatusNode';

type TimelineAccent = 'saturn' | 'sun' | 'mars' | 'pearl';

function getStatusFromAccent(accent?: TimelineAccent) {
  switch (accent) {
    case 'sun':
      return 'warning';
    case 'mars':
      return 'critical';
    case 'saturn':
      return 'processing';
    default:
      return 'active';
  }
}

export interface TimelineEvent {
  id: string;
  time: string;
  title: string;
  description?: string;
  accent?: TimelineAccent;
  icon?: ReactNode;
}

export interface TimelineStreamProps {
  events: TimelineEvent[];
  className?: string;
}

export function TimelineStream({ events, className }: Readonly<TimelineStreamProps>) {
  return (
    <motion.ol
      className={clsx('relative flex flex-col gap-6 pl-4', className)}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
    >
      <span
        aria-hidden
        className="pointer-events-none absolute left-1 top-0 h-full w-px bg-gradient-to-b from-pearl-300/10 via-pearl-300/20 to-transparent"
      />
      {events.map((event, index) => {
        const isLast = index === events.length - 1;
        const status = getStatusFromAccent(event.accent);

        return (
          <motion.li
            key={event.id}
            className="relative flex flex-col gap-2 rounded-3xl border border-pearl-300/10 bg-white/5 px-5 py-4 backdrop-blur-glass"
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, ease: 'easeOut', delay: index * 0.05 }}
          >
            <span className="absolute -left-3 top-5">
              <PulsingStatusNode status={status} size="md" />
            </span>
            {!isLast ? (
              <span
                aria-hidden
                className="pointer-events-none absolute -left-[0.125rem] top-12 h-12 w-px bg-gradient-to-b from-pearl-300/20 to-transparent"
              />
            ) : null}
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.24em] text-pearl-300/70">
              <span>{event.time}</span>
              {event.icon ? <span className="text-pearl-200/60">{event.icon}</span> : null}
            </div>
            <div className="text-sm tracking-[0.1em] text-pearl-100">{event.title}</div>
            {event.description ? (
              <div className="text-xs tracking-[0.16em] text-pearl-200/70">{event.description}</div>
            ) : null}
          </motion.li>
        );
      })}
    </motion.ol>
  );
}
