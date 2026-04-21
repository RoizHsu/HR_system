import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/**
 * 加班相關邏輯的 Composable
 * 可被 PersonalDashboard.vue 和 DashView.vue 共用
 */
export function useOvertime() {
  const overtimeRecords = ref([])
  const overtimeApplyForm = ref({
    work_date: null,
    hours: 1,
    reason: ''
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

  const loadOvertimeData = async () => {
    try {
      const res = await api.get('employees/overtimes/')
      overtimeRecords.value = res.data
    } catch (err) {
      ElMessage.error(parseError(err, '讀取加班記錄失敗'))
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
      await loadOvertimeData()
    } catch (err) {
      ElMessage.error(parseError(err, '送出加班申請失敗'))
    }
  }

  const resetForm = () => {
    overtimeApplyForm.value = {
      work_date: null,
      hours: 1,
      reason: ''
    }
  }

  return {
    // State
    overtimeRecords,
    overtimeApplyForm,
    // Methods
    submitOvertime,
    loadOvertimeData,
    resetForm,
    parseError
  }
}
