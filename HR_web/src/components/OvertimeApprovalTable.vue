<template>
  <div class="overtime-approval-section">
    <!-- 內部分頁 Tab -->
    <el-tabs v-model="activeInternalTab">
      <!-- 當月排班 -->
      <el-tab-pane label="當月排班" name="shifts">
        <el-table :data="shiftSchedules">
          <el-table-column prop="shift_date" label="日期" />
          <el-table-column prop="start_time" label="上班" />
          <el-table-column prop="end_time" label="下班" />
          <el-table-column prop="shift_type" label="班別" />
        </el-table>
      </el-tab-pane>

      <!-- 加班記錄 -->
      <el-tab-pane label="加班記錄" name="records">
        <!-- 加班申請卡片 -->
        <el-card class="inner-card" shadow="never">
          <template #header>提出加班申請</template>
          <el-form :inline="true" :model="overtimeApplyForm" class="overtime-form">
            <el-form-item label="日期">
              <el-date-picker v-model="overtimeApplyForm.work_date" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="時數">
              <el-input-number v-model="overtimeApplyForm.hours" :min="0.5" :step="0.5" />
            </el-form-item>
            <el-form-item label="原因">
              <el-input v-model="overtimeApplyForm.reason" placeholder="輸入加班原因" style="width: 280px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmitOvertime">送出申請</el-button>
            </el-form-item>
          </el-form>
          <p class="hint-text">主管若 12 小時內未處理，系統將自動核准。</p>
        </el-card>

        <!-- 加班記錄表格 -->
        <el-table :data="overtimeRecords" style="margin-top: 16px;">
          <el-table-column prop="work_date" label="日期" />
          <el-table-column prop="hours" label="時數" />
          <el-table-column prop="status" label="狀態" />
          <el-table-column prop="auto_approved" label="自動核准">
            <template #default="scope">{{ scope.row.auto_approved ? '是' : '否' }}</template>
          </el-table-column>
          <el-table-column prop="approved_by_name" label="核准主管" />
          <el-table-column prop="reason" label="原因" />
        </el-table>

        <!-- 主管審核區（如果有待審核項目） -->
        <template v-if="showApprovalSection">
          <el-divider>主管審核區</el-divider>
          <el-table :data="managerPendingOvertimes">
            <el-table-column prop="employee_name" label="員工" />
            <el-table-column prop="work_date" label="加班日期" />
            <el-table-column prop="hours" label="時數" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button type="success" size="small" @click="handleApprove(scope.row.id)">核准</el-button>
                <el-button type="danger" size="small" @click="handleReject(scope.row.id)">拒絕</el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useOvertime } from '../composables/useOvertime'
import { useManagerOversight } from '../composables/useManagerOversight'
import api from '../api'

// 從 Composables 導入
const {
  overtimeRecords,
  overtimeApplyForm,
  submitOvertime,
  loadOvertimeData
} = useOvertime()

const {
  managerPendingOvertimes,
  approveOvertime,
  rejectOvertime,
  loadManagerPendingOvertimes
} = useManagerOversight()

// 本組件 state
const activeInternalTab = ref('records')  // 內部 Tab 控制 - 默認開啟加班記錄
const shiftSchedules = ref([])

// 定義 Props
const props = defineProps({
  showApproval: {
    type: Boolean,
    default: false
  }
})

// 定義 Emits
const emit = defineEmits(['submitted', '已核准', 'approved', '已拒絕', 'rejected'])

// 計算屬性：是否顯示審核區
const showApprovalSection = computed(() => props.showApproval && managerPendingOvertimes.value.length > 0)

// 提交加班申請
const handleSubmitOvertime = async () => {
  const success = await submitOvertime()
  if (success) {
    emit('submitted')
  }
}

// 核准加班
const handleApprove = async (overtimeId) => {
  const success = await approveOvertime(overtimeId)
  if (success) {
    emit('已核准')
    emit('approved')
  }
}

// 拒絕加班
const handleReject = async (overtimeId) => {
  const success = await rejectOvertime(overtimeId)
  if (success) {
    emit('已拒絕')
    emit('rejected')
  }
}

// 暴露給父組件的方法 - 分別加載數據，確保主管審核區能顯示
const loadData = async () => {
  // 加載排班資訊
  try {
    const shiftsRes = await api.get('employees/shifts/')
    shiftSchedules.value = shiftsRes.data
  } catch (err) {
    console.error('加載排班資訊失敗:', err)
    shiftSchedules.value = []
  }

  // 加載員工的加班記錄
  try {
    await loadOvertimeData()
  } catch (err) {
    console.error('加載加班記錄失敗:', err)
  }

  // 如果需要顯示主管審核區，分別加載主管待審核的加班
  if (props.showApproval) {
    try {
      await loadManagerPendingOvertimes()
    } catch (err) {
      console.error('加載主管待審核加班失敗:', err)
    }
  }
}

defineExpose({ loadData })
</script>

<style scoped>
.overtime-approval-section {
  width: 100%;
}

.inner-card {
  margin-bottom: 14px;
  border: none;
  border-radius: 12px;
}

.overtime-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hint-text {
  margin: 2px 0 0;
  color: #68758a;
  font-size: 12px;
}

:deep(.el-card) {
  border: none;
  border-radius: 12px;
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

:deep(.el-button--danger) {
  background-color: #f56c6c;
  border-color: #f56c6c;
}
</style>
