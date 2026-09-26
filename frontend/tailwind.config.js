/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eefcf3",
          100: "#d6f7e2",
          500: "#0f9d58",
          600: "#0c8148",
          700: "#0a6a3c",
          900: "#053a20",
        },
      },
    },
  },
  plugins: [],
}
