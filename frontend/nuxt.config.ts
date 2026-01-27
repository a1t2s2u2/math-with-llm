export default defineNuxtConfig({
  compatibilityDate: '2024-01-27',
  devtools: { enabled: true },

  typescript: {
    strict: true,
    typeCheck: true
  },

  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  },

  css: ['~/assets/css/main.css']
})
