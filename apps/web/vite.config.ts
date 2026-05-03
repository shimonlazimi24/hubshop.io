import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/** Used by `vite` dev server and `vite preview` (Railway). Prefer `VITE_API_URL` on the web service so SPA + proxy match. */
const apiProxyTarget =
  process.env.VITE_API_PROXY ??
  process.env.VITE_API_URL ??
  "http://localhost:8001";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
  // Railway (and other PaaS) assigns a public hostname for `vite preview`; Vite 6 blocks unknown Host headers by default.
  preview: {
    allowedHosts: true,
    proxy: {
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
});
