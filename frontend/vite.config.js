import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    },
    watch: {
      // 编辑器/工具写入时的临时目录会触发 EBUSY，直接忽略
      ignored: ['**/.*.tmpdir/**', '**/*.tmp', '**/.*.tmp']
    }
  }
})
