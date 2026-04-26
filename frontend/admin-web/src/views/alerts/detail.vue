<template>
  <div class="alert-detail-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button @click="goBack">返回</el-button>
          <span>预警详情 #{{ alertId }}</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="预警等级">
          <el-tag :type="getLevelType(alert.alertLevel)" size="large">
            {{ getLevelText(alert.alertLevel) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(alert.status)" size="large">
            {{ getStatusText(alert.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ alert.userId }}</el-descriptions-item>
        <el-descriptions-item label="预警类型">{{ alert.alertType }}</el-descriptions-item>
        <el-descriptions-item label="触发来源">{{ alert.triggerSource }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ alert.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="风险关键词" :span="2">
          <el-tag v-for="kw in alert.riskKeywords" :key="kw" style="margin-right: 8px;">{{ kw }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="触发内容" :span="2">
          <div class="trigger-content">{{ alert.triggerContent }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="置信度">{{ (alert.confidenceScore * 100).toFixed(1) }}%</el-descriptions-item>
        <el-descriptions-item label="处理人">{{ alert.handlerName || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <el-card style="margin-top: 20px;" v-if="alert.status === 'pending'">
      <template #header>处理预警</template>
      <el-form :model="handleForm" label-width="100px">
        <el-form-item label="处理状态">
          <el-select v-model="handleForm.status" placeholder="请选择">
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="误报" value="false_positive" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理结果">
          <el-input v-model="handleForm.handleResult" type="textarea" :rows="3" placeholder="请输入处理结果" />
        </el-form-item>
        <el-form-item label="后续跟进">
          <el-input v-model="handleForm.followUpPlan" type="textarea" :rows="3" placeholder="请输入后续跟进计划" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitHandle">提交处理</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;" v-if="alert.handleResult">
      <template #header>处理记录</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="处理人">{{ alert.handlerName }}</el-descriptions-item>
        <el-descriptions-item label="处理时间">{{ alert.handleTime }}</el-descriptions-item>
        <el-descriptions-item label="处理结果">{{ alert.handleResult }}</el-descriptions-item>
        <el-descriptions-item label="后续跟进">{{ alert.followUpPlan || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const alertId = route.params.id

const alert = ref({
  id: 1,
  userId: 101,
  alertLevel: 'red',
  alertType: 'crisis_intervention',
  triggerSource: 'chat',
  triggerContent: '用户在对话中表达了极端的想法，提到"不想活了"、"活着没有意义"等内容，需要立即关注。',
  riskKeywords: ['不想活', '没有意义'],
  confidenceScore: 0.85,
  status: 'pending',
  createdAt: '2024-01-15 10:30:00',
  handleResult: '',
  followUpPlan: '',
  handlerName: '',
  handleTime: '',
})

const handleForm = reactive({
  status: 'processing',
  handleResult: '',
  followUpPlan: '',
})

function getLevelType(level: string) {
  const types: Record<string, string> = { red: 'danger', orange: 'warning', yellow: 'info' }
  return types[level] || 'info'
}

function getLevelText(level: string) {
  const texts: Record<string, string> = { red: '红色', orange: '橙色', yellow: '黄色' }
  return texts[level] || level
}

function getStatusType(status: string) {
  const types: Record<string, string> = { pending: 'warning', processing: 'primary', resolved: 'success', false_positive: 'info' }
  return types[status] || 'info'
}

function getStatusText(status: string) {
  const texts: Record<string, string> = { pending: '待处理', processing: '处理中', resolved: '已解决', false_positive: '误报' }
  return texts[status] || status
}

function goBack() {
  router.back()
}

async function submitHandle() {
  if (!handleForm.handleResult) {
    ElMessage.warning('请输入处理结果')
    return
  }
  
  // TODO: 调用API提交处理
  ElMessage.success('处理成功')
  alert.value.status = handleForm.status
  alert.value.handleResult = handleForm.handleResult
  alert.value.followUpPlan = handleForm.followUpPlan
  alert.value.handlerName = '管理员'
  alert.value.handleTime = new Date().toLocaleString()
}

onMounted(() => {
  // TODO: 加载预警详情
})
</script>

<style lang="scss" scoped>
.alert-detail-page {
  .card-header {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .trigger-content {
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    line-height: 1.6;
  }
}
</style>
