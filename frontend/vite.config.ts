import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Define all possible backend URLs
const backendUrls = {
  local: "http://localhost:8000",
  local127: "http://127.0.0.1:8000",
  dev: "https://dev.api.smart-hr-bot.com",
  test: "https://test.api.smart-hr-bot.com",
  prod: "https://api.smart-hr-bot.com",
}

const activeBackend = backendUrls.local // change this to local127, dev, test, prod when needed

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: activeBackend,
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
