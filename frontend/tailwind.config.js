/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // "Instrument panel" direction — a deep pine/teal instead of the
        // generic indigo-to-violet every AI SaaS app defaults to. See
        // DESIGN.md for the full rationale.
        brand: {
          50: "#f0f7f5",
          100: "#dbeae5",
          200: "#b8d6cc",
          300: "#8dbcad",
          400: "#5f9d8b",
          500: "#3d7d6c",
          600: "#2f6456",
          700: "#275145",
          800: "#204339",
          900: "#1c3830",
        },
        // Warm paper neutrals for page/card backgrounds — deliberately not
        // stark white or cold gray. Body text/borders still use Tailwind's
        // default gray scale (reads fine against a warm ground); this is
        // just the ground itself.
        paper: {
          50: "#faf8f4",
          100: "#f3efe7",
          900: "#1c1a17",
          950: "#131210",
        },
        wellness: {
          low: "#ef4444",
          moderate: "#f59e0b",
          good: "#10b981",
          excellent: "#0ea5e9",
        },
      },
      fontFamily: {
        // IBM Plex: designed for technical/data-dense enterprise software —
        // a genuine fit for "instrument panel for your own longitudinal
        // data," not an arbitrary swap. Mono carries every number in the
        // product (scores, chart labels, stats) so they read as readings,
        // not just bold text.
        sans: ["IBM Plex Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"],
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
