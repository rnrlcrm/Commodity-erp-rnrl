import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import { HoloPanel } from '../components/design-system/HoloPanel';
import { AIInsightBar, type AIInsight } from '../components/design-system/AIInsightBar';
import { FloatingActionBar, type FloatingActionBarAction } from '../components/design-system/FloatingActionBar';
import { HoloGrid } from '../components/design-system/HoloGrid';
import { LiquidButton } from '../components/design-system/LiquidButton';
import { MultiLayerTabs } from '../components/design-system/MultiLayerTabs';
import { NeonInputField } from '../components/design-system/NeonInputField';
import { TimelineStream, type TimelineEvent } from '../components/design-system/TimelineStream';
import { VolumetricTable, type VolumetricRow } from '../components/design-system/VolumetricTable';

export function HoloShell() {
  const [instrumentFilter, setInstrumentFilter] = useState('');

  const rows = useMemo<VolumetricRow[]>(
    () => [
      {
        id: 'row-a',
        asset: 'Brazil Fiber A16',
        region: 'LATAM-ORB',
        exposure: '42.7K T',
        delta: '+1.8%',
        status: 'processing',
        supervisor: 'Chavez • G'
      },
      {
        id: 'row-b',
        asset: 'India Staple P8',
        region: 'APAC-MTR',
        exposure: '31.4K T',
        delta: '-0.6%',
        status: 'critical',
        supervisor: 'Verma • S'
      },
      {
        id: 'row-c',
        asset: 'US Delta L2',
        region: 'NA-DELTA',
        exposure: '24.9K T',
        delta: '+0.4%',
        status: 'active',
        supervisor: 'Harris • P'
      },
      {
        id: 'row-d',
        asset: 'Egypt Long E3',
        region: 'MENA-PORT',
        exposure: '19.6K T',
        delta: '+0.9%',
        status: 'warning',
        supervisor: 'Nassar • L'
      }
    ],
    []
  );

  const filteredRows = useMemo(() => {
    const term = instrumentFilter.trim().toLowerCase();
    if (!term) {
      return rows;
    }

    return rows.filter((row) =>
      [row.asset, row.region, row.supervisor].some((value) => value.toLowerCase().includes(term))
    );
  }, [instrumentFilter, rows]);

  const riskRows = useMemo(() => {
    return rows.filter((row) => {
      const numericDelta = Number.parseFloat(row.delta.replace('%', ''));
      return Number.isFinite(numericDelta) && Math.abs(numericDelta) >= 0.8;
    });
  }, [rows]);

  const insights = useMemo<AIInsight[]>(
    () => [
      {
        id: 'ai-1',
        label: 'HEDGING VECTOR UPDATED',
        detail: 'Satellite demand spike detected for LATAM textile nodes. Suggest widening corridor by 2.4%.',
        level: 'info'
      },
      {
        id: 'ai-2',
        label: 'CREDIT CUSHION ALERT',
        detail: 'Oceanic syndicate reduced limit by 4.2M USD. Recommend shifting Brazil fiber to orbital line.',
        level: 'warning'
      },
      {
        id: 'ai-3',
        label: 'NEGOTIATION BOT STATUS',
        detail: 'Gulf counterpart stalled at 04:12 UTC. Deploy escalation routine?',
        level: 'critical'
      }
    ],
    []
  );

  const timeline = useMemo<TimelineEvent[]>(
    () => [
      {
        id: 'evt-1',
        time: '04:22 UTC',
        title: 'APAC mesh reconciled with orbital ledger',
        description: 'Variance dropped to 0.12% after auto-match cycle.',
        accent: 'saturn'
      },
      {
        id: 'evt-2',
        time: '03:58 UTC',
        title: 'Negotiation AI flagged counterparty latency',
        description: 'Queued for human review after 2 automated nudges.',
        accent: 'sun'
      },
      {
        id: 'evt-3',
        time: '03:33 UTC',
        title: 'Warehouse drone fleet re-routed to MENA-PORT',
        description: 'Avoided storm corridor, ETA unchanged.',
        accent: 'saturn'
      },
      {
        id: 'evt-4',
        time: '02:47 UTC',
        title: 'Risk desk applied delta hedge to US Delta L2',
        description: 'Stabilized drift within safe band.',
        accent: 'mars'
      }
    ],
    []
  );

  const allocationEvents = useMemo(() => {
    return timeline.filter((event) =>
      /warehouse|routing|fleet|mesh/i.test(`${event.title} ${event.description ?? ''}`)
    );
  }, [timeline]);

  const workAreaTabs = useMemo(
    () => [
      {
        id: 'positions',
        label: 'POSITIONS',
        badge: filteredRows.length,
        content: (
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
              <NeonInputField
                label="Filter instrument"
                value={instrumentFilter}
                onChange={setInstrumentFilter}
                placeholder="Search instrument, region, or supervisor"
                icon={Search}
                aiSuggestion="Prioritize LATAM fiber corridors"
              />
              <LiquidButton variant="secondary" onClick={() => setInstrumentFilter('')}>
                Reset Filter
              </LiquidButton>
            </div>
            <VolumetricTable rows={filteredRows} />
          </div>
        )
      },
      {
        id: 'risk',
        label: 'RISK WINDOWS',
        badge: riskRows.length,
        content: (
          <div className="flex flex-col gap-6">
            <div className="rounded-3xl border border-pearl-300/10 bg-white/5 p-6 text-sm tracking-[0.14em] text-pearl-200/80 shadow-[0_18px_48px_rgba(5,10,20,0.35)] backdrop-blur-glass">
              Exposure corridors recalibrated at 04:00 UTC. AI recommends hedging the highlighted routes within the next 90 minutes.
            </div>
            <VolumetricTable rows={riskRows.length > 0 ? riskRows : rows} />
          </div>
        )
      },
      {
        id: 'allocations',
        label: 'ALLOCATIONS',
        badge: allocationEvents.length,
        content: (
          <div className="flex flex-col gap-6">
            <div className="rounded-3xl border border-pearl-300/10 bg-white/5 p-6 text-sm tracking-[0.14em] text-pearl-200/80 shadow-[0_18px_48px_rgba(5,10,20,0.35)] backdrop-blur-glass">
              Logistics mesh tracking current reroutes and drone fleet assignments across orbital and terrestrial lanes.
            </div>
            <TimelineStream events={allocationEvents.length > 0 ? allocationEvents : timeline} />
          </div>
        )
      }
    ],
    [allocationEvents, filteredRows, instrumentFilter, riskRows, rows, timeline]
  );

  const actions = useMemo<FloatingActionBarAction[]>(
    () => [
      {
        id: 'act-authorize',
        label: 'Authorize Route',
        variant: 'primary'
      },
      {
        id: 'act-escalate',
        label: 'Escalate Drift',
        variant: 'danger'
      },
      {
        id: 'act-sync',
        label: 'Sync Mesh',
        variant: 'secondary'
      }
    ],
    []
  );

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-space-900 via-space-800 to-space-900">
      <AmbientGrid />
      <div className="relative z-10 flex min-h-screen items-stretch justify-center p-10 perspective-1600">
        <div className="flex w-full max-w-6xl flex-col gap-10">
          <HoloGrid columns={2}>
            <HoloPanel title="PRIMARY WORK AREA" className="w-full">
              <MultiLayerTabs tabs={workAreaTabs} />
            </HoloPanel>

            <HoloPanel title="AI / ACTIVITY" accent="sun" className="w-full">
              <div className="flex flex-col gap-6">
                <AIInsightBar insights={insights} />
                <TimelineStream events={timeline} />
              </div>
            </HoloPanel>
          </HoloGrid>

          <FloatingActionBar actions={actions} />
        </div>
      </div>
    </div>
  );
}

function AmbientGrid() {
  return (
    <div className="pointer-events-none absolute inset-0">
      <svg className="absolute inset-0 h-full w-full opacity-40" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gridGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--color-saturn-300)" stopOpacity="0.2" />
            <stop offset="50%" stopColor="var(--color-sun-300)" stopOpacity="0.15" />
            <stop offset="100%" stopColor="var(--color-mars-400)" stopOpacity="0.1" />
          </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#gridGradient)" />
        <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
          <path
            d="M 80 0 L 0 0 0 80"
            fill="none"
            stroke="var(--color-pearl-300)"
            strokeOpacity="0.15"
            strokeWidth="1"
          />
        </pattern>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(96,165,250,0.3),transparent_45%),radial-gradient(circle_at_80%_30%,rgba(251,191,36,0.2),transparent_55%),radial-gradient(circle_at_50%_80%,rgba(248,113,113,0.25),transparent_50%)]" />
    </div>
  );
}
