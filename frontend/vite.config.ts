import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Gera sourcemaps apenas em dev; em prod mantém bundle limpo
    sourcemap: false,
    // Tamanho mínimo para considerar um chunk como "grande" (kB)
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        // Code-splitting manual: separa vendors pesados do código da aplicação
        manualChunks: {
          react: ["react", "react-dom"],
          router: ["react-router-dom"],
          ui: [
            "@radix-ui/react-accordion",
            "@radix-ui/react-collapsible",
            "@radix-ui/react-dialog",
            "@radix-ui/react-dropdown-menu",
            "@radix-ui/react-hover-card",
            "@radix-ui/react-label",
            "@radix-ui/react-navigation-menu",
            "@radix-ui/react-progress",
            "@radix-ui/react-select",
            "@radix-ui/react-separator",
            "@radix-ui/react-slot",
            "@radix-ui/react-tabs",
            "@radix-ui/react-tooltip",
          ],
        },
        // Nomes de chunk previsíveis para melhor cache HTTP
        chunkFileNames: "assets/[name]-[hash].js",
        entryFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
    // Minificação avançada com esbuild (padrão e rápida)
    minify: "esbuild",
    // Remove console.log e debugger em produção
    esbuildOptions: {
      drop: ["console", "debugger"],
    },
    // Compressão CSS
    cssMinify: true,
  },
  // Garante caminhos corretos no Railway (sem subpath)
  base: "/",
})
