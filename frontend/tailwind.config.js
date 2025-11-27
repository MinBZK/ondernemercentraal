/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}', './src/formkit.theme.ts', // <-- add your theme file
  ],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [import('tailwindcss-primeui')],
}
