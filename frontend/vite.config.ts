import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { PrimeVueResolver } from '@primevue/auto-import-resolver'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    AutoImport({
      imports: ['vue', 'vue-router', 'vue-i18n'],
      dirs: ['./src/composables/**', './src/views/**', './src/pages/**'],
    }),
    tailwindcss(),
    vue(),
    vueDevTools({
      launchEditor: process.env.VITE_EDITOR || 'code',
    }),
    Components({
      dirs: ['src/components', 'src/views', 'src/pages'],
      resolvers: [PrimeVueResolver()],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
