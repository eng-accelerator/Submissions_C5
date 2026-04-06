/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4ff',
          100: '#dce6ff',
          200: '#b9ccff',
          300: '#84a9ff',
          400: '#4d7eff',
          500: '#1a56ff',
          600: '#0038f5',
          700: '#002de0',
          800: '#0026b5',
          900: '#00218e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
