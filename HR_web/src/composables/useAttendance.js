import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/**
 * 打卡相關邏輯的 Composable
 * 可被 PersonalDashboard.vue 和 DashView.vue 共用
 */
export function useAttendance() {
  const attendanceRecords = ref([])
  const attendanceToday = ref({ has_clock_in: false, clocked_out: false, record: null })
  const earlyLeaveDialogVisible = ref(false)
  const noteInput = ref('')

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

  const loadAttendanceData = async () => {
    try {
      const [attendanceRes, attendanceTodayRes] = await Promise.all([
        api.get('employees/attendance/'),
        api.get('employees/attendance/today-status/')
      ])

      attendanceRecords.value = attendanceRes.data
      attendanceToday.value = attendanceTodayRes.data
    } catch (err) {
      ElMessage.error(parseError(err, '讀取打卡記錄失敗'))
    }
  }

  const clockIn = async () => {
    try {
      await api.post('employees/attendance/clock-in/')
      ElMessage.success('上班打卡成功')
      await loadAttendanceData()
    } catch (err) {
      ElMessage.error(parseError(err, '打卡失敗'))
    }
  }

  const clockOut = async (note = null) => {
    try {
      const payload = note ? { note } : {}
      await api.post('employees/attendance/clock-out/', payload)
      ElMessage.success('下班打卡成功')
      await loadAttendanceData()
    } catch (err) {
      ElMessage.error(parseError(err, '打卡失敗'))
    }
  }

  const showEarlyLeaveDialog = () => {
    earlyLeaveDialogVisible.value = true
    noteInput.value = ''
  }

  const submitEarlyLeave = async () => {
    if (!noteInput.value.trim()) {
      ElMessage.error('請填寫提早下班原因')
      return
    }
    await clockOut(noteInput.value)
    earlyLeaveDialogVisible.value = false
    noteInput.value = ''
  }

  return {
    // State
    attendanceRecords,
    attendanceToday,
    earlyLeaveDialogVisible,
    noteInput,
    // Methods
    clockIn,
    clockOut,
    showEarlyLeaveDialog,
    submitEarlyLeave,
    loadAttendanceData,
    parseError
  }
}
