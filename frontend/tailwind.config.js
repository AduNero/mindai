/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f4ff",
          100: "#dce4ff",
          200: "#bac9ff",
          300: "#8fa5ff",
          400: "#6b83fa",
          500: "#4f5fee",
          600: "#3f45d1",
          700: "#3436a8",
          800: "#2c2f84",
          900: "#282a68",
        },
        wellness: {
          low: "#ef4444",
          moderate: "#f59e0b",
          good: "#10b981",
          excellent: "#0ea5e9",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
