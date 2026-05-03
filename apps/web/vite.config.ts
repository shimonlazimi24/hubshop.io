import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

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
        target: process.env.VITE_API_PROXY ?? "http://localhost:8001",
        changeOrigin: true,
      },
    },
  },
  // Railway (and other PaaS) assigns a public hostname for `vite preview`; Vite 6 blocks unknown Host headers by default.
  preview: {
    allowedHosts: true,
  },
});
