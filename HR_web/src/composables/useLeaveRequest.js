import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/**
 * 請假相關邏輯的 Composable
 * 可被 PersonalDashboard.vue 和 DashView.vue 共用
 */
export function useLeaveRequest() {
  const leaveRequests = ref([])
  const leaveRequestDialogVisible = ref(false)
  const leaveForm = ref({
    leave_type: '',
    start_date: null,
    end_date: null,
    reason: ''
  })

  // 假別選項（與後端模型對應）
  const leaveTypeOptions = [
    { label: '特休', value: 'annual' },
    { label: '病假', value: 'sick' },
    { label: '事假', value: 'personal' },
    { label: '補休', value: 'compensatory' }
  ]

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

  const loadLeaveData = async () => {
    try {
      const res = await api.get('employees/leaves/')
      leaveRequests.value = res.data
    } catch (err) {
      ElMessage.error(parseError(err, '讀取請假記錄失敗'))
    }
  }

  const showLeaveDialog = () => {
    leaveRequestDialogVisible.value = true
    leaveForm.value = {
      leave_type: '',
      start_date: null,
      end_date: null,
      reason: ''
    }
  }

  const submitLeaveRequest = async () => {
    // 驗證必填字段
    if (!leaveForm.value.leave_type) {
      ElMessage.error('請選擇假別')
      return false
    }
    if (!leaveForm.value.start_date) {
      ElMessage.error('請選擇起始日')
      return false
    }
    if (!leaveForm.value.end_date) {
      ElMessage.error('請選擇結束日')
      return false
    }
    if (leaveForm.value.start_date > leaveForm.value.end_date) {
      ElMessage.error('結束日不能早於起始日')
      return false
    }
    if (!leaveForm.value.reason.trim()) {
      ElMessage.error('請填寫請假原因')
      return false
    }

    try {
      // 調用 POST /employees/leaves/ API
      await api.post('employees/leaves/', {
        leave_type: leaveForm.value.leave_type,
        start_date: leaveForm.value.start_date,
        end_date: leaveForm.value.end_date,
        reason: leaveForm.value.reason
      })

      ElMessage.success('請假申請已送出，等待主管核准')
      leaveRequestDialogVisible.value = false

      // 重新加載請假列表
      await loadLeaveData()
      return true
    } catch (err) {
      ElMessage.error(parseError(err, '提交請假申請失敗'))
      return false
    }
  }

  const resetForm = () => {
    leaveForm.value = {
      leave_type: '',
      start_date: null,
      end_date: null,
      reason: ''
    }
  }

  return {
    // State
    leaveRequests,
    leaveRequestDialogVisible,
    leaveForm,
    leaveTypeOptions,
    // Methods
    showLeaveDialog,
    submitLeaveRequest,
    loadLeaveData,
    resetForm,
    parseError
  }
}
