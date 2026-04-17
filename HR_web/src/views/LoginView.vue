<template>
	<div class="login-page">
		<el-card class="login-card">
			<template #header>
				<div class="header-row">
					<h2>HR 員工管理系統</h2>
					<span>登入 / 註冊</span>
				</div>
			</template>

			<div v-if="!postLoginEmployee">
				<el-segmented
					v-model="authMode"
					class="auth-switch"
					:options="[
						{ label: '登入', value: 'login' },
						{ label: '註冊', value: 'register' }
					]"
				/>

				<el-form label-width="110px" class="auth-form" @submit.prevent="submitAuth">
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
						<el-date-picker v-model="authForm.birthday" type="date" value-format="YYYY-MM-DD" placeholder="請選擇出生日期" style="width: 100%" />
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
			</div>

			<div v-else class="post-login-panel">
				<el-alert
					title="登入成功"
					type="success"
					:closable="false"
					show-icon
					class="success-alert"
				/>

				<p class="welcome-text">歡迎，{{ postLoginEmployee.name || postLoginEmployee.account }}</p>

				<div class="action-row">
					<el-button @click="goHome">進入首頁</el-button>
					<el-button v-if="postLoginEmployee.can_manage_employee_data" type="primary" @click="goDashboard">
						進入 HR 後台
					</el-button>
				</div>
			</div>
		</el-card>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api, { setAuthToken } from '../api'

const router = useRouter()

const authMode = ref('login')
const authLoading = ref(false)
const postLoginEmployee = ref(null)

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

const handleRegister = async () => {
	const res = await api.post('employees/auth/register/', authForm.value)
	setAuthToken(res.data.token)
	localStorage.setItem('hr_employee', JSON.stringify(res.data.employee))
	postLoginEmployee.value = res.data.employee
	ElMessage.success('註冊成功')
}

const handleLogin = async () => {
	const payload = {
		account: authForm.value.account,
		password: authForm.value.password,
	}
	const res = await api.post('employees/auth/login/', payload)
	setAuthToken(res.data.token)
	localStorage.setItem('hr_employee', JSON.stringify(res.data.employee))
	postLoginEmployee.value = res.data.employee
	ElMessage.success('登入成功')
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
	}

	authLoading.value = true
	try {
		if (authMode.value === 'register') {
			await handleRegister()
		} else {
			await handleLogin()
		}
	} catch (err) {
		ElMessage.error(parseError(err, authMode.value === 'register' ? '註冊失敗' : '登入失敗'))
	} finally {
		authLoading.value = false
	}
}

const goDashboard = () => {
	router.push('/dashboard')
}

const goHome = () => {
	router.push('/')
}
</script>

<style scoped>
.login-page {
	min-height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 24px;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
	width: 100%;
	max-width: 520px;
	border: none;
	border-radius: 16px;
	box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.header-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 16px;
}

.header-row h2 {
	margin: 0;
}

.header-row span {
	color: #6b7280;
}

.auth-switch {
	margin-bottom: 16px;
}

.auth-form {
	margin-bottom: 0;
}

.full-btn {
	width: 100%;
}

.post-login-panel {
	padding-top: 8px;
}

.success-alert {
	margin-bottom: 16px;
}

.welcome-text {
	margin: 0 0 16px;
	font-size: 16px;
	color: #1f2937;
}

.action-row {
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
}

@media (max-width: 640px) {
	.header-row {
		flex-direction: column;
		align-items: flex-start;
	}

	.action-row {
		flex-direction: column;
	}

	.action-row .el-button {
		width: 100%;
	}
}
</style>
