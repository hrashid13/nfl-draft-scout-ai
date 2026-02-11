/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Your custom color palette
        wheat: '#F8DEB5',
        'blue-slate': {
          DEFAULT: '#4E717E',
          50: '#E8EDEF',
          100: '#D1DBE0',
          200: '#A3B7C1',
          300: '#7593A2',
          400: '#476F83',
          500: '#4E717E',
          600: '#3E5A65',
          700: '#2F444C',
          800: '#1F2D32',
          900: '#101719',
        },
        'dark-amethyst': {
          DEFAULT: '#100A33',
          50: '#3A2F7A',
          100: '#2F2563',
          200: '#251B4D',
          300: '#1A1136',
          400: '#150C30',
          500: '#100A33',
          600: '#0C082A',
          700: '#080521',
          800: '#040318',
          900: '#00010F',
        },
        evergreen: {
          DEFAULT: '#132B1F',
          50: '#3D7D5E',
          100: '#316850',
          200: '#255342',
          300: '#193E34',
          400: '#163529',
          500: '#132B1F',
          600: '#0F2219',
          700: '#0B1913',
          800: '#07100D',
          900: '#030706',
        },
        'molten-lava': {
          DEFAULT: '#711B09',
          50: '#F5A488',
          100: '#F3937A',
          200: '#EE725E',
          300: '#E95142',
          400: '#D63726',
          500: '#711B09',
          600: '#5A1507',
          700: '#431005',
          800: '#2C0A03',
          900: '#150501',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #132B1F 0%, #1a2d33 60%, #100A33 100%)',
        'gradient-card': 'linear-gradient(135deg, #132B1F 0%, #4E717E 100%)',
        'gradient-button': 'linear-gradient(135deg, #711B09 0%, #5A1507 100%)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}