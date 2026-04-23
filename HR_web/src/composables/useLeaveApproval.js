import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/**
 * 主管審核請假的 Composable
 * DashView.vue 獨有（PersonalDashboard.vue 不需要）
 */
export function useLeaveApproval() {
  const managerPendingLeaves = ref([])

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

  const loadManagerPendingLeaves = async () => {
    try {
      const res = await api.get('employees/leaves/pending-approvals/')
      managerPendingLeaves.value = res.data
    } catch (err) {
      // 如果後端端點還沒實現（404），就保持空陣列，不報錯
      if (err.response?.status === 404) {
        console.warn('後端還未提供請假審核端點 (pending-approvals)')
        managerPendingLeaves.value = []
      } else {
        console.error('讀取待審核請假失敗:', err)
        managerPendingLeaves.value = []
      }
    }
  }

  const approveLeave = async (leaveId) => {
    try {
      await api.post(`employees/leaves/${leaveId}/approve/`)
      ElMessage.success('已核准請假申請')
      await loadManagerPendingLeaves()
      return true
    } catch (err) {
      if (err.response?.status === 404) {
        ElMessage.warning('後端還未提供請假審核功能')
      } else {
        ElMessage.error(parseError(err, '核准請假申請失敗'))
      }
      return false
    }
  }

  const rejectLeave = async (leaveId) => {
    try {
      await api.post(`employees/leaves/${leaveId}/reject/`)
      ElMessage.success('已拒絕請假申請')
      await loadManagerPendingLeaves()
      return true
    } catch (err) {
      if (err.response?.status === 404) {
        ElMessage.warning('後端還未提供請假審核功能')
      } else {
        ElMessage.error(parseError(err, '拒絕請假申請失敗'))
      }
      return false
    }
  }

  return {
    // State
    managerPendingLeaves,
    // Methods
    loadManagerPendingLeaves,
    approveLeave,
    rejectLeave,
    parseError
  }
}
