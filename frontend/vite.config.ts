import { fileURLToPath, URL } from "node:url";

import { defineConfig, type PluginOption } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";
import { visualizer } from "rollup-plugin-visualizer";

// https://vitejs.dev/config/

export default defineConfig({
  // plugins: [vue(), vueJsx(), visualizer() as PluginOption],
  plugins: [vue(), vueJsx()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 3000,
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          chart: ["echarts"],
          vue: ["vue", "vue-router", "pinia", "@vueuse/core", "vue-i18n"],
          jspdf: ["jspdf"],
          lodash: ["lodash"],
          "vxe-table": ["vxe-table"],
          element: ["element-plus"],
        },
      },
    },
  },
});
