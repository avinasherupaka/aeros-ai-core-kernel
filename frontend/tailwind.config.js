/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Balanced enterprise light theme (ISA-101 + modern SaaS).
        app: "#f5f6f8",        // application canvas
        panel: "#ffffff",       // cards / panels
        panel2: "#f1f5f9",      // subtle inset surface
        panel3: "#e8edf3",      // deeper inset / headers
        line: "#e2e8f0",        // hairline borders
        line2: "#cbd5e1",       // stronger borders
        ink: "#0f172a",         // primary text (slate-900)
        ink2: "#334155",        // body text (slate-700)
        ink3: "#64748b",        // muted text (slate-500)
        brand: {
          DEFAULT: "#4f46e5",   // indigo-600 primary accent
          hover: "#4338ca",
          soft: "#eef2ff",      // indigo-50 tint
          ring: "#c7d2fe",
        },
        // RYG reserved strictly for operational status (accessible on light).
        status: {
          red: "#dc2626",
          "red-soft": "#fef2f2",
          "red-line": "#fecaca",
          amber: "#d97706",
          "amber-soft": "#fffbeb",
          "amber-line": "#fde68a",
          green: "#059669",
          "green-soft": "#ecfdf5",
          "green-line": "#a7f3d0",
          neutral: "#94a3b8",     // unknown / not evaluated
          "neutral-soft": "#f1f5f9",
        },
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06)",
        raised: "0 4px 12px rgba(15,23,42,0.08)",
        float: "0 8px 30px rgba(15,23,42,0.16)",
      },
      keyframes: {
        flow: { to: { "stroke-dashoffset": "-24" } },
        pulseNode: { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.4" } },
        breathe: { "0%, 100%": { transform: "scale(1)", opacity: "0.9" }, "50%": { transform: "scale(1.18)", opacity: "0.5" } },
        slideUp: { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
      },
      animation: {
        flow: "flow 1s linear infinite",
        "pulse-node": "pulseNode 1.8s ease-in-out infinite",
        breathe: "breathe 2s ease-in-out infinite",
        "slide-up": "slideUp 0.16s ease-out",
      },
    },
  },
  plugins: [],
}
