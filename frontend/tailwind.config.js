/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // ISA-101 muted operational surface
        surface: {
          950: "#0b0f16",
          900: "#0f1420",
          850: "#151b28",
          800: "#1b2333",
          700: "#243044",
          600: "#31405a",
        },
        // RYG reserved strictly for operational status
        status: {
          red: "#ef4444",
          "red-dim": "#7f1d1d",
          yellow: "#f59e0b",
          "yellow-dim": "#78350f",
          green: "#10b981",
          "green-dim": "#064e3b",
          gray: "#64748b",
        },
        biotech: {
          accent: "#38bdf8",
          teal: "#2dd4bf",
        },
      },
      keyframes: {
        flow: {
          to: { "stroke-dashoffset": "-24" },
        },
        pulseNode: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
        breathe: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.9" },
          "50%": { transform: "scale(1.15)", opacity: "0.5" },
        },
      },
      animation: {
        flow: "flow 1s linear infinite",
        "pulse-node": "pulseNode 1.6s ease-in-out infinite",
        breathe: "breathe 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
}
