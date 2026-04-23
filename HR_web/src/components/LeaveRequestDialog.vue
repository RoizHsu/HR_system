<template>
  <div class="leave-request-section">
    <!-- 新增請假按鈕 -->
    <div class="section-actions">
      <div class="clock-buttons">
        <el-button type="primary" @click="showLeaveDialog">新增請假</el-button>
      </div>
    </div>

    <!-- 請假記錄表格 -->
    <el-table :data="leaveRequests">
      <el-table-column prop="leave_type" label="假別" />
      <el-table-column prop="start_date" label="起始日" />
      <el-table-column prop="end_date" label="結束日" />
      <el-table-column prop="status" label="狀態" />
      <el-table-column prop="reason" label="原因" />
    </el-table>

    <!-- 主管審核區（如果有待審核項目） -->
    <template v-if="showApprovalSection">
      <el-divider>主管審核區</el-divider>
      <el-table :data="managerPendingLeaves">
        <el-table-column prop="employee_name" label="員工" />
        <el-table-column prop="leave_type" label="假別" />
        <el-table-column prop="start_date" label="起始日" />
        <el-table-column prop="end_date" label="結束日" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="success" size="small" @click="handleApprove(scope.row.id)">核准</el-button>
            <el-button type="danger" size="small" @click="handleReject(scope.row.id)">拒絕</el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <!-- 新增請假 Dialog -->
    <el-dialog v-model="leaveRequestDialogVisible" title="新增請假申請" width="600px" @close="resetForm">
      <el-form :model="leaveForm" label-width="100px" style="padding: 0 20px;">
        <!-- 假別選擇 -->
        <el-form-item label="假別">
          <el-select v-model="leaveForm.leave_type" placeholder="請選擇假別">
            <el-option v-for="option in leaveTypeOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>

        <!-- 起始日 -->
        <el-form-item label="起始日">
          <el-date-picker
            v-model="leaveForm.start_date"
            type="date"
            placeholder="選擇起始日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <!-- 結束日 -->
        <el-form-item label="結束日">
          <el-date-picker
            v-model="leaveForm.end_date"
            type="date"
            placeholder="選擇結束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <!-- 原因 -->
        <el-form-item label="請假原因">
          <el-input
            v-model="leaveForm.reason"
            type="textarea"
            :rows="4"
            placeholder="請填寫請假原因"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span>
          <el-button @click="leaveRequestDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitLeaveRequest">提交申請</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLeaveRequest } from '../composables/useLeaveRequest'
import { useLeaveApproval } from '../composables/useLeaveApproval'

// 從 Composable 導入
const {
  leaveRequests,
  leaveRequestDialogVisible,
  leaveForm,
  leaveTypeOptions,
  showLeaveDialog,
  submitLeaveRequest,
  loadLeaveData,
  resetForm
} = useLeaveRequest()

const {
  managerPendingLeaves,
  approveLeave,
  rejectLeave,
  loadManagerPendingLeaves
} = useLeaveApproval()

// 定義 Props
const props = defineProps({
  showApproval: {
    type: Boolean,
    default: false
  }
})

// 定義 Emits（告訴父組件發生了什麼）
const emit = defineEmits(['submitted', '已核准', 'approved', '已拒絕', 'rejected'])

// 計算屬性：是否顯示審核區
const showApprovalSection = computed(() => props.showApproval)

// 提交請假申請
const handleSubmitLeaveRequest = async () => {
  const success = await submitLeaveRequest()
  if (success) {
    // 觸發父組件刷新其他數據
    emit('submitted')
  }
}

// 核准請假
const handleApprove = async (leaveId) => {
  const success = await approveLeave(leaveId)
  if (success) {
    emit('已核准')
    emit('approved')
  }
}

// 拒絕請假
const handleReject = async (leaveId) => {
  const success = await rejectLeave(leaveId)
  if (success) {
    emit('已拒絕')
    emit('rejected')
  }
}

// 暴露給父組件的方法
const loadData = async () => {
  // 加載員工的請假記錄
  try {
    await loadLeaveData()
  } catch (err) {
    console.error('加載請假記錄失敗:', err)
  }

  // 如果需要顯示主管審核區，加載主管待審核的請假
  if (props.showApproval) {
    try {
      await loadManagerPendingLeaves()
    } catch (err) {
      console.error('加載主管待審核請假失敗:', err)
    }
  }
}

defineExpose({ loadData })
</script>

<style scoped>
.leave-request-section {
  width: 100%;
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
</style>
