import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const proxyTarget =
    env.VITE_DEV_PROXY_TARGET?.trim() || 'http://127.0.0.1:8001'

  const apiProxy = {
    '/api': {
      target: proxyTarget,
      changeOrigin: true,
    },
  } as const

  return {
    plugins: [react()],
    server: {
      port: Number(env.VITE_DEV_PORT) || 5173,
      proxy: { ...apiProxy },
      allowedHosts: env.VITE_ALLOWED_HOSTS
        ? env.VITE_ALLOWED_HOSTS.split(',').map((h: string) => h.trim())
        : [],
    },
    preview: {
      proxy: { ...apiProxy },
    },
  }
})
