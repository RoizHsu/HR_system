// src/main.js
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import router from './router' // 引入 router路由設定

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')