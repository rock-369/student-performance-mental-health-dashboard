import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => ({
  plugins: [react()],

  // Development server config
  server: {
    port: 3000,
    host: true, // Listen on all addresses
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },

  // Preview server (for production builds)
  preview: {
    port: 4173,
    host: true
  },

  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: mode === 'development',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks for better caching
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'chart-vendor': ['recharts'],
          'icons-vendor': ['lucide-react']
        }
      }
    },
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000
  },

  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
  }
}))
