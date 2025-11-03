import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendUrls = {
  local: "http://localhost:8000",
  local127: "http://127.0.0.1:8000",
  dev: "https://dev.api.smart-hr-bot.com",
  test: "https://test.api.smart-hr-bot.com",
  prod: "https://api.smart-hr-bot.com",
};

const activeBackend = backendUrls.local;

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: activeBackend,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, "/api"),
      },
    },
  },
});
