<template>
  <div class="alert-detail-page" v-loading="loading">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button @click="goBack">返回</el-button>
          <span>预警详情 #{{ alertId }}</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="预警等级">
          <el-tag :type="getLevelType(alert.risk_level)" size="large">
            {{ getLevelText(alert.risk_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="alert.handled ? 'success' : 'warning'" size="large">
            {{ alert.handled ? '已处理' : '待处理' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ alert.user_id }}</el-descriptions-item>
        <el-descriptions-item label="会话ID">{{ alert.session_id }}</el-descriptions-item>
        <el-descriptions-item label="风险分数">{{ alert.risk_score }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(alert.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="匹配关键词" :span="2">
          <el-tag v-for="kw in parsedKeywords" :key="kw" style="margin-right: 8px;" type="danger">{{ kw }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="alert.handled_at" label="处理时间">{{ formatTime(alert.handled_at) }}</el-descriptions-item>
        <el-descriptions-item v-if="alert.notes" label="处理备注" :span="2">{{ alert.notes }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <el-card style="margin-top: 20px;" v-if="!alert.handled">
      <template #header>处理预警</template>
      <el-form :model="handleForm" label-width="100px">
        <el-form-item label="处理备注">
          <el-input v-model="handleForm.notes" type="textarea" :rows="4" placeholder="请输入处理备注..." />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitHandle">标记为已处理</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;" v-if="alert.handled && alert.notes">
      <template #header>处理记录</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="处理时间">{{ formatTime(alert.handled_at) }}</el-descriptions-item>
        <el-descriptions-item label="处理备注">{{ alert.notes }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/request'

const route = useRoute()
const router = useRouter()

const alertId = route.params.id as string
const loading = ref(false)

const alert = ref<any>({
  id: 0,
  user_id: '',
  session_id: '',
  risk_level: '',
  risk_score: 0,
  matched_keywords: '',
  handled: 0,
  handler_id: null,
  handled_at: null,
  notes: null,
  created_at: '',
})

const handleForm = reactive({
  notes: '',
})

const parsedKeywords = computed(() => {
  if (!alert.value.matched_keywords) return []
  try {
    return JSON.parse(alert.value.matched_keywords)
  } catch {
    return alert.value.matched_keywords.split(',')
  }
})

function getLevelType(level: string) {
  const types: Record<string, string> = { red: 'danger', orange: 'warning', yellow: 'info' }
  return types[level] || 'info'
}

function getLevelText(level: string) {
  const texts: Record<string, string> = { red: '红色', orange: '橙色', yellow: '黄色' }
  return texts[level] || level
}

function formatTime(time: string) {
  if (!time) return ''
  return time.replace('T', ' ').substring(0, 19)
}

function goBack() {
  router.back()
}

async function loadAlert() {
  loading.value = true
  try {
    const data = await api.admin.getCrisisEvents('', '', 1, 1000)
    const found = data.find((a: any) => a.id === parseInt(alertId))
    if (found) {
      alert.value = found
    } else {
      ElMessage.error('未找到该预警记录')
      router.back()
    }
  } catch (e) {
    console.error('加载预警详情失败', e)
    ElMessage.error('加载预警详情失败')
  } finally {
    loading.value = false
  }
}

async function submitHandle() {
  try {
    await api.admin.handleCrisis(parseInt(alertId), handleForm.notes)
    ElMessage.success('处理成功')
    alert.value.handled = 1
    alert.value.notes = handleForm.notes
    alert.value.handled_at = new Date().toISOString()
  } catch (e) {
    console.error('处理失败', e)
    ElMessage.error('处理失败')
  }
}

onMounted(() => {
  loadAlert()
})
</script>

<style lang="scss" scoped>
.alert-detail-page {
  .card-header {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}
</style>
