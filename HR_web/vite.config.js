import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',// 監聽所有網絡介面 讓vite在所有網絡接口上監聽，這樣其他設備就可以通過IP地址訪問你的開發服務器
    port: 5173,
  },
})
