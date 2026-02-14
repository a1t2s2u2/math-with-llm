export default defineNuxtConfig({
  compatibilityDate: '2024-01-27',
  devtools: { enabled: true },
  modules: ['@vite-pwa/nuxt'],

  typescript: {
    strict: true,
    typeCheck: false
  },

  app: {
    head: {
      meta: [
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        {
          name: 'apple-mobile-web-app-status-bar-style',
          content: 'black-translucent'
        },
        { name: 'theme-color', content: '#1e1e1e' },
        {
          name: 'viewport',
          content:
            'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover'
        }
      ],
      link: [
        {
          rel: 'apple-touch-icon',
          href: '/apple-touch-icon.png',
          sizes: '180x180'
        }
      ]
    }
  },

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Math with LLM',
      short_name: 'MathLLM',
      display: 'standalone',
      theme_color: '#1e1e1e',
      background_color: '#1e1e1e',
      icons: [
        {
          src: '/icon-192x192.png',
          sizes: '192x192',
          type: 'image/png'
        },
        {
          src: '/icon-512x512.png',
          sizes: '512x512',
          type: 'image/png'
        },
        {
          src: '/icon-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable'
        }
      ]
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff2}'],
      runtimeCaching: [
        {
          urlPattern: /^https?:\/\/.*\/api\/.*/i,
          handler: 'NetworkOnly' as const
        }
      ]
    },
    devOptions: {
      enabled: true
    }
  },

  vite: {
    server: {
      proxy: {
        '/api': {
          target: process.env.BACKEND_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path: string) => path.replace(/^\/api/, '')
        }
      }
    },
    optimizeDeps: {
      esbuildOptions: {
        loader: {
          '.keep': 'empty'
        }
      }
    }
  },

  css: ['~/assets/css/main.css', 'katex/dist/katex.min.css']
})
