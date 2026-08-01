/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#050A14",
        surface: "#0D1B2A",
        elevated: "#1A2744",
        border: "#1E2D45",
        accent: "#2563EB",
        "accent-soft": "#3B82F6",
        success: "#10B981",
        danger: "#EF4444",
        warning: "#F59E0B",
        muted: "#94A3B8",
        ink: "#F1F5F9",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      animation: {
        "pulse-line": "pulse-line 3s ease-in-out infinite",
        "fade-in": "fade-in 0.4s ease-out",
        "slide-up": "slide-up 0.3s ease-out",
      },
      keyframes: {
        "pulse-line": {
          "0%, 100%": { opacity: 0.4 },
          "50%": { opacity: 1 },
        },
        "fade-in": {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        "slide-up": {
          from: { opacity: 0, transform: "translateY(8px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
}
