import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, /api/* is forwarded to your FastAPI server, so no CORS setup is needed.
// Override with: API_URL=http://host:port npm run dev
const target = process.env.API_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
        timeout: 120000,
        proxyTimeout: 120000,
      },
    },
  },
});
