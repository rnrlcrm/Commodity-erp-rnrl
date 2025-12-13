import { HoloPanel } from './HoloPanel';

interface HoloCardProps {
  title?: string;
  footer?: React.ReactNode;
  children?: React.ReactNode;
  theme?: 'saturn' | 'sun' | 'mars' | 'pearl' | 'space';
}

export function HoloCard({ title, footer, children, theme = 'pearl' }: Readonly<HoloCardProps>) {
  return (
    <HoloPanel elevated glow theme={theme} className="space-y-3">
      {title && <div className="text-pearl-100 font-semibold">{title}</div>}
      <div>{children}</div>
      {footer && <div className="pt-2 border-t border-white/10 text-pearl-300">{footer}</div>}
    </HoloPanel>
  );
}

export default HoloCard;