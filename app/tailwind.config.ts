import type { Config } from "tailwindcss";

// Palette from FUNNEL.md 2.1 (the characters' world). There is deliberately NO gray
// in this theme: every text colour is Ink, Rice or Paper. Tailwind's default gray
// scales are removed so nobody can reach for text-gray-500 by accident.
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      paper: "#FBF6EC",
      ink: "#16120E",
      persimmon: { DEFAULT: "#B3311C", dark: "#8E2514" },
      jade: { DEFAULT: "#1F5A46", dark: "#143D30", light: "#DDEBE3" },
      rice: "#FFFFFF",
      brass: "#E7B85A",
      cream: "#F3E9D6",
      alert: "#7A1206",
    },
    fontFamily: {
      display: ['"Fraunces Variable"', "Georgia", "serif"],
      sans: ['"Atkinson Hyperlegible"', "system-ui", "sans-serif"],
    },
    extend: {
      fontSize: {
        fine: ["17px", { lineHeight: "1.5" }],
        base: ["20px", { lineHeight: "1.55" }],
        lg: ["22px", { lineHeight: "1.5" }],
        xl: ["26px", { lineHeight: "1.35" }],
        "2xl": ["30px", { lineHeight: "1.25" }],
        "3xl": ["36px", { lineHeight: "1.18" }],
        "4xl": ["40px", { lineHeight: "1.12" }],
        "5xl": ["52px", { lineHeight: "1.08" }],
        "6xl": ["60px", { lineHeight: "1.05" }],
      },
      maxWidth: { prose: "62ch" },
      borderRadius: { btn: "14px" },
      minHeight: { btn: "60px" },
    },
  },
  plugins: [],
};
export default config;
