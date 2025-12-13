import { ReactNode } from 'react';
import { GeometricBackground } from '@/components/2040/GeometricBackground';
import { HoloPanel } from '@/components/2040/HoloPanel';

interface SettingsSceneLayoutProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function SettingsSceneLayout({
  title,
  subtitle,
  actions,
  children,
}: Readonly<SettingsSceneLayoutProps>) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-space-950 text-pearl-50">
      <GeometricBackground />
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-48 -left-24 h-[520px] w-[520px] rounded-full bg-saturn-500/20 blur-[180px]" />
        <div className="absolute bottom-[-18rem] right-[-6rem] h-[640px] w-[640px] rounded-full bg-sun-500/15 blur-[200px]" />
      </div>
      <div className="relative z-10 mx-auto flex max-w-7xl flex-col gap-6 px-6 py-10">
        <HoloPanel theme="saturn" glow className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-mono uppercase tracking-[0.35em] text-saturn-200/80">RNRL 2040 Settings Hub</p>
            <h1 className="text-3xl font-heading text-pearl-50 text-glow-saturn">{title}</h1>
            {subtitle && <p className="text-sm text-pearl-300/90">{subtitle}</p>}
          </div>
          {actions && <div className="flex flex-wrap gap-3">{actions}</div>}
        </HoloPanel>
        {children}
      </div>
    </div>
  );
}

export default SettingsSceneLayout;
