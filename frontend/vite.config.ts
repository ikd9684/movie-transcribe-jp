import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/movie-transcribe/',
  server: {
    proxy: {
      '/movie-transcribe/api': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/movie-transcribe/, ''),
        changeOrigin: true,
      },
    },
  },
})
