/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0b0e17',
        surface: '#121624',
        card: '#121624',
        elevated: '#1a2030',
        border: '#232b3e',

        obsidian: {
          base: '#0b0e17',
          surface: '#0f131d',
          card: '#121624',
          elevated: '#1a2030',
          border: '#232b3e',
          borderLight: '#313540',
        },

        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },

        ai: {
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
        },

        primary: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          dim: '#c0c1ff',
          container: '#8083ff',
        },
        indigo: {
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
        purple: {
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        },
        amber: {
          500: '#f59e0b',
        },
        rose: {
          500: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        heading: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      }
    },
  },
  plugins: [],
};
