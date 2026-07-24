/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          200: "#bcd2ff",
          300: "#8eb4ff",
          400: "#598cff",
          500: "#3366ff",
          600: "#1f47e6",
          700: "#1a38b8",
          800: "#1a3193",
          900: "#1a2e74",
        },
      },
    },
  },
  plugins: [],
};
