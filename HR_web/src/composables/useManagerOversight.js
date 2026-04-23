import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/**
 * HR/管理者審核相關邏輯的 Composable
 * DashView.vue 獨有（PersonalDashboard.vue 不需要）
 */
export function useManagerOversight() {
  const managerPendingOvertimes = ref([])

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

  const loadManagerPendingOvertimes = async () => {
    try {
      const res = await api.get('employees/overtimes/pending-approvals/')
      managerPendingOvertimes.value = res.data
    } catch (err) {
      console.error('讀取待審核加班失敗:', err)
      managerPendingOvertimes.value = []
    }
  }

  const approveOvertime = async (overtimeId) => {
    try {
      await api.post(`employees/overtimes/${overtimeId}/approve/`)
      ElMessage.success('已核准加班申請')
      await loadManagerPendingOvertimes()
      return true
    } catch (err) {
      ElMessage.error(parseError(err, '核准加班申請失敗'))
      return false
    }
  }

  const rejectOvertime = async (overtimeId) => {
    try {
      await api.post(`employees/overtimes/${overtimeId}/reject/`)
      ElMessage.success('已拒絕加班申請')
      await loadManagerPendingOvertimes()
      return true
    } catch (err) {
      ElMessage.error(parseError(err, '拒絕加班申請失敗'))
      return false
    }
  }

  return {
    // State
    managerPendingOvertimes,
    // Methods
    loadManagerPendingOvertimes,
    approveOvertime,
    rejectOvertime,
    parseError
  }
}
