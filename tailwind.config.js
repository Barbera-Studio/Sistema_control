// tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './static/css/**/*.css'
  ],
  theme: {
    extend: {
      animation: {
        neonGlow: 'neonGlow 2s infinite',
        pulseBorder: 'pulseBorder 3s infinite',
        gradientShift: 'gradientShift 8s ease infinite',
      },
      keyframes: {
        neonGlow: {
          '0%, 100%': {
            textShadow: '0 0 8px #00f0ff, 0 0 20px #00e5ff, 0 0 40px #00d4ff',
          },
          '50%': {
            textShadow: '0 0 4px #00f0ff, 0 0 12px #00e5ff, 0 0 24px #00d4ff',
          },
        },
        pulseBorder: {
          '0%, 100%': {
            boxShadow: '0 0 15px #00f0ff, 0 0 40px #0066ff inset',
          },
          '50%': {
            boxShadow: '0 0 25px #00e5ff, 0 0 50px #0088ff inset',
          },
        },
        gradientShift: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
      },
      backgroundSize: {
        '600': '600% 600%',
      },
      dropShadow: {
        neon: '0 0 30px rgba(0,255,255,0.7)',
      },
      boxShadow: {
        orbital: '0 0 80px rgba(0,255,255,0.3)',
      },
      borderRadius: {
        '3xl': '1.5rem',
      },
    },
  },
  plugins: [],
}

