import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
// Proxy target is env-driven: BACKEND_URL (or VITE_API_URL) -> default localhost:8000.
// Frontend API base is VITE_API_URL (see src/api.js): "" = relative/proxy, else direct.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget =
    env.BACKEND_URL || env.VITE_BACKEND_URL || env.VITE_API_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: Number(env.FRONTEND_PORT || env.VITE_PORT || 5173),
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
