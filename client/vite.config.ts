import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, "..", "");
  return {
    plugins: [react()],
    envDir: "..",
    envPrefix: "pigeon",
    server: {
      port: 5173,
      host: true,
      proxy: {
        "/api": {
          target: env.BACKEND_URL_DOCKER,
          changeOrigin: true,
        },
      },
    },
  };
});
