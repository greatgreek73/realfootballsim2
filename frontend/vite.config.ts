import { defineConfig } from "vite";
import path from "node:path";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? '/static/front/' : '/',
  plugins: [react(), tsconfigPaths(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api':   { target: 'http://127.0.0.1:8000', changeOrigin: true }, // ← ТАК
      '/admin': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/static':{ target: 'http://127.0.0.1:8000', changeOrigin: true }, // <— добавили
      '/media': { target: 'http://127.0.0.1:8000', changeOrigin: true }, // <— добавили
      '/players': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ws':    { target: 'ws://127.0.0.1:8000', ws: true, changeOrigin: true },
    },
  },
});
