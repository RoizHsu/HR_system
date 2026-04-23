<template>
	<div class="dashboard-page" v-loading="pageLoading">
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
					<EarlyLeaveDialog ref="earlyLeaveDialogRef" @submitted="loadDashboardData" />
				</el-tab-pane>

				<el-tab-pane label="休假管理" name="leaves">
					<LeaveRequestDialog ref="leaveRequestDialogRef" :show-approval="true" @submitted="loadDashboardData" @approved="loadDashboardData" @rejected="loadDashboardData" />
				</el-tab-pane>

				<el-tab-pane label="加班紀錄" name="overtimes">
					<OvertimeApprovalTable ref="overtimeApprovalTableRef" :show-approval="true" @submitted="loadDashboardData" @approved="loadDashboardData" @rejected="loadDashboardData" />
				</el-tab-pane>

				<el-tab-pane v-if="canManageEmployeeData" label="公司員工資料修改" name="profile">
					<div class="employee-manager-container">
						<div class="filter-sidebar">
							<div class="sidebar-header">
								<h3>篩選選單</h3>
							</div>
							<el-alert title="僅限授權群組可使用" type="success" :closable="false" show-icon class="sidebar-alert" />
							<el-form label-width="0" class="filter-form">
								<div class="filter-group">
									<label class="filter-label">部門篩選</label>
									<el-select v-model="selectedCompanyDepartmentId" style="width: 100%" placeholder="全部部門" clearable @change="onCompanyDepartmentChange">
										<el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
									</el-select>
								</div>
								<div class="filter-group">
									<label class="filter-label">選擇員工</label>
									<el-select v-model="selectedCompanyEmployeeId" clearable filterable style="width: 100%" placeholder="搜尋員工" @change="onCompanyEmployeeChange">
										<el-option v-for="item in companyEditableEmployees" :key="item.id" :label="`${item.name || item.account}`" :value="item.id">
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
									<el-input v-model="profileForm.address" type="textarea" :rows="2" placeholder="輸入完整地址" />
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
									<el-button type="primary" :loading="companyEditSaving" :disabled="!selectedCompanyEmployeeId" @click="updateCompanyEmployee" size="large">💾 儲存員工資料</el-button>
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
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from '../api'
import EarlyLeaveDialog from '../components/EarlyLeaveDialog.vue'
import LeaveRequestDialog from '../components/LeaveRequestDialog.vue'
import OvertimeApprovalTable from '../components/OvertimeApprovalTable.vue'

const router = useRouter()

// 組件 Refs
const earlyLeaveDialogRef = ref(null)
const leaveRequestDialogRef = ref(null)
const overtimeApprovalTableRef = ref(null)

const pageLoading = ref(false)
const companyEditSaving = ref(false)
const activeTab = ref('overview')

const employee = ref(null)
const departments = ref([])
const allEmployees = ref([])
const selectedCompanyEmployeeId = ref(null)
const selectedCompanyDepartmentId = ref(null)

const orgDepartments = ref([])

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

const todayClockedInText = computed(() => {
	// 這個值會從 EarlyLeaveDialog 組件中取得
	// 暫時先保留用 ref
	return '是'
})

const hoursWorked = computed(() => {
	if (!attendanceToday.value.record?.clock_in) return 0
	const clockInTime = new Date(attendanceToday.value.record.clock_in)
	const now = new Date()
	return (now - clockInTime) / (1000 * 60 * 60)
})

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
		// 加載共享數據（打卡、請假、加班）
		await Promise.all([
			earlyLeaveDialogRef.value?.loadData(),
			leaveRequestDialogRef.value?.loadData(),
			overtimeApprovalTableRef.value?.loadData()
		])

		// 加載 HR 特有數據
		const [orgRes, deptRes, employeesRes] = await Promise.all([
			api.get('employees/org-chart/'),
			api.get('employees/departments/'),
			api.get('employees/list/')
		])

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
	localStorage.setItem('hr_employee', JSON.stringify(res.data))
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
	localStorage.removeItem('hr_employee')
	employee.value = null
	selectedCompanyEmployeeId.value = null
	selectedCompanyDepartmentId.value = null
	activeTab.value = 'overview'
	pageLoading.value = false
	companyEditSaving.value = false
	// 注：不直接清除composable的refs，讓它們在下次掛載時自動初始化
	router.push('/')
	ElMessage.success('已登出')
}

onMounted(async () => {
	const token = localStorage.getItem('hr_token')
	if (!token) {
		router.push('/login')
		return
	}

	try {
		await loadCurrentEmployee()
		await loadDashboardData()
		if (!canManageEmployeeData.value) {
			router.push('/')
			ElMessage.warning('只有 HR 人員可以進入後台')
		}
	} catch (err) {
		setAuthToken(null)
		localStorage.removeItem('hr_employee')
		employee.value = null
		router.push('/login')
	}
})
</script>

<style scoped>
.dashboard-page {
	min-height: 100vh;
	padding: 24px;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.readonly-tip {
	margin-top: 14px;
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
	.dashboard-page {
		padding: 14px;
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
