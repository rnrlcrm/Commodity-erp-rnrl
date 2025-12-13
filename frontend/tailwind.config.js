/** @type {import('tailwindcss').Config} */
import forms from '@tailwindcss/forms';

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}'
  ],
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        saturn: {
          100: 'var(--color-saturn-100)',
          200: 'var(--color-saturn-200)',
          300: 'var(--color-saturn-300)',
          400: 'var(--color-saturn-400)',
          500: 'var(--color-saturn-500)'
        },
        sun: {
          200: 'var(--color-sun-200)',
          300: 'var(--color-sun-300)',
          400: 'var(--color-sun-400)',
          500: 'var(--color-sun-500)'
        },
        mars: {
          300: 'var(--color-mars-300)',
          400: 'var(--color-mars-400)',
          500: 'var(--color-mars-500)',
          700: 'var(--color-mars-700)'
        },
        pearl: {
          50: 'var(--color-pearl-50)',
          100: 'var(--color-pearl-100)',
          200: 'var(--color-pearl-200)',
          300: 'var(--color-pearl-300)',
          500: 'var(--color-pearl-500)'
        },
        space: {
          600: 'var(--color-space-600)',
          700: 'var(--color-space-700)',
          800: 'var(--color-space-800)',
          900: 'var(--color-space-900)'
        }
      },
      fontFamily: {
        heading: 'var(--font-family-heading)',
        body: 'var(--font-family-body)',
        mono: 'var(--font-family-mono)'
      },
      spacing: {
        6: 'var(--spacing-6)',
        8: 'var(--spacing-8)',
        10: 'var(--spacing-10)'
      },
      borderRadius: {
        '3xl': 'var(--radius-3xl)',
        '4xl': 'var(--radius-4xl)'
      },
      boxShadow: {
        holo: '0 20px 60px rgba(96, 165, 250, 0.35)',
        'holo-sun': '0 20px 60px rgba(251, 191, 36, 0.35)',
        'holo-mars': '0 20px 60px rgba(248, 113, 113, 0.35)',
        depth: '0 30px 120px rgba(5, 10, 20, 0.65)'
      },
      backdropBlur: {
        glass: 'var(--backdrop-blur-glass)'
      }
    }
  },
  plugins: [
    forms,
    function ({ addUtilities, addVariant }) {
      addUtilities(
        {
          '.perspective-1600': {
            perspective: '1600px'
          },
          '.holo-transform-gpu': {
            transform: 'translateZ(0)',
            willChange: 'transform'
          },
          '.rotate-x-6': {
            transform: 'rotateX(6deg)'
          },
          '.backdrop-blur-glass': {
            backdropFilter: 'var(--backdrop-blur-glass)'
          },
          '.will-change-filter': {
            willChange: 'filter, backdrop-filter'
          }
        },
        ['responsive']
      );

      addUtilities({
        '@keyframes holo-pulse': {
          '0%, 100%': {
            opacity: '0.6',
            filter: 'brightness(1)'
          },
          '50%': {
            opacity: '1',
            filter: 'brightness(1.3)'
          }
        }
      });

      addUtilities(
        {
          '.animate-holo-pulse': {
            animation: 'holo-pulse 2.4s ease-in-out infinite'
          }
        },
        ['responsive', 'motion-safe']
      );

      addVariant('supports-backdrop', '@supports (backdrop-filter: blur(1px))');
      addVariant('motion-safe', '@media (prefers-reduced-motion: no-preference)');
      addVariant('motion-reduce', '@media (prefers-reduced-motion: reduce)');
    }
  ]
};
