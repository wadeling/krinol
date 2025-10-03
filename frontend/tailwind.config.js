/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  safelist: [
    'bg-white',
    'bg-slate-50',
    'bg-slate-100',
    'bg-slate-200',
    'bg-slate-300',
    'bg-slate-400',
    'bg-slate-500',
    'bg-slate-600',
    'bg-slate-700',
    'bg-slate-800',
    'bg-slate-900',
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        sky: {
          100: '#e0f2fe',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
        },
        emerald: {
          100: '#dcfce7',
          500: '#10b981',
        },
        amber: {
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          500: '#f59e0b',
          800: '#92400e',
          900: '#78350f',
        },
        rose: {
          100: '#ffe4e6',
          500: '#f43f5e',
        },
        violet: {
          400: '#a78bfa',
        },
        orange: {
          500: '#f97316',
        },
        green: {
          100: '#dcfce7',
          500: '#22c55e',
          800: '#166534',
        },
        blue: {
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          800: '#1e40af',
        },
        yellow: {
          100: '#fef3c7',
          800: '#92400e',
        },
        red: {
          100: '#fee2e2',
          500: '#ef4444',
          800: '#991b1b',
        },
      },
      fontFamily: {
        sans: ['Helvetica Neue', 'Helvetica', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.03)',
        'soft-lg': '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
      },
    },
  },
  plugins: [],
}
