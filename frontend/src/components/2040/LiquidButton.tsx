import React, { useEffect, useRef } from 'react';

type LiquidButtonProps = {
  label: string;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
};

// Lightweight canvas-based liquid ripple inside a rounded button
export default function LiquidButton({ label, onClick, className = '', disabled }: LiquidButtonProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = container.clientWidth;
    let height = container.clientHeight;
    canvas.width = width;
    canvas.height = height;

    let t = 0;
    let raf: number;
    const draw = () => {
      t += 0.04;
      ctx.clearRect(0, 0, width, height);
      // glass highlight gradient
      const grad = ctx.createLinearGradient(0, 0, 0, height);
      grad.addColorStop(0, 'rgba(255,255,255,0.35)');
      grad.addColorStop(0.5, 'rgba(255,255,255,0.08)');
      grad.addColorStop(1, 'rgba(255,255,255,0.02)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // liquid waves
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        const amp = 6 + i * 3;
        const freq = 0.02 + i * 0.01;
        const yBase = height * 0.6 + i * 4;
        for (let x = 0; x <= width; x++) {
          const y = yBase + Math.sin(x * freq + t + i * 1.2) * amp;
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fillStyle = `rgba(80,200,255,${0.08 + i * 0.06})`;
        ctx.fill();
      }
      ctx.restore();

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    const onResize = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      canvas.width = width;
      canvas.height = height;
    };
    window.addEventListener('resize', onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
    };
  }, []);

  return (
    <button
      ref={containerRef}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      className={
        `relative overflow-hidden rounded-2xl px-6 py-3 transition-all ` +
        `backdrop-blur-md border border-white/20 shadow-lg ` +
        `bg-gradient-to-br from-white/10 via-white/5 to-white/2 ` +
        `hover:from-cyan-300/20 hover:via-cyan-200/10 hover:to-transparent ` +
        `text-white tracking-wide ${disabled ? 'opacity-60 cursor-not-allowed' : 'hover:scale-[1.02]'} ` +
        className
      }
    >
      <span className="relative z-10 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-cyan-300 animate-pulse" />
        {label}
      </span>
      <canvas ref={canvasRef} className="absolute inset-0 z-0" />
      <span className="absolute inset-0 z-0 pointer-events-none bg-gradient-to-t from-cyan-400/10 to-transparent" />
    </button>
  );
}
