import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        steel: "#475569",
        line: "#d7dee8",
        panel: "#f8fafc",
        safe: "#047857",
        warn: "#b45309",
        danger: "#b91c1c"
      }
    }
  },
  plugins: []
};

export default config;
