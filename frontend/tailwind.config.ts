import type { Config } from "tailwindcss";
import { setupInspiraUI } from "@inspira-ui/plugins";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px"
      }
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))"
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))"
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)"
      },
      keyframes: {
        "border-beam": {
          "100%": {
            "offset-distance": "100%"
          }
        },
        meteor: {
          "0%": { transform: "rotate(215deg) translateX(0)", opacity: "1" },
          "70%": { opacity: "1" },
          "100%": { transform: "rotate(215deg) translateX(-500px)", opacity: "0" }
        },
        shimmer: {
          "0%, 90%, 100%": {
            "background-position": "calc(-100% - var(--shimmer-width)) 0"
          },
          "30%, 60%": {
            "background-position": "calc(100% + var(--shimmer-width)) 0"
          }
        },
        marquee: {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(calc(-100% - var(--gap, 1rem)))" }
        },
        "gradient-text": {
          "0%, 100%": {
            "background-size": "200% auto",
            "background-position": "0% center"
          },
          "50%": {
            "background-size": "200% auto",
            "background-position": "100% center"
          }
        },
        aurora: {
          from: {
            backgroundPosition: "50% 50%, 50% 50%"
          },
          to: {
            backgroundPosition: "350% 50%, 350% 50%"
          }
        }
      },
      animation: {
        "border-beam": "border-beam calc(var(--duration)*1s) infinite linear",
        meteor: "meteor 5s linear infinite",
        shimmer: "shimmer 8s infinite",
        marquee: "marquee var(--duration, 25s) linear infinite",
        "gradient-text": "gradient-text 4s ease infinite",
        aurora: "aurora 60s linear infinite"
      }
    }
  },
  plugins: [setupInspiraUI]
};

export default config;
