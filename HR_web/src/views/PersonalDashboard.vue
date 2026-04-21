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
              <div class="section-actions">
                <el-alert
                  :title="attendanceToday.has_clock_in ? (attendanceToday.clocked_out ? '今日已完成上下班打卡' : '今日已打卡上班，尚未下班打卡') : '今日尚未打卡'"
                  type="info"
                  :closable="false"
                  show-icon
                />
                <div class="clock-buttons">
                  <el-button type="primary" :disabled="attendanceToday.has_clock_in && !attendanceToday.clocked_out" @click="clockIn">上班打卡</el-button>
                  <el-button type="success" :disabled="!attendanceToday.has_clock_in || attendanceToday.clocked_out" @click="clockOut()">下班打卡</el-button>
                  <el-button type="warning" :disabled="!attendanceToday.has_clock_in || attendanceToday.clocked_out" @click="showEarlyLeaveDialog">提早下班</el-button>
                </div>
              </div>
              <el-table :data="attendanceRecords">
                <el-table-column prop="clock_in" label="上班打卡" />
                <el-table-column prop="clock_out" label="下班打卡" />
                <el-table-column prop="note" label="備註" />
              </el-table>

              <!-- 提早下班備註 Dialog -->
              <el-dialog v-model="earlyLeaveDialogVisible" title="提早下班申請" width="500px" @close="noteInput = ''">
                <div style="padding: 20px 0;">
                  <p style="margin-bottom: 20px; color: #333;">
                    請說明提早下班的原因：
                  </p>
                  <el-input
                    v-model="noteInput"
                    type="textarea"
                    rows="4"
                    placeholder="例：身體不適、家中有急事、其他..."
                    clearable
                  />
                </div>
                <template #footer>
                  <span>
                    <el-button @click="earlyLeaveDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitEarlyLeave">確認下班</el-button>
                  </span>
                </template>
              </el-dialog>
            </el-tab-pane>

            <!-- 排班資訊 -->
            <el-tab-pane label="排班資訊" name="shifts">
              <el-table :data="shiftSchedules">
                <el-table-column prop="shift_date" label="日期" />
                <el-table-column prop="start_time" label="上班" />
                <el-table-column prop="end_time" label="下班" />
                <el-table-column prop="shift_type" label="班別" />
              </el-table>
            </el-tab-pane>

            <!-- 休假管理 -->
            <el-tab-pane label="休假管理" name="leaves">
              <div class="section-actions">
                <div class="clock-buttons">
                  <el-button type="primary" @click="showLeaveDialog">新增請假</el-button>
                </div>
              </div>
              <el-table :data="leaveRequests">
                <el-table-column prop="leave_type" label="假別" />
                <el-table-column prop="start_date" label="起始日" />
                <el-table-column prop="end_date" label="結束日" />
                <el-table-column prop="status" label="狀態" />
                <el-table-column prop="reason" label="原因" />
              </el-table>

              <!-- 新增請假 Dialog -->
              <el-dialog v-model="leaveRequestDialogVisible" title="新增請假申請" width="600px" @close="leaveForm = { leave_type: '', start_date: null, end_date: null, reason: '' }">
                <el-form :model="leaveForm" label-width="100px" style="padding: 0 20px;">
                  <!-- 假別選擇 -->
                  <el-form-item label="假別">
                    <el-select v-model="leaveForm.leave_type" placeholder="請選擇假別">
                      <el-option v-for="option in leaveTypeOptions" :key="option.value" :label="option.label" :value="option.value" />
                    </el-select>
                  </el-form-item>

                  <!-- 起始日 -->
                  <el-form-item label="起始日">
                    <el-date-picker
                      v-model="leaveForm.start_date"
                      type="date"
                      placeholder="選擇起始日期"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>

                  <!-- 結束日 -->
                  <el-form-item label="結束日">
                    <el-date-picker
                      v-model="leaveForm.end_date"
                      type="date"
                      placeholder="選擇結束日期"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>

                  <!-- 原因 -->
                  <el-form-item label="請假原因">
                    <el-input
                      v-model="leaveForm.reason"
                      type="textarea"
                      rows="4"
                      placeholder="請填寫請假原因"
                      maxlength="255"
                      show-word-limit
                    />
                  </el-form-item>
                </el-form>

                <template #footer>
                  <span>
                    <el-button @click="leaveRequestDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitLeaveRequest">提交申請</el-button>
                  </span>
                </template>
              </el-dialog>
            </el-tab-pane>

            <!-- 加班紀錄 -->
            <el-tab-pane label="加班紀錄" name="overtimes">
              <el-card class="inner-card" shadow="never">
                <template #header>提出加班申請</template>
                <el-form :inline="true" :model="overtimeApplyForm" class="overtime-form">
                  <el-form-item label="日期"><el-date-picker v-model="overtimeApplyForm.work_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
                  <el-form-item label="時數"><el-input-number v-model="overtimeApplyForm.hours" :min="0.5" :step="0.5" /></el-form-item>
                  <el-form-item label="原因"><el-input v-model="overtimeApplyForm.reason" placeholder="輸入加班原因" style="width: 280px" /></el-form-item>
                  <el-form-item><el-button type="primary" @click="submitOvertime">送出申請</el-button></el-form-item>
                </el-form>
                <p class="hint-text">主管若 12 小時內未處理，系統將自動核准。</p>
              </el-card>

              <el-table :data="overtimeRecords">
                <el-table-column prop="work_date" label="日期" />
                <el-table-column prop="hours" label="時數" />
                <el-table-column prop="status" label="狀態" />
                <el-table-column prop="auto_approved" label="自動核准">
                  <template #default="scope">{{ scope.row.auto_approved ? '是' : '否' }}</template>
                </el-table-column>
                <el-table-column prop="approved_by_name" label="核准主管" />
                <el-table-column prop="reason" label="原因" />
              </el-table>
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
import { useAttendance } from '../composables/useAttendance'
import { useLeaveRequest } from '../composables/useLeaveRequest'
import { useOvertime } from '../composables/useOvertime'

const router = useRouter()

// 使用 Composables 導入共享邏輯
const {
  attendanceRecords,
  attendanceToday,
  earlyLeaveDialogVisible,
  noteInput,
  clockIn,
  clockOut,
  showEarlyLeaveDialog,
  submitEarlyLeave,
  loadAttendanceData
} = useAttendance()

const {
  leaveRequests,
  leaveRequestDialogVisible,
  leaveForm,
  leaveTypeOptions,
  showLeaveDialog,
  submitLeaveRequest,
  loadLeaveData
} = useLeaveRequest()

const {
  overtimeRecords,
  overtimeApplyForm,
  submitOvertime,
  loadOvertimeData
} = useOvertime()

const activeTab = ref('attendance')
const employee = ref(null)
const showMenuDropdown = ref(false)
const shiftSchedules = ref([])

const isLoggedIn = computed(() => !!employee.value)

const departmentDisplay = computed(() => {
  if (!employee.value?.department_name) return '未指派部門'
  const manager = employee.value.department_manager_name || employee.value.manager_name || '未設定'
  return `${employee.value.department_name}（主管：${manager}）`
})

const todayClockedInText = computed(() => (attendanceToday.value.has_clock_in ? '是' : '否'))

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
    const [shiftsRes] = await Promise.all([
      api.get('employees/shifts/')
    ])
    shiftSchedules.value = shiftsRes.data

    // 載入各 Composable 的數據
    await Promise.all([
      loadAttendanceData(),
      loadLeaveData(),
      loadOvertimeData()
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
