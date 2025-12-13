/** @type {import('tailwindcss').Config} */
import plugin from 'tailwindcss/plugin';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'heading': ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
        'body': ['IBM Plex Sans', 'Söhne', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'IBM Plex Mono', 'Courier New', 'monospace'],
      },
      colors: {
        saturn: { 50: '#EEF4FF', 100: '#D9E6FF', 200: '#BCD4FF', 300: '#8EB8FF', 400: '#5A91FF', 500: '#3366FF', 600: '#1E40AF', 700: '#1A357A', 800: '#162B5E', 900: '#0F1E42', glow: 'rgba(51, 102, 255, 0.4)', halo: 'rgba(51, 102, 255, 0.15)' },
        sun: { 50: '#FFFBEA', 100: '#FFF3C4', 200: '#FFE58F', 300: '#FFD558', 400: '#FFC52F', 500: '#FFB800', 600: '#E6A100', 700: '#CC8F00', 800: '#B37D00', 900: '#996B00', glow: 'rgba(255, 184, 0, 0.5)', halo: 'rgba(255, 184, 0, 0.2)' },
        mars: { 50: '#FFF1F2', 100: '#FFE1E3', 200: '#FFC7CB', 300: '#FFA0A7', 400: '#FF6B76', 500: '#FF3B4A', 600: '#E61E2E', 700: '#C20F1F', 800: '#A00D1A', 900: '#840B16', glow: 'rgba(255, 59, 74, 0.5)', halo: 'rgba(255, 59, 74, 0.2)' },
        pearl: { 50: '#FFFFFF', 100: '#FAFAFA', 200: '#F5F5F5', 300: '#E8E8E8', 400: '#D1D1D1', 500: '#B8B8B8', 600: '#8F8F8F', 700: '#6B6B6B', 800: '#4A4A4A', 900: '#2E2E2E', glass: 'rgba(255, 255, 255, 0.08)', border: 'rgba(255, 255, 255, 0.12)' },
        space: { 50: '#E8EAF0', 100: '#C5C9D9', 200: '#9BA1B8', 300: '#727A97', 400: '#4A5276', 500: '#242B45', 600: '#1A2136', 700: '#111728', 800: '#0A0F1C', 900: '#050812', void: 'rgba(10, 15, 28, 0.95)', depth: 'rgba(10, 15, 28, 0.6)' },
        buy: { DEFAULT: '#00E676', light: '#69F0AE' },
        sell: { DEFAULT: '#FF3B4A', light: '#FF6B76' },
      },
      backdropBlur: { 'holo': '24px', 'holo-sm': '12px', 'holo-lg': '40px', 'holo-xl': '64px' },
      boxShadow: {
        'holo': '0 0 40px rgba(51, 102, 255, 0.15), 0 8px 32px rgba(0, 0, 0, 0.4)',
        'holo-strong': '0 0 60px rgba(51, 102, 255, 0.3), 0 12px 48px rgba(0, 0, 0, 0.6)',
        'holo-sun': '0 0 40px rgba(255, 184, 0, 0.2), 0 8px 32px rgba(0, 0, 0, 0.4)',
        'holo-mars': '0 0 40px rgba(255, 59, 74, 0.2), 0 8px 32px rgba(0, 0, 0, 0.4)',
        'depth-1': '0 4px 16px rgba(0, 0, 0, 0.3)',
        'depth-2': '0 8px 32px rgba(0, 0, 0, 0.4)',
        'depth-3': '0 16px 64px rgba(0, 0, 0, 0.5)',
        'inner-glow': 'inset 0 0 20px rgba(51, 102, 255, 0.1)',
      },
      transitionTimingFunction: { 'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)', 'spring-smooth': 'cubic-bezier(0.16, 1, 0.3, 1)', 'elastic': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)' },
      backgroundImage: {
        'holo-gradient': 'linear-gradient(135deg, rgba(51, 102, 255, 0.1) 0%, rgba(255, 184, 0, 0.05) 100%)',
        'holo-border': 'linear-gradient(to right, rgba(51, 102, 255, 0.3), rgba(255, 184, 0, 0.3))',
        'space-depth': 'radial-gradient(circle at 50% 50%, rgba(36, 43, 69, 0.8) 0%, rgba(5, 8, 18, 1) 100%)',
        'glass-shimmer': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 50%, rgba(255, 255, 255, 0.1) 100%)',
      },
      zIndex: { 'depth-back': '-10', 'depth-base': '0', 'holo-surface': '10', 'holo-elevated': '20', 'holo-overlay': '30', 'command-halo': '100', 'ai-insight': '90' },
      transitionDuration: { '250': '250ms', '400': '400ms', '600': '600ms' },
      borderRadius: { 'holo': '16px', 'holo-sm': '12px', 'holo-lg': '24px', 'holo-xl': '32px' },
    },
  },
  plugins: [
    plugin(function({ addUtilities, addComponents }) {
      addUtilities({
        '.hologlass': { background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(24px)', border: '1px solid rgba(255, 255, 255, 0.08)', boxShadow: '0 0 40px rgba(51, 102, 255, 0.15), 0 8px 32px rgba(0, 0, 0, 0.4)' },
        '.hologlass-strong': { background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(40px)', border: '1px solid rgba(255, 255, 255, 0.15)', boxShadow: '0 0 60px rgba(51, 102, 255, 0.3), 0 12px 48px rgba(0, 0, 0, 0.6)' },
        '.hologlass-pearl': { background: 'rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(24px)', border: '1px solid rgba(255, 255, 255, 0.12)' },
        '.hologlass-saturn': { background: 'rgba(51, 102, 255, 0.08)', backdropFilter: 'blur(24px)', border: '1px solid rgba(51, 102, 255, 0.2)', boxShadow: '0 0 40px rgba(51, 102, 255, 0.25), 0 8px 32px rgba(0, 0, 0, 0.4)' },
        '.hologlass-sun': { background: 'rgba(255, 184, 0, 0.08)', backdropFilter: 'blur(24px)', border: '1px solid rgba(255, 184, 0, 0.2)', boxShadow: '0 0 40px rgba(255, 184, 0, 0.25), 0 8px 32px rgba(0, 0, 0, 0.4)' },
        '.transform-3d': { transformStyle: 'preserve-3d' },
        '.backface-hidden': { backfaceVisibility: 'hidden' },
        '.volumetric-float': { transform: 'translateZ(20px)' },
        '.volumetric-hover': { transform: 'translateZ(40px) scale(1.02)', transition: 'transform 400ms cubic-bezier(0.34, 1.56, 0.64, 1)' },
        '.text-glow-saturn': { textShadow: '0 0 20px rgba(51, 102, 255, 0.6), 0 0 40px rgba(51, 102, 255, 0.3)' },
        '.text-glow-sun': { textShadow: '0 0 20px rgba(255, 184, 0, 0.6), 0 0 40px rgba(255, 184, 0, 0.3)' },
        '.edge-highlight': { position: 'relative' },
      });

      addComponents({
        '.command-halo': { position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '640px', maxWidth: '90vw', background: 'rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(40px)', border: '1px solid rgba(255, 255, 255, 0.15)', borderRadius: '24px', boxShadow: '0 0 80px rgba(51, 102, 255, 0.4), 0 16px 64px rgba(0, 0, 0, 0.7)', zIndex: '100' },
        '.ai-insight-bar': { background: 'rgba(51, 102, 255, 0.05)', backdropFilter: 'blur(16px)', border: '1px solid rgba(51, 102, 255, 0.2)', borderRadius: '12px', padding: '12px 16px', boxShadow: '0 0 24px rgba(51, 102, 255, 0.15)' },
        '.volumetric-row': { background: 'rgba(255, 255, 255, 0.03)', backdropFilter: 'blur(12px)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px', transform: 'translateZ(0)', transition: 'all 300ms cubic-bezier(0.34, 1.56, 0.64, 1)' },
      });
    }),
  ],
};
