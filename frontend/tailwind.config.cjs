/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#10b981'
        }
      },
      fontFamily: {
        display: ['"Instrument Serif"', 'serif'],
      },
      borderRadius: {
        'xl2': '1rem',
      }
    },
  },
  plugins: [],
}
