import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  // Базовый префикс для ассетов в прод-сборке, чтобы они запрашивались как /static/front/...
  base: '/static/front/',
  plugins: [react(), tsconfigPaths(), tailwindcss()],
  // ДОБАВЛЕНО: dev-сервер Vite с прокси на Django (API, admin, WebSocket)
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
