<template>
  <div class="personal-dashboard-page">
    <!-- 頂部導航 -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1>個人資料</h1>
      </div>
      <div class="header-right">
        <span v-if="isLoggedIn" class="user-info">歡迎，{{ employee?.name || employee?.account }}</span>
        
        <!-- 菜單按鈕 -->
        <button v-if="isLoggedIn" class="menu-icon-btn" @click="showMenuDropdown = !showMenuDropdown">
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
          <router-link to="/personal" @click="showMenuDropdown = false" class="dropdown-link" @click.prevent>
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
    </header>

    <!-- 主容器 -->
    <div class="dashboard-container">

      <!-- 內容區域 -->
      <main class="dashboard-content">
        <div v-if="!isLoggedIn" class="not-logged-in">
          <p>請先登入以查看個人資料</p>
          <router-link to="/login" class="login-link">前往登入</router-link>
        </div>

        <div v-else class="dashboard-main">
          <!-- 個人基本資訊 -->
          <section class="info-section">
            <h2>基本資訊</h2>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="員工編號">{{ employee?.employee_id || '-' }}</el-descriptions-item>
              <el-descriptions-item label="姓名">{{ employee?.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="性別">{{ employee?.gender === 'M' ? '男' : employee?.gender === 'F' ? '女' : '其他' }}</el-descriptions-item>
              <el-descriptions-item label="身分證字號">{{ employee?.id_number || '-' }}</el-descriptions-item>
              <el-descriptions-item label="部門">{{ departmentDisplay }}</el-descriptions-item>
              <el-descriptions-item label="今日打卡">{{ todayClockedInText }}</el-descriptions-item>
            </el-descriptions>
          </section>

          <!-- tab 內容 -->
          <el-tabs v-model="activeTab" class="dashboard-tabs">
            <!-- 打卡資訊 -->
            <el-tab-pane label="打卡資訊" name="attendance">
              <EarlyLeaveDialog ref="earlyLeaveDialogRef" @submitted="loadPortalData" />
            </el-tab-pane>

            <!-- 休假管理 -->
            <el-tab-pane label="休假管理" name="leaves">
              <LeaveRequestDialog ref="leaveRequestDialogRef" :show-approval="false" @submitted="loadPortalData" />
            </el-tab-pane>

            <!-- 加班紀錄 -->
            <el-tab-pane label="加班紀錄" name="overtimes">
              <OvertimeApprovalTable ref="overtimeApprovalTableRef" :show-approval="false" @submitted="loadPortalData" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElDialog, ElForm, ElFormItem, ElInput, ElButton, ElSelect, ElOption, ElDatePicker } from 'element-plus'
import api, { setAuthToken } from '../api'
import EarlyLeaveDialog from '../components/EarlyLeaveDialog.vue'
import LeaveRequestDialog from '../components/LeaveRequestDialog.vue'
import OvertimeApprovalTable from '../components/OvertimeApprovalTable.vue'

const router = useRouter()

// 組件 Refs
const earlyLeaveDialogRef = ref(null)
const leaveRequestDialogRef = ref(null)
const overtimeApprovalTableRef = ref(null)

const activeTab = ref('attendance')
const employee = ref(null)
const showMenuDropdown = ref(false)

const isLoggedIn = computed(() => !!employee.value)

const departmentDisplay = computed(() => {
  if (!employee.value?.department_name) return '未指派部門'
  const manager = employee.value.department_manager_name || employee.value.manager_name || '未設定'
  return `${employee.value.department_name}（主管：${manager}）`
})

const todayClockedInText = computed(() => {
  // 這個值會從 EarlyLeaveDialog 組件中取得
  // 暫時先保留用 ref
  return '是'
})

const parseError = (err, fallbackMessage) => {
  const data = err.response?.data
  if (!data) return fallbackMessage
  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  const messages = Object.entries(data).map(([key, value]) => {
    if (Array.isArray(value)) return `${key}: ${value[0]}`
    return `${key}: ${value}`
  })
  return messages.length ? messages.join('; ') : fallbackMessage
}

// 統一載入所有數據
const loadPortalData = async () => {
  try {
    // 載入各元件的數據
    await Promise.all([
      earlyLeaveDialogRef.value?.loadData(),
      leaveRequestDialogRef.value?.loadData(),
      overtimeApprovalTableRef.value?.loadData()
    ])
  } catch (err) {
    ElMessage.error(parseError(err, '讀取資料失敗'))
  }
}

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
  showMenuDropdown.value = false
  ElMessage.success('已登出')
  router.push('/')
}

onMounted(async () => {
  const token = localStorage.getItem('hr_token')
  if (!token) return

  try {
    await loadCurrentEmployee()
    await loadPortalData()
  } catch (err) {
    setAuthToken(null)
    localStorage.removeItem('hr_employee')
    employee.value = null
    router.push('/login')
  }

  // 點擊外部關閉菜單
  document.addEventListener('click', (e) => {
    const headerRight = document.querySelector('.header-right')
    if (headerRight && !headerRight.contains(e.target)) {
      showMenuDropdown.value = false
    }
  })
})
</script>

<style scoped>
.personal-dashboard-page {
  min-height: 100vh;
  background: #f9fafb;
}

/* 頂部導航 */
.dashboard-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 20px;
  color: #111827;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.user-info {
  font-size: 14px;
  color: #6b7280;
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

.dashboard-container {
  display: flex;
  position: relative;
}

.dashboard-content {
  flex: 1;
  padding: 24px;
}

.not-logged-in {
  text-align: center;
  padding: 60px 20px;
}

.login-link {
  display: inline-block;
  margin-top: 16px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 6px;
  text-decoration: none;
}

.info-section {
  margin-bottom: 32px;
}

.info-section h2 {
  margin: 0 0 16px;
  font-size: 18px;
  color: #111827;
}

.section-actions {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.clock-buttons {
  display: flex;
  gap: 8px;
}

.inner-card {
  margin-bottom: 14px;
}

.overtime-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hint-text {
  margin: 2px 0 0;
  color: #68758a;
}

.dashboard-tabs {
  margin-top: 24px;
}

:deep(.el-card) {
  border: none;
  border-radius: 12px;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5568d3, #6b3c91);
}

@media (max-width: 900px) {
  .dashboard-content {
    padding: 16px;
  }

  .info-section {
    margin-bottom: 24px;
  }

  .section-actions {
    flex-direction: column;
  }
}
</style>
