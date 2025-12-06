/** @type {import('tailwindcss').Config} */
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
      transitionDuration: {
        '120': '120ms',
      },
      zIndex: {
        '35': '35',
        '45': '45',
        '60': '60',
      },
      colors: {
        // TRUE ASTRO-NUMEROLOGY COLORS
        // Based on: Sun(1)-Naman, Saturn(8)-Lekha/Naman/RNRL, Mars(9)-Rajkumar
        
        // SUN (1) - Naman Life Path - PRIMARY GOLD
        sun: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B', // Pure Sun Gold
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
        
        // SATURN (8) - Lekha, Naman Birth, RNRL - DEEP SAPPHIRE
        saturn: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#1E40AF', // Deep Saturn Blue
          600: '#1E3A8A',
          700: '#1E3A8A',
          800: '#1E3A8A',
          900: '#172554',
        },
        
        // MARS (9) - Rajkumar Life Path - BURGUNDY
        mars: {
          50: '#FDF2F8',
          100: '#FCE7F3',
          200: '#FBCFE8',
          300: '#F9A8D4',
          400: '#F472B6',
          500: '#9F1239', // Deep Mars Burgundy
          600: '#881337',
          700: '#6F1732',
          800: '#5C122A',
          900: '#4A0E22',
        },
        
        // Supporting colors
        pearl: {
          50: '#FFFFFF',
          100: '#FAFAFA',
          200: '#F5F5F5',
          300: '#E5E5E5',
          400: '#D4D4D4',
          500: '#E8E4DC', // Pearl White
          600: '#C4C0B8',
          700: '#A09C94',
          800: '#7C7870',
          900: '#58544C',
        },
        
        // Legacy colors for compatibility
        space: {
          DEFAULT: '#0A1128',
          50: '#E8EAF0',
          100: '#C5C9D9',
          200: '#A2A8C2',
          300: '#7F87AB',
          400: '#5C6694',
          500: '#3A4570',
          600: '#2F3A5F',
          700: '#253055',
          800: '#1A2642',
          900: '#0F1830',
        },
        
        // Trading Colors
        buy: {
          DEFAULT: '#00C853',
          light: '#66BB6A',
          dark: '#00B248',
        },
        sell: {
          DEFAULT: '#DC143C',
          light: '#EF5350',
          dark: '#C91134',
        },
      },
      
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #006B7D 0%, #004D5C 100%)',
        'gradient-gold': 'linear-gradient(135deg, #D4AF37 0%, #BF9B2E 100%)',
        'gradient-ai': 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
        'glass': 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
      },
      
      backdropBlur: {
        'glass': '20px',
      },
      
      animation: {
        'price-flash': 'flash 400ms ease-out',
      },
      
      keyframes: {
        flash: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
}
