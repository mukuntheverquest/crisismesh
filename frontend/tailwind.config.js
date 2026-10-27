/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        crisis: {
          50: '#fef7f7',
          100: '#fdeaea',
          200: '#fbd5d5',
          300: '#f8b4b4',
          400: '#f48787',
          500: '#ef5353',
          600: '#e02424',
          700: '#c01818',
          800: '#9e1616',
          900: '#821717',
        },
        alert: {
          50: '#fff8ed',
          100: '#ffefd0',
          200: '#ffdfa1',
          300: '#ffcc6b',
          400: '#ffb338',
          500: '#ff9900',
          600: '#e67700',
          700: '#cc5c00',
          800: '#a64700',
          900: '#853800',
        },
        safe: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}