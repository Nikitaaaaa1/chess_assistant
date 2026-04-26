/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'board-green': '#769656',
        'board-white': '#eeeed2',
      }
    },
  },
  plugins: [],
}
