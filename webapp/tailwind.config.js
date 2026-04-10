/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#000000',
          secondary: '#1C1C1E',
          tertiary: '#2C2C2E',
        },
        accent: {
          red: '#FF3B30',
          green: '#34C759',
          blue: '#007AFF',
          cyan: '#00D4AA',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#8E8E93',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'system-ui',
          'Segoe UI',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}
