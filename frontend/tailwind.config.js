/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // MTN MoMo brand colors: yellow #FFCC00 on black/near-black.
        // brand-500 is the core MoMo yellow — always paired with black text,
        // never used as text color on a light background (poor contrast).
        brand: {
          50: "#fffdf0",
          100: "#fff8d6",
          200: "#ffefa3",
          300: "#ffe670",
          400: "#ffd633",
          500: "#FFCC00",
          600: "#e6b800",
          700: "#cc9f00",
          800: "#997700",
          900: "#664f00",
        },
        ink: {
          // near-black surfaces used for the sidebar / header, matching MoMo's
          // black-and-yellow look rather than a pure #000 which is harsher on screen.
          900: "#0d0d0d",
          800: "#1a1a1a",
          700: "#262626",
          600: "#333333",
        },
      },
    },
  },
  plugins: [],
}
