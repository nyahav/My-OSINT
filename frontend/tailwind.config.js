
const colors = require('./colorSchema.ts');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Import colors directly from your schema
        'app-bg': colors.background,
        'app-primary': colors.primary,
        'app-accent': colors.accent,
        'app-text': colors.text,
        'app-danger': colors.danger,
        'app-secondary': colors.secondary,
        
        // Or import the entire object
        custom: colors,
      },
      // Optional: Add custom background colors for easier usage
      backgroundColor: {
        'app': '#0f0f1a',
      },
      // Optional: Add custom text colors for easier usage
      textColor: {
        'app': '#E5E7EB',
      }
    },
  },
  plugins: [],
}