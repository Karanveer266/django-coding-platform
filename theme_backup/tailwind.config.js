/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './../theme/templates/**/*.html',
    './../users/templates/**/*.html',
    './../problems/templates/**/*.html',
    './../blogs/templates/**/*.html',
    './../submit/templates/**/*.html',
    './../learning_sessions/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}