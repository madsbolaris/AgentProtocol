/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0066cc',
        success: '#00a000',
        warning: '#ff8c00',
        danger: '#cc0000',
        info: '#0099cc',
      },
    },
  },
  plugins: [],
}
