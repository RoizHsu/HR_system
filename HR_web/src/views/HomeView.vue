<template>
  <div class="home-page">
    <section class="hero-card">
      <p class="eyebrow">HR System Portal</p>
      <h1>員工入口首頁</h1>
      <p class="lead">這裡是公開首頁。登入後，系統會顯示你的個人資料、打卡、請假與加班區塊。</p>

      <div class="action-row">
        <router-link to="/login" class="primary-link">前往登入 / 註冊</router-link>
        <router-link v-if="isHrEmployee" to="/dashboard" class="secondary-link">進入 HR 後台</router-link>
      </div>

      <div v-if="isLoggedIn" class="status-card">
        <strong>目前已登入：</strong>
        <span>{{ employeeName }}</span>
      </div>
    </section>

    <section v-if="isAuthenticated" class="portal-card">
      <div class="portal-header">
        <div>
          <h2>歡迎，{{ employee?.name || employee?.account }}</h2>
          <p>{{ employee?.employee_id }} | {{ employee?.department_name || '未指派部門' }}</p>
        </div>
        <el-button type="danger" plain @click="logout">登出</el-button>
      </div>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="個人資訊" name="overview">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="員工編號">{{ employee?.employee_id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ employee?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="性別">{{ employee?.gender === 'M' ? '男' : employee?.gender === 'F' ? '女' : '其他' }}</el-descriptions-item>
            <el-descriptions-item label="身分證字號">{{ employee?.id_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="部門">{{ departmentDisplay }}</el-descriptions-item>
            <el-descriptions-item label="今日打卡">{{ todayClockedInText }}</el-descriptions-item>
          </el-descriptions>
          <el-alert
            class="info-tip"
            :title="canManageEmployeeData ? '你是 HR 人員，可以進入後台管理' : '你目前是一般員工，這裡是你的個人主頁'"
            :type="canManageEmployeeData ? 'success' : 'info'"
            :closable="false"
            show-icon
          />
        </el-tab-pane>

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
              <el-button type="success" :disabled="!attendanceToday.has_clock_in || attendanceToday.clocked_out" @click="clockOut">下班打卡</el-button>
            </div>
          </div>

          <el-table :data="attendanceRecords">
            <el-table-column prop="clock_in" label="上班打卡" />
            <el-table-column prop="clock_out" label="下班打卡" />
            <el-table-column prop="note" label="備註" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="排班資訊" name="shifts">
          <el-table :data="shiftSchedules">
            <el-table-column prop="shift_date" label="日期" />
            <el-table-column prop="start_time" label="上班" />
            <el-table-column prop="end_time" label="下班" />
            <el-table-column prop="shift_type" label="班別" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="休假管理" name="leaves">
          <el-table :data="leaveRequests">
            <el-table-column prop="leave_type" label="假別" />
            <el-table-column prop="start_date" label="起始日" />
            <el-table-column prop="end_date" label="結束日" />
            <el-table-column prop="status" label="狀態" />
            <el-table-column prop="reason" label="原因" />
          </el-table>
        </el-tab-pane>

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
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from '../api'

const router = useRouter()

const activeTab = ref('overview')
const employee = ref(null)
const attendanceRecords = ref([])
const attendanceToday = ref({ has_clock_in: false, clocked_out: false, record: null })
const shiftSchedules = ref([])
const leaveRequests = ref([])
const overtimeRecords = ref([])

const overtimeApplyForm = ref({
  work_date: null,
  hours: 1,
  reason: ''
})

const isLoggedIn = computed(() => !!employee.value)
const canManageEmployeeData = computed(() => !!employee.value?.can_manage_employee_data)
const isHrEmployee = computed(() => !!employee.value?.can_manage_employee_data)

const departmentDisplay = computed(() => {
  if (!employee.value?.department_name) return '未指派部門'
  const manager = employee.value.department_manager_name || employee.value.manager_name || '未設定'
  return `${employee.value.department_name}（主管：${manager}）`
})

const todayClockedInText = computed(() => (attendanceToday.value.has_clock_in ? '是' : '否'))
const employeeName = computed(() => employee.value?.name || employee.value?.account || '未知使用者')

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

const loadPortalData = async () => {
  const [attendanceRes, attendanceTodayRes, shiftsRes, leavesRes, overtimeRes] = await Promise.all([
    api.get('employees/attendance/'),
    api.get('employees/attendance/today-status/'),
    api.get('employees/shifts/'),
    api.get('employees/leaves/'),
    api.get('employees/overtimes/')
  ])

  attendanceRecords.value = attendanceRes.data
  attendanceToday.value = attendanceTodayRes.data
  shiftSchedules.value = shiftsRes.data
  leaveRequests.value = leavesRes.data
  overtimeRecords.value = overtimeRes.data
}

const loadCurrentEmployee = async () => {
  const res = await api.get('employees/list/me/')
  employee.value = res.data
  localStorage.setItem('hr_employee', JSON.stringify(res.data))
}

const clockIn = async () => {
  try {
    await api.post('employees/attendance/clock-in/')
    ElMessage.success('上班打卡成功')
    await loadPortalData()
  } catch (err) {
    ElMessage.error(parseError(err, '打卡失敗'))
  }
}

const clockOut = async () => {
  try {
    await api.post('employees/attendance/clock-out/')
    ElMessage.success('下班打卡成功')
    await loadPortalData()
  } catch (err) {
    ElMessage.error(parseError(err, '打卡失敗'))
  }
}

const submitOvertime = async () => {
  if (!overtimeApplyForm.value.work_date || !overtimeApplyForm.value.hours) {
    ElMessage.error('請完整填寫加班日期與時數')
    return
  }

  try {
    await api.post('employees/overtimes/', overtimeApplyForm.value)
    overtimeApplyForm.value = { work_date: null, hours: 1, reason: '' }
    ElMessage.success('加班申請已送出')
    await loadPortalData()
  } catch (err) {
    ElMessage.error(parseError(err, '送出加班申請失敗'))
  }
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
  attendanceRecords.value = []
  shiftSchedules.value = []
  leaveRequests.value = []
  overtimeRecords.value = []
  activeTab.value = 'overview'
  ElMessage.success('已登出')
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
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero-card,
.portal-card {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto 24px;
  padding: 40px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
}

.portal-card {
  padding: 28px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #667eea;
}

.hero-card h1,
.portal-header h2 {
  margin: 0;
  color: #111827;
}

.hero-card h1 {
  font-size: 40px;
  line-height: 1.1;
}

.portal-header h2 {
  font-size: 24px;
}

.lead {
  margin: 16px 0 28px;
  font-size: 16px;
  line-height: 1.7;
  color: #4b5563;
}

.action-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-link,
.secondary-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
}

.primary-link {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.secondary-link {
  border: 1px solid #d1d5db;
  color: #1f2937;
  background: #fff;
}

.status-card {
  margin-top: 24px;
  padding: 16px 18px;
  border-radius: 14px;
  background: #f9fafb;
  color: #111827;
}

.portal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.portal-header p {
  margin: 8px 0 0;
  color: #9ca3af;
}

.info-tip {
  margin-top: 14px;
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

:deep(.el-card) {
  border: none;
  border-radius: 12px;
}

:deep(.el-tabs__header) {
  border-bottom: 2px solid #f0f0f0;
}

:deep(.el-tabs__nav-wrap::after) {
  background: linear-gradient(90deg, #667eea, #764ba2);
  height: 3px;
}

:deep(.el-tab-pane) {
  padding: 24px 0;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
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
  .home-page {
    padding: 14px;
  }

  .hero-card,
  .portal-card {
    padding: 20px;
  }

  .hero-card h1 {
    font-size: 30px;
  }

  .portal-header {
    flex-direction: column;
    align-items: stretch;
  }

  .section-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .action-row {
    flex-direction: column;
  }

  .primary-link,
  .secondary-link {
    width: 100%;
  }
}
</style>