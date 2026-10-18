/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Legal Intelligence Workbench Design Tokens
        midnight: {
          DEFAULT: '#0C182A', // Deep midnight navy
          light: '#162744',
          surface: '#11213A',
          dark: '#070E1A',
        },
        ivory: {
          DEFAULT: '#FBFBF9', // Warm ivory page background
          surface: '#FFFFFF', // Clean white component surface
          subtle: '#F4F4EE',  // Subtle parchment tone
          dark: '#EAEAE2',
        },
        crimson: {
          DEFAULT: '#8B1E3F', // Legal burgundy / crimson
          hover: '#731633',
          light: '#A8254D',
          subtle: '#FDF2F4',
        },
        gold: {
          DEFAULT: '#C5A880', // Muted antique gold
          dark: '#9E7D47',
          light: '#DCC3A1',
          subtle: '#FAF6F0',
        },
        charcoal: {
          DEFAULT: '#1C232B', // High-contrast primary text
          body: '#333F4D',    // Paragraph / body text
          muted: '#64748B',   // Labels / secondary captions
          subtle: '#94A3B8',  // Placeholders / borders
        },
        line: {
          DEFAULT: '#E2E8F0', // Refined divider lines
          dark: '#CBD5E1',
          warm: '#E4DFD5',
        },
        legalgreen: {
          DEFAULT: '#2E7D32',
          subtle: '#EDF7ED',
          border: '#C8E6C9',
        },
        legalamber: {
          DEFAULT: '#D97706',
          subtle: '#FFFBEB',
          border: '#FDE68A',
        },
        legalred: {
          DEFAULT: '#C53030',
          subtle: '#FEF2F2',
          border: '#FECACA',
        },
        // Backwards compatibility with previous legal-* token usages
        legal: {
          navy: {
            DEFAULT: '#0C182A',
            light: '#162744',
            dark: '#070E1A',
          },
          parchment: {
            DEFAULT: '#FBFBF9',
            light: '#FFFFFF',
            dark: '#F4F4EE',
            muted: '#EAEAE2',
          },
          burgundy: {
            DEFAULT: '#8B1E3F',
            hover: '#731633',
            light: '#A8254D',
            subtle: '#FDF2F4',
          },
          gold: {
            DEFAULT: '#C5A880',
            light: '#DCC3A1',
            subtle: '#FAF6F0',
          },
          charcoal: {
            DEFAULT: '#1C232B',
            muted: '#64748B',
            subtle: '#94A3B8',
          },
          border: {
            DEFAULT: '#E2E8F0',
            dark: '#CBD5E1',
            warm: '#E4DFD5',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['"Source Serif 4"', 'Merriweather', 'Georgia', 'serif'],
        serif: ['"Source Serif 4"', 'Merriweather', 'Georgia', 'serif'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        'elevated': '0 4px 6px -1px rgba(12, 24, 42, 0.05), 0 2px 4px -2px rgba(12, 24, 42, 0.05)',
        'modal': '0 20px 25px -5px rgba(12, 24, 42, 0.1), 0 8px 10px -6px rgba(12, 24, 42, 0.1)',
      }
    },
  },
  plugins: [],
}
