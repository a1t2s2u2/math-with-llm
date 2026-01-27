export default defineNuxtConfig({
  compatibilityDate: '2024-01-27',
  devtools: { enabled: true },

  typescript: {
    strict: true,
    typeCheck: false
  },

  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://backend:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  },

  css: ['~/assets/css/main.css']
})
