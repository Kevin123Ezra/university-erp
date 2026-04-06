import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/web": {
        target: "http://localhost:8069",
        changeOrigin: true,
      },
      "/uni": {
        target: "http://localhost:8069",
        changeOrigin: true,
      },
    },
  },
});
