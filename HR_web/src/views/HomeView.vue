<template>
  <div class="home-page">
    <!-- 頂部導航 -->
    <header class="navbar">
      <div class="navbar-left">
        <button class="menu-toggle" @click="showMenu = !showMenu">
          <span></span>
          <span></span>
          <span></span>
        </button>
        <h1 class="logo">HR System</h1>
      </div>
      <div class="navbar-right">
        <div v-if="!isLoggedIn" class="auth-menu">
          <router-link to="/login" class="nav-link">歡迎登入/註冊</router-link>
        </div>
        <div v-else class="user-menu">
          <span class="welcome-text">歡迎，{{ employee?.name || employee?.account }}</span>
          
          <!-- 菜單按鈕 -->
          <button class="menu-icon-btn" @click="showMenuDropdown = !showMenuDropdown">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>

          <!-- 下拉菜單 -->
          <nav v-if="showMenuDropdown" class="dropdown-menu">
            <router-link to="/" @click="showMenuDropdown = false" class="dropdown-link">
              <span class="icon">🏠</span>
              回首頁
            </router-link>
            <router-link to="/personal" @click="showMenuDropdown = false" class="dropdown-link">
              <span class="icon">👤</span>
              個人資料
            </router-link>
            <div class="dropdown-divider"></div>
            <button @click="logout" class="dropdown-link logout-link">
              <span class="icon">🚪</span>
              登出
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- 主容器 -->
    <div class="main-content">
      <!-- 英雄區段 -->
      <section class="hero">
        <div class="hero-content">
          <p class="eyebrow">HR System Portal</p>
          <h2>首頁</h2>
          <p class="lead">歡迎XX股份有限公司</p>
          <p v-if="!isLoggedIn" class="subtext">請登入以查看你的個人資料、打卡記錄、排班、休假和加班資訊。</p>
          <p v-else class="subtext">登入成功！請前往個人資料查看你的工作相關資訊。</p>
        </div>
      </section>

      <!-- 功能介紹卡片 -->
      <section class="features">
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🕐</div>
            <h3>穩定</h3>
            <p>快速打卡上班、下班，查看歷史記錄</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>堅持</h3>
            <p>查看你的班次安排和時間表</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🏖️</div>
            <h3>服務</h3>
            <p>提交和追蹤你的假期申請</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>效率</h3>
            <p>申請加班，主管 12 小時內自動核准</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from '../api'

const router = useRouter()

const employee = ref(null)
const showMenu = ref(false)
const showMenuDropdown = ref(false)

const isLoggedIn = computed(() => !!employee.value)
const isHrEmployee = computed(() => !!employee.value?.can_manage_employee_data)

const loadCurrentEmployee = async () => {
  const res = await api.get('employees/list/me/')
  employee.value = res.data
  localStorage.setItem('hr_employee', JSON.stringify(res.data))
}

const logout = async () => {
  try {
    await api.post('employees/auth/logout/')
  } catch (err) {
    console.error(err)
  }
  setAuthToken(null)
  localStorage.removeItem('hr_employee')
  employee.value = null
  showMenu.value = false
  ElMessage.success('已登出')
  router.push('/')
}

onMounted(async () => {
  const token = localStorage.getItem('hr_token')
  if (!token) return

  try {
    await loadCurrentEmployee()
  } catch (err) {
    setAuthToken(null)
    localStorage.removeItem('hr_employee')
    employee.value = null
  }

  // 點擊外部關閉菜單
  document.addEventListener('click', (e) => {
    const userMenu = document.querySelector('.user-menu')
    if (userMenu && !userMenu.contains(e.target)) {
      showMenuDropdown.value = false
    }
  })
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #fff;
}

/* 頂部導航欄 */
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  display: none;
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  cursor: pointer;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  padding: 0;
}

.menu-toggle span {
  width: 22px;
  height: 2.5px;
  background: #333;
  border-radius: 2px;
}

.logo {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.auth-menu .nav-link {
  padding: 8px 16px;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

.auth-menu .nav-link:hover {
  opacity: 0.9;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.welcome-text {
  font-size: 14px;
  color: #6b7280;
}

.logout-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

/* 菜單按鈕 */
.menu-icon-btn {
  width: 36px;
  height: 36px;
  padding: 6px;
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
  position: relative;
}

.menu-icon-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.menu-icon-btn svg {
  stroke: currentColor;
}

/* 下拉菜單 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  z-index: 40;
  overflow: hidden;
}

.dropdown-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #374151;
  height: auto;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  width: 100%;
  text-align: left;
  transition: background 0.2s;
  font-family: inherit;
}

.dropdown-link:hover {
  background: #f9fafb;
  color: #111827;
}

.dropdown-link.logout-link {
  color: #dc2626;
  border-top: 1px solid #e5e7eb;
}

.dropdown-link.logout-link:hover {
  background: #fee2e2;
  color: #991b1b;
}

.dropdown-link .icon {
  font-size: 16px;
  min-width: 20px;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 0;
}

/* 主容器 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

/* 英雄區段 */
.hero {
  padding: 80px 24px;
  text-align: center;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
}

.hero-content {
  max-width: 600px;
  margin: 0 auto;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #667eea;
}

.hero h2 {
  margin: 0 0 16px;
  font-size: 48px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
}

.lead {
  margin: 0 0 12px;
  font-size: 18px;
  color: #374151;
  font-weight: 500;
}

.subtext {
  margin: 0 0 32px;
  font-size: 16px;
  color: #6b7280;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 28px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  font-size: 15px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5568d3, #6b3c91);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

/* 功能卡片 */
.features {
  padding: 80px 24px;
  background: white;
}

.features-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.feature-card {
  padding: 32px 24px;
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  text-align: center;
  transition: all 0.3s;
}

.feature-card:hover {
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.1);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #111827;
  font-weight: 600;
}

.feature-card p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
}

/* 手機適配 */
@media (max-width: 768px) {
  .navbar {
    padding: 12px 16px;
  }

  .menu-toggle {
    display: flex;
  }

  .logo {
    font-size: 18px;
  }

  .navbar-right {
    gap: 12px;
  }

  .welcome-text {
    display: none;
  }

  .hero {
    padding: 60px 16px;
  }

  .hero h2 {
    font-size: 32px;
  }

  .lead {
    font-size: 16px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .features {
    padding: 60px 16px;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .feature-card {
    padding: 24px 16px;
  }
}
</style>