<template>
  <div class="early-leave-section">
    <!-- 打卡資訊 Alert -->
    <el-alert
      :title="attendanceToday.has_clock_in ? (attendanceToday.clocked_out ? '今日已完成上下班打卡' : '今日已打卡上班，尚未下班打卡') : '今日尚未打卡'"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 14px;"
    />

    <!-- 打卡按鈕 -->
    <div class="clock-buttons">
      <el-button type="primary" :disabled="attendanceToday.has_clock_in && !attendanceToday.clocked_out" @click="clockIn">上班打卡</el-button>
      <el-button type="success" :disabled="!attendanceToday.has_clock_in || attendanceToday.clocked_out" @click="clockOut()">下班打卡</el-button>
      <el-button type="warning" :disabled="!attendanceToday.has_clock_in || attendanceToday.clocked_out" @click="showEarlyLeaveDialog">提早下班</el-button>
    </div>

    <!-- 提早下班備註 Dialog -->
    <el-dialog v-model="earlyLeaveDialogVisible" title="提早下班申請" width="500px" @close="noteInput = ''">
      <div style="padding: 20px 0;">
        <p style="margin-bottom: 20px; color: #333;">
          請說明提早下班的原因：
        </p>
        <el-input
          v-model="noteInput"
          type="textarea"
          rows="4"
          placeholder="例：身體不適、家中有急事、其他..."
          clearable
        />
      </div>
      <template #footer>
        <span>
          <el-button @click="earlyLeaveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitEarlyLeave">確認下班</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 打卡記錄表格 -->
    <div style="margin-top: 20px;">
      <h3 style="margin-bottom: 12px; font-size: 14px; color: #374151; font-weight: 600;">打卡記錄</h3>
      <el-table :data="attendanceRecords">
        <el-table-column prop="clock_in" label="上班打卡" />
        <el-table-column prop="clock_out" label="下班打卡" />
        <el-table-column prop="note" label="備註" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { useAttendance } from '../composables/useAttendance'

// 從 Composable 導入
const {
  attendanceRecords,
  attendanceToday,
  earlyLeaveDialogVisible,
  noteInput,
  clockIn,
  clockOut,
  showEarlyLeaveDialog,
  submitEarlyLeave,
  loadAttendanceData
} = useAttendance()

// 定義 Emits
const emit = defineEmits(['submitted'])

// 提交提早下班
const handleSubmitEarlyLeave = async () => {
  const success = await submitEarlyLeave()
  if (success) {
    emit('submitted')
  }
}

// 暴露給父組件的方法
const loadData = async () => {
  await loadAttendanceData()
}

defineExpose({ loadData })
</script>

<style scoped>
.early-leave-section {
  width: 100%;
}

.clock-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

:deep(.el-button--success) {
  background-color: #67c23a;
  border-color: #67c23a;
}

:deep(.el-button--warning) {
  background-color: #e6a23c;
  border-color: #e6a23c;
}
</style>
