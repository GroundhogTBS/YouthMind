<template>
  <div class="alerts-page">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>预警管理</span>
          <el-button type="primary" @click="loadAlerts">刷新</el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="filters.status" placeholder="状态" clearable @change="loadAlerts">
          <el-option label="待处理" value="unhandled" />
          <el-option label="已处理" value="handled" />
        </el-select>
        <el-select v-model="filters.riskLevel" placeholder="风险等级" clearable @change="loadAlerts" style="margin-left: 10px;">
          <el-option label="红色" value="red" />
          <el-option label="橙色" value="orange" />
          <el-option label="黄色" value="yellow" />
        </el-select>
      </div>
      
      <el-table :data="alerts" style="width: 100%; margin-top: 16px;" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.risk_level)">
              {{ getLevelText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="risk_score" label="风险分" width="80" />
        <el-table-column prop="matched_keywords" label="匹配关键词" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatKeywords(row.matched_keywords) }}
          </template>
        </el-table-column>
        <el-table-column prop="session_id" label="会话ID" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="handled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.handled ? 'success' : 'warning'">
              {{ row.handled ? '已处理' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
            <el-button 
              v-if="!row.handled" 
              type="success" 
              link 
              @click="handleAlert(row)"
            >处理</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadAlerts"
        @current-change="loadAlerts"
        style="margin-top: 16px; justify-content: flex-end;"
      />
    </el-card>
    
    <el-dialog v-model="detailVisible" title="预警详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ currentAlert?.id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentAlert?.user_id }}</el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="getLevelType(currentAlert?.risk_level)">
            {{ getLevelText(currentAlert?.risk_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险分数">{{ currentAlert?.risk_score }}</el-descriptions-item>
        <el-descriptions-item label="会话ID">{{ currentAlert?.session_id }}</el-descriptions-item>
        <el-descriptions-item label="消息ID">{{ currentAlert?.message_id }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatTime(currentAlert?.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="匹配关键词" :span="2">
          {{ formatKeywords(currentAlert?.matched_keywords) }}
        </el-descriptions-item>
        <el-descriptions-item label="处理状态" :span="2">
          <el-tag :type="currentAlert?.handled ? 'success' : 'warning'">
            {{ currentAlert?.handled ? '已处理' : '待处理' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentAlert?.handled_at" label="处理时间" :span="2">
          {{ formatTime(currentAlert?.handled_at) }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentAlert?.notes" label="处理备注" :span="2">
          {{ currentAlert?.notes }}
        </el-descriptions-item>
      </el-descriptions>
      
      <div v-if="!currentAlert?.handled" style="margin-top: 20px;">
        <el-input
          v-model="handleNotes"
          type="textarea"
          :rows="3"
          placeholder="请输入处理备注..."
        />
        <el-button type="primary" style="margin-top: 10px;" @click="submitHandle">
          标记为已处理
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api/request'

const loading = ref(false)
const alerts = ref<any[]>([])
const detailVisible = ref(false)
const currentAlert = ref<any>(null)
const handleNotes = ref('')

const filters = reactive({
  status: '',
  riskLevel: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
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

function formatKeywords(keywords: string) {
  if (!keywords) return ''
  try {
    const arr = JSON.parse(keywords)
    return arr.join(', ')
  } catch {
    return keywords
  }
}

async function loadAlerts() {
  loading.value = true
  try {
    const data = await api.admin.getCrisisEvents(
      filters.status,
      filters.riskLevel,
      pagination.page,
      pagination.pageSize
    )
    alerts.value = data
    pagination.total = data.length
  } catch (e) {
    console.error('加载预警失败', e)
    ElMessage.error('加载预警列表失败')
  } finally {
    loading.value = false
  }
}

function viewDetail(row: any) {
  currentAlert.value = row
  handleNotes.value = ''
  detailVisible.value = true
}

async function handleAlert(row: any) {
  currentAlert.value = row
  handleNotes.value = ''
  detailVisible.value = true
}

async function submitHandle() {
  if (!currentAlert.value) return
  
  try {
    await api.admin.handleCrisis(currentAlert.value.id, handleNotes.value)
    ElMessage.success('处理成功')
    detailVisible.value = false
    loadAlerts()
  } catch (e) {
    console.error('处理失败', e)
    ElMessage.error('处理失败')
  }
}

onMounted(() => {
  loadAlerts()
})
</script>

<style lang="scss" scoped>
.alerts-page {
  .filter-bar {
    display: flex;
    align-items: center;
  }
}
</style>
