import { defineConfig } from 'vite'


// https://vite.dev/config/
export default defineConfig({
  base: './',
  build: {
    outDir: '../public', // Render looks for this
    emptyOutDir: true,
  },
})
