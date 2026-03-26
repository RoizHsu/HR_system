<script setup>
import { ref, onMounted } from 'vue'
import api from './api'
import { ElMessage } from 'element-plus'

const employees = ref([])
const dialogVisible = ref(false) // 控制彈窗顯示
const loading = ref(false)

// 定義表單資料模型
const form = ref({
  employee_id: '',
  name: '',
  gender: '',
  id_number: '',
  birthday: null,
  phone: '',
  address: '',
  job_title: '',
  status: 'active',
  hire_date: null,
  emergency_contact: '',
  emergency_phone: ''
})

// 表單驗證
const validateForm = () => {
  if (!form.value.employee_id.trim()) {
    ElMessage.error('員工編號不能為空')
    return false
  }
  if (!form.value.name.trim()) {
    ElMessage.error('姓名不能為空')
    return false
  }
  if (!form.value.gender) {
    ElMessage.error('性別不能為空')
    return false
  }
  if (!form.value.id_number.trim()) {
    ElMessage.error('身分證號不能為空')
    return false
  }
  if (form.value.id_number.length > 10) {
    ElMessage.error('身分證號字數不超過 10')
    return false
  }
  if (!form.value.birthday) {
    ElMessage.error('生日不能為空')
    return false
  }
  if (!form.value.phone.trim()) {
    ElMessage.error('電話不能為空')
    return false
  }
  if (!form.value.address.trim()) {
    ElMessage.error('地址不能為空')
    return false
  }
  if (!form.value.job_title.trim()) {
    ElMessage.error('職稱不能為空')
    return false
  }
  if (!form.value.hire_date) {
    ElMessage.error('到職日不能為空')
    return false
  }
  if (!form.value.emergency_contact.trim()) {
    ElMessage.error('緊急聯絡人不能為空')
    return false
  }
  if (!form.value.emergency_phone.trim()) {
    ElMessage.error('緊急聯絡電話不能為空')
    return false
  }
  return true
}

// 取得員工列表
const fetchEmployees = async () => {
  loading.value = true
  try {
    const res = await api.get('employees/list/')
    employees.value = res.data
  } catch (err) {
    ElMessage.error('無法取得資料')
  } finally {
    loading.value = false
  }
}

// 提交新增員工
const handleSubmit = async () => {
  // 先驗證表單
  if (!validateForm()) {
    return
  }
  
  try {
    // 這裡調用 POST API (DRF 自動生成的)
    await api.post('employees/list/', form.value)
    ElMessage.success('新增成功！')
    dialogVisible.value = false // 關閉彈窗
    fetchEmployees() // 重新整理列表
    // 重置表單
    form.value = { employee_id: '', name: '', gender: '', id_number: '', birthday: null, phone: '', address: '', job_title: '', status: 'active', hire_date: null, emergency_contact: '', emergency_phone: '' }
  } catch (err) {
    // 打印詳細的後端錯誤信息到控制台
    console.error('=== API 錯誤詳情 ===')
    console.error('完整響應:', err.response?.data)
    console.error('狀態碼:', err.response?.status)
    console.error('發送的資料:', form.value)
    
    // 提取錯誤訊息（DRF 通常返回欄位級別的錯誤）
    const responseData = err.response?.data
    let errorMsg = '新增失敗，請檢查資料格式'
    
    if (typeof responseData === 'object') {
      // 如果有欄位級別的錯誤
      const fieldErrors = Object.entries(responseData)
        .filter(([key, val]) => val && val.length > 0)
        .map(([field, errors]) => `${field}: ${errors[0]}`)
      
      if (fieldErrors.length > 0) {
        errorMsg = fieldErrors.join('; ')
      } else if (responseData.detail) {
        errorMsg = responseData.detail
      } else if (responseData.non_field_errors?.[0]) {
        errorMsg = responseData.non_field_errors[0]
      }
    }
    
    ElMessage.error(errorMsg)
  }
}

onMounted(fetchEmployees)
</script>

<template>
  <div style="padding: 30px;">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="margin: 0;">HR 員工管理系統</h2>
          <el-button type="primary" @click="dialogVisible = true">新增員工</el-button>
        </div>
      </template>

      <el-table :data="employees" v-loading="loading" style="width: 100%">
        <el-table-column prop="employee_id" label="編號" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="department_name" label="部門" />
        <el-table-column prop="job_title" label="職稱" />
        <el-table-column prop="status" label="狀態">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '在職' : '離職' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hire_date" label="到職日" />
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增員工資料" width="700px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="員工編號">
          <el-input v-model="form.employee_id" placeholder="例如: IT002" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="性別">
          <el-select v-model="form.gender" style="width: 100%">
            <el-option label="男" value="M" />
            <el-option label="女" value="F" />
            <el-option label="其他" value="O" />
          </el-select>
        </el-form-item>
        <el-form-item label="身分證號">
          <el-input v-model="form.id_number" placeholder="請勿超過 10 個字元" maxlength="10" />
        </el-form-item>
        <el-form-item label="生日">
          <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="電話">
          <el-input v-model="form.phone" placeholder="例如: 0912345678" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="職稱">
          <el-input v-model="form.job_title" />
        </el-form-item>
        <el-form-item label="到職日">
          <el-date-picker v-model="form.hire_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="狀態">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="在職" value="active" />
            <el-option label="離職" value="resigned" />
          </el-select>
        </el-form-item>
        <el-form-item label="緊急聯絡人">
          <el-input v-model="form.emergency_contact" />
        </el-form-item>
        <el-form-item label="緊急聯絡電話">
          <el-input v-model="form.emergency_phone" placeholder="例如: 0912345678" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">確認新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>