/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          primary:  '#0A0A0F',
          secondary: '#161B26',
          elevated:  '#1D2334',
          tertiary:  '#252B3B',
        },
        accent: {
          red:    '#FF3B30',
          green:  '#30D158',
          blue:   '#0A84FF',
          cyan:   '#00D4C8',
          orange: '#FF9500',
        },
        text: {
          primary:   '#FFFFFF',
          secondary: '#8E8E93',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'system-ui', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
