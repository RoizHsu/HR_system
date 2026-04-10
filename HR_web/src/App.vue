<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from './api'

const authMode = ref('login')
const authLoading = ref(false)
const pageLoading = ref(false)
const activeTab = ref('overview')

const employee = ref(null)
const departments = ref([])
const allEmployees = ref([])

const attendanceRecords = ref([])
const attendanceToday = ref({ has_clock_in: false, clocked_out: false, record: null })
const shiftSchedules = ref([])
const leaveRequests = ref([])
const overtimeRecords = ref([])
const managerPendingOvertimes = ref([])
const orgDepartments = ref([])

const authForm = ref({
  account: '',
  email: '',
  password: '',
  password_confirm: '',
  id_number: '',
  name: '',
  gender: 'O',
  birthday: null,
  emergency_contact: '',
  emergency_phone: ''
})

const overtimeApplyForm = ref({
  work_date: null,
  hours: 1,
  reason: ''
})

const profileForm = ref({
  employee_id: '',
  account: '',
  email: '',
  name: '',
  gender: 'O',
  birthday: null,
  id_number: '',
  phone: '',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  department: null,
  job_title: '',
  manager: null,
  emp_type: 'full_time',
  status: 'active',
  hire_date: null,
  resignation_date: null,
  position_level: 1
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const isAuthenticated = computed(() => !!employee.value)

const orgRows = computed(() => {
  const rows = []
  orgDepartments.value.forEach((department) => {
    department.employees.forEach((member) => {
      rows.push({
        department_name: department.name,
        parent_department: orgDepartments.value.find((d) => d.id === department.parent)?.name || '-',
        ...member
      })
    })
  })
  return rows
})

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

  const messages = Object.entries(data)
    .map(([key, value]) => {
      if (Array.isArray(value)) return `${key}: ${value[0]}`
      return `${key}: ${value}`
    })
  return messages.length ? messages.join('; ') : fallbackMessage
}

const applyEmployeeToForm = (data) => {
  profileForm.value = {
    employee_id: data.employee_id || '',
    account: data.account || '',
    email: data.email || '',
    name: data.name || '',
    gender: data.gender || 'O',
    birthday: data.birthday,
    id_number: data.id_number || '',
    phone: data.phone || '',
    address: data.address || '',
    emergency_contact: data.emergency_contact || '',
    emergency_phone: data.emergency_phone || '',
    department: data.department,
    job_title: data.job_title || '',
    manager: data.manager,
    emp_type: data.emp_type || 'full_time',
    status: data.status || 'active',
    hire_date: data.hire_date,
    resignation_date: data.resignation_date,
    position_level: data.position_level || 1
  }
}

const loadDashboardData = async () => {
  pageLoading.value = true
  try {
    const [attendanceRes, attendanceTodayRes, shiftsRes, leavesRes, overtimeRes, managerPendingRes, orgRes, deptRes, employeesRes] = await Promise.all([
      api.get('employees/attendance/'),
      api.get('employees/attendance/today-status/'),
      api.get('employees/shifts/'),
      api.get('employees/leaves/'),
      api.get('employees/overtimes/'),
      api.get('employees/overtimes/pending-approvals/'),
      api.get('employees/org-chart/'),
      api.get('employees/departments/'),
      api.get('employees/list/')
    ])

    attendanceRecords.value = attendanceRes.data
    attendanceToday.value = attendanceTodayRes.data
    shiftSchedules.value = shiftsRes.data
    leaveRequests.value = leavesRes.data
    overtimeRecords.value = overtimeRes.data
    managerPendingOvertimes.value = managerPendingRes.data
    orgDepartments.value = orgRes.data.departments || []
    departments.value = deptRes.data
    allEmployees.value = employeesRes.data
  } catch (err) {
    ElMessage.error(parseError(err, '讀取儀表板資料失敗'))
  } finally {
    pageLoading.value = false
  }
}

const loadCurrentEmployee = async () => {
  const res = await api.get('employees/list/me/')
  employee.value = res.data
  applyEmployeeToForm(res.data)
}

const handleRegister = async () => {
  authLoading.value = true
  try {
    const res = await api.post('employees/auth/register/', authForm.value)
    setAuthToken(res.data.token)
    employee.value = res.data.employee
    applyEmployeeToForm(employee.value)
    await loadDashboardData()
    activeTab.value = 'overview'
    ElMessage.success('註冊成功，已自動登入')
  } catch (err) {
    ElMessage.error(parseError(err, '註冊失敗'))
  } finally {
    authLoading.value = false
  }
}

const handleLogin = async () => {
  authLoading.value = true
  try {
    const payload = {
      account: authForm.value.account,
      password: authForm.value.password
    }
    const res = await api.post('employees/auth/login/', payload)
    setAuthToken(res.data.token)
    employee.value = res.data.employee
    applyEmployeeToForm(employee.value)
    await loadDashboardData()
    activeTab.value = 'overview'
    ElMessage.success('登入成功')
  } catch (err) {
    ElMessage.error(parseError(err, '登入失敗'))
  } finally {
    authLoading.value = false
  }
}

const submitAuth = async () => {
  if (!authForm.value.account.trim()) {
    ElMessage.error('帳號不能為空')
    return
  }
  if (!authForm.value.password) {
    ElMessage.error('密碼不能為空')
    return
  }

  if (authMode.value === 'register') {
    if (!authForm.value.email.trim()) {
      ElMessage.error('Email 不能為空')
      return
    }
    if (!authForm.value.password_confirm) {
      ElMessage.error('請再次輸入密碼')
      return
    }
    await handleRegister()
  } else {
    await handleLogin()
  }
}

const clockIn = async () => {
  try {
    await api.post('employees/attendance/clock-in/')
    ElMessage.success('上班打卡成功')
    await loadDashboardData()
  } catch (err) {
    ElMessage.error(parseError(err, '打卡失敗'))
  }
}

const clockOut = async () => {
  try {
    await api.post('employees/attendance/clock-out/')
    ElMessage.success('下班打卡成功')
    await loadDashboardData()
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
    overtimeApplyForm.value = {
      work_date: null,
      hours: 1,
      reason: ''
    }
    ElMessage.success('加班申請已送出')
    await loadDashboardData()
  } catch (err) {
    ElMessage.error(parseError(err, '送出加班申請失敗'))
  }
}

const approveOvertime = async (id) => {
  try {
    await api.post(`employees/overtimes/${id}/approve/`)
    ElMessage.success('已核准加班申請')
    await loadDashboardData()
  } catch (err) {
    ElMessage.error(parseError(err, '核准失敗'))
  }
}

const rejectOvertime = async (id) => {
  try {
    await api.post(`employees/overtimes/${id}/reject/`)
    ElMessage.success('已拒絕加班申請')
    await loadDashboardData()
  } catch (err) {
    ElMessage.error(parseError(err, '拒絕失敗'))
  }
}

const updateProfile = async () => {
  try {
    const res = await api.patch('employees/list/me/update/', profileForm.value)
    employee.value = res.data
    applyEmployeeToForm(res.data)
    ElMessage.success('個人資料已更新')
    await loadDashboardData()
  } catch (err) {
    ElMessage.error(parseError(err, '更新資料失敗'))
  }
}

const changePassword = async () => {
  try {
    const res = await api.post('employees/auth/change-password/', passwordForm.value)
    setAuthToken(res.data.token)
    passwordForm.value = {
      old_password: '',
      new_password: '',
      new_password_confirm: ''
    }
    ElMessage.success('密碼修改成功')
  } catch (err) {
    ElMessage.error(parseError(err, '修改密碼失敗'))
  }
}

const logout = async () => {
  try {
    await api.post('employees/auth/logout/')
  } catch (err) {
    console.error(err)
  }
  setAuthToken(null)
  employee.value = null
  attendanceRecords.value = []
  shiftSchedules.value = []
  leaveRequests.value = []
  overtimeRecords.value = []
  managerPendingOvertimes.value = []
  orgDepartments.value = []
  ElMessage.success('已登出')
}

onMounted(async () => {
  const token = localStorage.getItem('hr_token')
  if (!token) return

  try {
    await loadCurrentEmployee()
    await loadDashboardData()
  } catch (err) {
    setAuthToken(null)
    employee.value = null
  }
})
</script>

<template>
  <div class="page-shell">
    <el-card v-if="!isAuthenticated" class="auth-card">
      <template #header>
        <div class="header-row">
          <h2>HR 員工管理系統</h2>
          <span>請先登入或註冊</span>
        </div>
      </template>

      <el-segmented v-model="authMode" :options="[
        { label: '登入', value: 'login' },
        { label: '註冊', value: 'register' }
      ]" class="auth-switch" />

      <el-form label-width="110px" class="auth-form">
        <el-form-item label="帳號">
          <el-input v-model="authForm.account" placeholder="請輸入帳號" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="身分證字號">
          <el-input v-model="authForm.id_number" placeholder="請輸入身分證字號" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="姓名">
          <el-input v-model="authForm.name" placeholder="請輸入姓名" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="性別">
          <el-select v-model="authForm.gender" placeholder="請選擇性別">
            <el-option label="男" value="M" />
            <el-option label="女" value="F" />
            <el-option label="其他" value="O" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="出生日期">
          <el-date-picker v-model="authForm.birthday" type="date" value-format="YYYY-MM-DD" placeholder="請選擇出生日期(1999/01/01)" style="width: 100%" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="電子郵件">
          <el-input v-model="authForm.email" placeholder="name@example.com" />
        </el-form-item>

        <el-form-item label="密碼">
          <el-input v-model="authForm.password" show-password type="password" placeholder="請輸入密碼" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="確認密碼">
          <el-input v-model="authForm.password_confirm" show-password type="password" placeholder="請再次輸入密碼" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="緊急聯絡人姓名">
          <el-input v-model="authForm.emergency_contact" placeholder="請輸入緊急聯絡人姓名" />
        </el-form-item>

        <el-form-item v-if="authMode === 'register'" label="緊急聯絡人電話">
          <el-input v-model="authForm.emergency_phone" placeholder="請輸入緊急聯絡人電話" />
        </el-form-item>
      </el-form>


      <el-button type="primary" :loading="authLoading" class="full-btn" @click="submitAuth">
        {{ authMode === 'register' ? '建立帳號' : '登入系統' }}
      </el-button>
    </el-card>

    <div v-else class="dashboard-wrap" v-loading="pageLoading">
      <el-card class="top-card">
        <div class="header-row">
          <div>
            <h2>歡迎，{{ employee?.name || employee?.account }}</h2>
            <p>{{ employee?.employee_id }} | {{ employee?.department_name || '未指派部門' }}</p>
          </div>
          <el-button type="danger" plain @click="logout">登出</el-button>
        </div>
      </el-card>

      <el-card>
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
          </el-tab-pane>

          <el-tab-pane label="打卡資訊" name="attendance">
            <div class="section-actions">
              <el-alert :title="attendanceToday.has_clock_in ? (attendanceToday.clocked_out ? '今日已完成上下班打卡' : '今日已打卡上班，尚未下班打卡') : '今日尚未打卡'" type="info" :closable="false" show-icon />
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
              <el-table-column prop="auto_approved" label="自動核准"><template #default="scope">{{ scope.row.auto_approved ? '是' : '否' }}</template></el-table-column>
              <el-table-column prop="approved_by_name" label="核准主管" />
              <el-table-column prop="reason" label="原因" />
            </el-table>

            <el-divider v-if="managerPendingOvertimes.length > 0">主管審核區</el-divider>
            <el-table v-if="managerPendingOvertimes.length > 0" :data="managerPendingOvertimes">
              <el-table-column prop="employee_name" label="員工" />
              <el-table-column prop="work_date" label="加班日期" />
              <el-table-column prop="hours" label="時數" />
              <el-table-column prop="reason" label="原因" />
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button type="success" size="small" @click="approveOvertime(scope.row.id)">核准</el-button>
                  <el-button type="danger" size="small" @click="rejectOvertime(scope.row.id)">拒絕</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="基本檔案(可修改)" name="profile">
            <el-form :model="profileForm" label-width="130px" class="grid-form">
              <el-form-item label="員工編號"><el-input v-model="profileForm.employee_id" /></el-form-item>
              <el-form-item label="帳號"><el-input v-model="profileForm.account" /></el-form-item>
              <el-form-item label="電子郵件"><el-input v-model="profileForm.email" /></el-form-item>
              <el-form-item label="姓名"><el-input v-model="profileForm.name" /></el-form-item>
              <el-form-item label="性別"><el-select v-model="profileForm.gender" style="width: 100%"><el-option label="男" value="M" /><el-option label="女" value="F" /><el-option label="其他" value="O" /></el-select></el-form-item>
              <el-form-item label="出生日期"><el-date-picker v-model="profileForm.birthday" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
              <el-form-item label="身分證字號"><el-input v-model="profileForm.id_number" /></el-form-item>
              <el-form-item label="聯絡電話"><el-input v-model="profileForm.phone" /></el-form-item>
              <el-form-item label="地址" class="span-2"><el-input v-model="profileForm.address" type="textarea" rows="2" /></el-form-item>
              <el-form-item label="緊急聯絡人"><el-input v-model="profileForm.emergency_contact" /></el-form-item>
              <el-form-item label="緊急聯絡電話"><el-input v-model="profileForm.emergency_phone" /></el-form-item>
              <el-form-item label="部門"><el-select v-model="profileForm.department" clearable style="width: 100%"><el-option v-for="department in departments" :key="department.id" :label="department.name" :value="department.id" /></el-select></el-form-item>
              <el-form-item label="職稱"><el-input v-model="profileForm.job_title" /></el-form-item>
              <el-form-item label="主管"><el-select v-model="profileForm.manager" clearable style="width: 100%"><el-option v-for="manager in allEmployees" :key="manager.id" :label="manager.name || manager.account" :value="manager.id" /></el-select></el-form-item>
              <el-form-item label="員工類型"><el-select v-model="profileForm.emp_type" style="width: 100%"><el-option label="全職" value="full_time" /><el-option label="兼職" value="part_time" /><el-option label="實習" value="intern" /></el-select></el-form-item>
              <el-form-item label="員工狀態"><el-select v-model="profileForm.status" style="width: 100%"><el-option label="在職" value="active" /><el-option label="離職" value="resigned" /><el-option label="留停" value="on_leave" /></el-select></el-form-item>
              <el-form-item label="職位階層"><el-input-number v-model="profileForm.position_level" :min="1" /></el-form-item>
              <el-form-item label="到職日"><el-date-picker v-model="profileForm.hire_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
              <el-form-item label="離職日"><el-date-picker v-model="profileForm.resignation_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
            </el-form>
            <el-button type="primary" @click="updateProfile">儲存基本檔案</el-button>
          </el-tab-pane>

          <el-tab-pane label="組織圖" name="org">
            <el-table :data="orgRows">
              <el-table-column prop="department_name" label="部門" />
              <el-table-column prop="parent_department" label="上層部門" />
              <el-table-column prop="employee_id" label="員工編號" />
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="job_title" label="職稱" />
              <el-table-column prop="position_level" label="職位階層" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="密碼修改" name="password">
            <el-form :model="passwordForm" label-width="120px" class="password-form">
              <el-form-item label="舊密碼"><el-input v-model="passwordForm.old_password" show-password type="password" /></el-form-item>
              <el-form-item label="新密碼"><el-input v-model="passwordForm.new_password" show-password type="password" /></el-form-item>
              <el-form-item label="確認新密碼"><el-input v-model="passwordForm.new_password_confirm" show-password type="password" /></el-form-item>
            </el-form>
            <el-button type="warning" @click="changePassword">更新密碼</el-button>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.page-shell {
  min-height: 100vh;
  padding: 32px;
  background: linear-gradient(160deg, #f6f8fb 0%, #f0efe7 100%);
}

.auth-card {
  max-width: 580px;
  margin: 48px auto;
}

.dashboard-wrap {
  max-width: 1240px;
  margin: 0 auto;
}

.top-card {
  margin-bottom: 18px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.header-row h2 {
  margin: 0;
}

.header-row p {
  margin: 4px 0 0;
  color: #667085;
}

.auth-switch {
  margin-bottom: 16px;
}

.auth-form {
  margin-bottom: 12px;
}

.full-btn {
  width: 100%;
}

.grid-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 12px;
}

.span-2 {
  grid-column: span 2;
}

.password-form {
  max-width: 480px;
}

.inner-card {
  margin-bottom: 14px;
}

.hint-text {
  margin: 2px 0 0;
  color: #68758a;
}

.overtime-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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

@media (max-width: 900px) {
  .page-shell {
    padding: 14px;
  }

  .grid-form {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: span 1;
  }

  .section-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
