<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from './api'
import { el } from 'element-plus/es/locale/index.mjs'

const authMode = ref('login')
const authLoading = ref(false)
const pageLoading = ref(false)
const companyEditSaving = ref(false)
const activeTab = ref('overview')

const employee = ref(null)
const departments = ref([])
const allEmployees = ref([])
const selectedCompanyEmployeeId = ref(null)
const selectedCompanyDepartmentId = ref(null)

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
const canManageEmployeeData = computed(() => !!employee.value?.can_manage_employee_data)

const companyEditableEmployees = computed(() => {
  let result = allEmployees.value || []
  if (selectedCompanyDepartmentId.value) {
    result = result.filter((emp) => emp.department === selectedCompanyDepartmentId.value)
  }
  return result
})

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

    if (canManageEmployeeData.value) {
      if (!selectedCompanyEmployeeId.value && allEmployees.value.length > 0) {
        selectedCompanyEmployeeId.value = allEmployees.value[0].id
        applyEmployeeToForm(allEmployees.value[0])
      }

      if (selectedCompanyEmployeeId.value) {
        const selected = allEmployees.value.find((item) => item.id === selectedCompanyEmployeeId.value)
        if (selected) {
          applyEmployeeToForm(selected)
        }
      }
    }
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

const onCompanyDepartmentChange = () => {
  selectedCompanyEmployeeId.value = null
}

const onCompanyEmployeeChange = () => {
  if (!selectedCompanyEmployeeId.value) return
  const selected = companyEditableEmployees.value.find((item) => item.id === selectedCompanyEmployeeId.value)
  if (!selected) return
  applyEmployeeToForm(selected)
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

const updateCompanyEmployee = async () => {
  if (!canManageEmployeeData.value) {
    ElMessage.error('你目前沒有員工資料修改權限')
    return
  }

  if (!selectedCompanyEmployeeId.value) {
    ElMessage.error('請先選擇要修改的員工')
    return
  }

  companyEditSaving.value = true
  try {
    const res = await api.patch(`employees/list/${selectedCompanyEmployeeId.value}/`, profileForm.value)
    const updatedEmployee = res.data

    allEmployees.value = allEmployees.value.map((item) => (item.id === updatedEmployee.id ? updatedEmployee : item))
    applyEmployeeToForm(updatedEmployee)
    if (employee.value?.id === updatedEmployee.id) {
      employee.value = updatedEmployee
    }

    ElMessage.success('員工資料已更新')
    await loadDashboardData()
  } catch (err) {
    ElMessage.error(parseError(err, '更新員工資料失敗'))
  } finally {
    companyEditSaving.value = false
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
  selectedCompanyEmployeeId.value = null
  selectedCompanyDepartmentId.value = null
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

      <el-form label-width="110px" class="auth-form" @submit.prevent="submitAuth" @keydown.enter.prevent="submitAuth">
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

        <el-button type="primary" native-type="submit" :loading="authLoading" class="full-btn">
          {{ authMode === 'register' ? '建立帳號' : '登入系統' }}
        </el-button>
      </el-form>
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
            <el-alert
              class="readonly-tip"
              :title="canManageEmployeeData ? '你具備公司員工資料管理權限' : '目前帳號為唯讀模式，可查看資料但不可修改員工檔案'"
              :type="canManageEmployeeData ? 'success' : 'info'"
              :closable="false"
              show-icon
            />
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

          <el-tab-pane v-if="canManageEmployeeData" label="公司員工資料修改" name="profile">
            <div class="employee-manager-container">
              <!-- 左側篩選邊欄 -->
              <div class="filter-sidebar">
                <div class="sidebar-header">
                  <h3>篩選選單</h3>
                </div>
                <el-alert
                  title="僅限授權群組可使用"
                  type="success"
                  :closable="false"
                  show-icon
                  class="sidebar-alert"
                />
                <el-form label-width="0" class="filter-form">
                  <div class="filter-group">
                    <label class="filter-label">部門篩選</label>
                    <el-select
                      v-model="selectedCompanyDepartmentId"
                      style="width: 100%"
                      placeholder="全部部門"
                      clearable
                      @change="onCompanyDepartmentChange"
                    >
                      <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
                    </el-select>
                  </div>
                  <div class="filter-group">
                    <label class="filter-label">選擇員工</label>
                    <el-select
                      v-model="selectedCompanyEmployeeId"
                      clearable
                      filterable
                      style="width: 100%"
                      placeholder="搜尋員工"
                      @change="onCompanyEmployeeChange"
                    >
                      <el-option
                        v-for="item in companyEditableEmployees"
                        :key="item.id"
                        :label="`${item.name || item.account}`"
                        :value="item.id"
                      >
                        <div class="employee-option">
                          <div class="employee-name">{{ item.name || item.account }}</div>
                          <div class="employee-id">{{ item.employee_id }}</div>
                        </div>
                      </el-option>
                    </el-select>
                  </div>
                  <div class="filter-stats">
                    <span class="stat-label">可用員工</span>
                    <span class="stat-count">{{ companyEditableEmployees.length }}</span>
                  </div>
                </el-form>
              </div>

              <!-- 右側編輯區 -->
              <div class="edit-content">
                <div class="content-header" v-if="selectedCompanyEmployeeId">
                  <h3>員工資料編輯</h3>
                  <el-tag type="success" effect="light" v-if="selectedCompanyEmployeeId">
                    {{ allEmployees.find((e) => e.id === selectedCompanyEmployeeId)?.name || '編輯中' }}
                  </el-tag>
                </div>
                <el-empty v-else description="請先選擇員工" class="empty-state" />

                <el-form v-if="selectedCompanyEmployeeId" :model="profileForm" label-width="100px" class="edit-grid-form">
                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="員工編號"><el-input v-model="profileForm.employee_id" disabled /></el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="帳號"><el-input v-model="profileForm.account" disabled /></el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="姓名"><el-input v-model="profileForm.name" /></el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="電子郵件"><el-input v-model="profileForm.email" type="email" /></el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="性別">
                        <el-select v-model="profileForm.gender" style="width: 100%">
                          <el-option label="男" value="M" />
                          <el-option label="女" value="F" />
                          <el-option label="其他" value="O" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="出生日期"><el-date-picker v-model="profileForm.birthday" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="身分證字號"><el-input v-model="profileForm.id_number" /></el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="聯絡電話"><el-input v-model="profileForm.phone" /></el-form-item>
                    </el-col>
                  </el-row>

                  <el-form-item label="地址">
                    <el-input v-model="profileForm.address" type="textarea" rows="2" placeholder="輸入完整地址" />
                  </el-form-item>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="緊急聯絡人"><el-input v-model="profileForm.emergency_contact" /></el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="聯絡電話"><el-input v-model="profileForm.emergency_phone" /></el-form-item>
                    </el-col>
                  </el-row>

                  <el-divider />

                  <div class="section-title">職位資訊</div>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="部門">
                        <el-select v-model="profileForm.department" clearable style="width: 100%">
                          <el-option v-for="department in departments" :key="department.id" :label="department.name" :value="department.id" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="職稱"><el-input v-model="profileForm.job_title" placeholder="e.g. 工程師" /></el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="主管">
                        <el-select v-model="profileForm.manager" clearable filterable style="width: 100%" placeholder="選擇直屬主管">
                          <el-option v-for="manager in allEmployees" :key="manager.id" :label="manager.name || manager.account" :value="manager.id" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="員工類型">
                        <el-select v-model="profileForm.emp_type" style="width: 100%">
                          <el-option label="全職" value="full_time" />
                          <el-option label="兼職" value="part_time" />
                          <el-option label="實習" value="intern" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="員工狀態">
                        <el-select v-model="profileForm.status" style="width: 100%">
                          <el-option label="在職" value="active" />
                          <el-option label="離職" value="resigned" />
                          <el-option label="留停" value="on_leave" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="職位階層">
                        <el-input-number v-model="profileForm.position_level" :min="1" style="width: 100%" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="到職日"><el-date-picker v-model="profileForm.hire_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="離職日"><el-date-picker v-model="profileForm.resignation_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
                    </el-col>
                  </el-row>

                  <div class="form-actions">
                    <el-button type="primary" :loading="companyEditSaving" :disabled="!selectedCompanyEmployeeId" @click="updateCompanyEmployee" size="large">
                      <span>💾 儲存員工資料</span>
                    </el-button>
                    <el-button @click="selectedCompanyEmployeeId = null" size="large">清除選擇</el-button>
                  </div>
                </el-form>
              </div>
            </div>
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
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-card {
  max-width: 460px;
  margin: 60px auto;
  border: none;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.dashboard-wrap {
  min-height: 100vh;
  padding: 24px;
}

.top-card {
  margin-bottom: 24px;
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  background: white;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.header-row h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.header-row p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #9ca3af;
}

/* 員工管理容器 */
.employee-manager-container {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  min-height: calc(100vh - 200px);
}

.filter-sidebar {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: fit-content;
  position: sticky;
  top: 24px;
}

.sidebar-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.sidebar-alert {
  margin-bottom: 20px;
  border-radius: 8px;
}

.filter-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.employee-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 0;
}

.employee-name {
  font-weight: 500;
  color: #1f2937;
}

.employee-id {
  font-size: 12px;
  color: #9ca3af;
}

.filter-stats {
  margin-top: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 4px solid #667eea;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.stat-count {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.edit-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.content-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.empty-state {
  padding: 60px 20px;
}

.edit-grid-form {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 20px 0 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.auth-switch {
  margin-bottom: 16px;
}

.readonly-tip {
  margin-top: 14px;
}

.manager-alert {
  margin-bottom: 14px;
}

.auth-form {
  margin-bottom: 12px;
}

.full-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
  font-weight: 500;
}

.grid-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 12px;
}

.selector-form {
  margin-bottom: 4px;
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

/* Element Plus 自訂覆蓋 */
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

:deep(.el-input__wrapper) {
  border-radius: 6px;
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

@media (max-width: 1200px) {
  .employee-manager-container {
    grid-template-columns: 1fr;
  }

  .filter-sidebar {
    position: static;
  }
}

@media (max-width: 900px) {
  .dashboard-wrap {
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

  .edit-content {
    padding: 16px;
  }
}
</style>
