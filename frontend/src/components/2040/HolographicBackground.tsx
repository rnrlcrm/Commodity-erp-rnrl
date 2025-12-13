/**
 * Holographic Background Component - OPTIMIZED
 * Static blurred circular radial gradients with screen blend mode
 * Specifications: blur 60-80px, opacity 20-30%, 2040 colors
 */

interface HolographicBackgroundProps {
  className?: string;
}

export function HolographicBackground({ className = '' }: HolographicBackgroundProps) {
  return (
    <div className={`fixed inset-0 pointer-events-none overflow-hidden ${className}`}>
      {/* Dark overlay */}
      <div className="absolute inset-0 opacity-95" style={{ background: 'var(--space-void)' }} />
      
      {/* Blob 1: Saturn Blue (top-left) */}
      <div
        className="absolute -top-40 -left-40 w-[1000px] h-[1000px] rounded-full mix-blend-screen opacity-30"
        style={{
          background: 'radial-gradient(circle, rgba(51,102,255,0.3) 0%, transparent 70%)',
          filter: 'blur(80px)'
        }}
      />
      
      {/* Blob 2: Sun Yellow (right-side) */}
      <div
        className="absolute top-1/3 -right-60 w-[900px] h-[900px] rounded-full mix-blend-screen opacity-25"
        style={{
          background: 'radial-gradient(circle, rgba(255,184,0,0.25) 0%, transparent 70%)',
          filter: 'blur(70px)'
        }}
      />
      
      {/* Blob 3: Teal (bottom-center) */}
      <div
        className="absolute -bottom-48 left-1/2 -translate-x-1/2 w-[1100px] h-[1100px] rounded-full mix-blend-screen opacity-22"
        style={{
          background: 'radial-gradient(circle, rgba(16,185,129,0.22) 0%, transparent 70%)',
          filter: 'blur(75px)'
        }}
      />
    </div>
  );
}
