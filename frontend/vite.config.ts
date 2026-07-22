import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Разрешает доступ извне
    port: 5173,
    strictPort: true,
    allowedHosts: ['d17876ce249ab3.lhr.life', '.lhr.life'], // <-- ВАЖНО: Разрешаем домены localhost.run
    proxy: {
      // Все запросы к /api/ перенаправляем на Django
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Перенаправляем медиафайлы на Django
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
})