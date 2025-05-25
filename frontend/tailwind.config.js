
const colors = require('./colorSchema.ts');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'app-bg': colors.background,
        'app-primary': colors.primary,
        'app-accent': colors.accent,
        'app-text': colors.text,
        'app-danger': colors.danger,
        'app-secondary': colors.secondary,


        custom: colors,
      },

      backgroundColor: {
        'app': '#0f0f1a',
      },

      textColor: {
        'app': '#E5E7EB',
      }
    },
  },
  plugins: [],
}