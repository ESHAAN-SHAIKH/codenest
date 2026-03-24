/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FF6B6B', // Red/Coral
          light: '#FF8787',
          dark: '#FA5252',
        },
        secondary: {
          DEFAULT: '#4DABF7', // Blue
          light: '#74C0FC',
          dark: '#339AF0',
        },
        success: '#69DB7C',
        warning: '#FCC419',
        error: '#FF8787',
        background: '#F8F9FA',
        surface: '#FFFFFF',
      },
      fontFamily: {
        sans: ['"Comic Neue"', 'cursive', 'sans-serif'], // Kid-friendly font
      }
    },
  },
  plugins: [],
}
