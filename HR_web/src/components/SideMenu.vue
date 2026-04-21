<template>
  <div class="side-menu">
    <!-- 漢堡菜單按鈕 -->
    <button class="menu-toggle" @click="isOpen = !isOpen" :class="{ active: isOpen }">
      <span></span>
      <span></span>
      <span></span>
    </button>

    <!-- 側邊菜單 -->
    <nav class="menu-sidebar" :class="{ open: isOpen }">
      <div class="menu-header">
        <h3>菜單</h3>
        <button class="close-btn" @click="isOpen = false">×</button>
      </div>

      <ul class="menu-list">
        <!-- 回首頁 - 所有人都有 -->
        <li>
          <router-link to="/" @click="isOpen = false" class="menu-link">
            <span class="icon">🏠</span>
            <span>回首頁</span>
          </router-link>
        </li>

        <!-- 已登入才顯示 -->
        <li v-if="isLoggedIn">
          <router-link to="/personal" @click="isOpen = false" class="menu-link">
            <span class="icon">👤</span>
            <span>個人資料</span>
          </router-link>
        </li>

        <!-- 分隔線 -->
        <li v-if="isLoggedIn" class="menu-divider"></li>

        <!-- 登出按鈕 - 已登入才顯示 -->
        <li v-if="isLoggedIn">
          <button @click="handleLogout" class="menu-link logout-btn">
            <span class="icon">🚪</span>
            <span>登出</span>
          </button>
        </li>
      </ul>
    </nav>

    <!-- 遮罩層 -->
    <div v-if="isOpen" class="menu-overlay" @click="isOpen = false"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from '../api'

const router = useRouter()
const isOpen = ref(false)

const employee = ref(null)

const isLoggedIn = computed(() => !!employee.value)

const handleLogout = async () => {
  try {
    await api.post('employees/auth/logout/')
  } catch (err) {
    console.error(err)
  }
  setAuthToken(null)
  localStorage.removeItem('hr_employee')
  employee.value = null
  isOpen.value = false
  ElMessage.success('已登出')
  router.push('/')
}

// 從 localStorage 初始化員工資訊
const loadEmployee = () => {
  const stored = localStorage.getItem('hr_employee')
  if (stored) {
    employee.value = JSON.parse(stored)
  }
}

// 監聽登入狀態變化
const checkAuthStatus = () => {
  const token = localStorage.getItem('hr_token')
  if (!token) {
    employee.value = null
  } else {
    loadEmployee()
  }
}

// 初始化
loadEmployee()

// 監聽 storage 變化
window.addEventListener('storage', checkAuthStatus)
</script>

<style scoped>
.side-menu {
  position: relative;
}

/* 漢堡菜單按鈕 */
.menu-toggle {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 44px;
  height: 44px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  z-index: 1000;
  padding: 0;
  transition: all 0.3s ease;
}

.menu-toggle span {
  width: 24px;
  height: 2.5px;
  background: #333;
  border-radius: 2px;
  transition: all 0.3s ease;
  display: block;
}

.menu-toggle.active span:nth-child(1) {
  transform: translateY(7.5px) rotate(45deg);
}

.menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.menu-toggle.active span:nth-child(3) {
  transform: translateY(-7.5px) rotate(-45deg);
}

/* 側邊菜單 */
.menu-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 280px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 999;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.menu-sidebar.open {
  transform: translateX(0);
}

.menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.menu-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #111827;
}

.menu-list {
  list-style: none;
  padding: 8px 0;
  margin: 0;
  flex: 1;
}

.menu-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #374151;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  width: 100%;
  text-align: left;
  transition: all 0.2s;
  font-family: inherit;
}

.menu-link:hover {
  background: #f3f4f6;
  color: #111827;
}

.menu-link.router-link-active {
  background: #e5e7eb;
  color: #667eea;
  font-weight: 500;
}

.logout-btn {
  color: #dc2626;
}

.logout-btn:hover {
  background: #fee2e2;
  color: #991b1b;
}

.menu-link .icon {
  font-size: 18px;
  min-width: 24px;
}

.menu-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 8px 0;
}

/* 遮罩層 */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 移動設備 */
@media (max-width: 768px) {
  .menu-sidebar {
    width: 220px;
  }
}
</style>
