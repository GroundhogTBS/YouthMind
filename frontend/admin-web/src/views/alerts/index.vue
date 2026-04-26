<template>
  <div class="alerts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预警列表</span>
          <el-button type="primary" @click="refreshList">刷新</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="预警等级">
          <el-select v-model="filters.level" placeholder="全部" clearable>
            <el-option label="红色" value="red" />
            <el-option label="橙色" value="orange" />
            <el-option label="黄色" value="yellow" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="误报" value="false_positive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="alertList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="alertLevel" label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.alertLevel)">
              {{ getLevelText(row.alertLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alertType" label="类型" />
        <el-table-column prop="triggerSource" label="来源" width="100" />
        <el-table-column prop="triggerContent" label="触发内容" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewAlert(row.id)">查看</el-button>
            <el-button type="success" link @click="handleAlert(row.id)" v-if="row.status === 'pending'">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchList"
        @current-change="fetchList"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(false)

const filters = reactive({
  level: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const alertList = ref([
  { id: 1, userId: 101, alertLevel: 'red', alertType: 'crisis_intervention', triggerSource: 'chat', triggerContent: '用户表达了极端的想法...', createdAt: '2024-01-15 10:30:00', status: 'pending' },
  { id: 2, userId: 205, alertLevel: 'orange', alertType: 'high_risk_warning', triggerSource: 'assessment', triggerContent: 'PHQ-9评分达到中度抑郁...', createdAt: '2024-01-15 09:45:00', status: 'processing' },
  { id: 3, userId: 308, alertLevel: 'yellow', alertType: 'attention_needed', triggerSource: 'emotion', triggerContent: '连续多日情绪低落...', createdAt: '2024-01-15 08:20:00', status: 'resolved' },
])

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

async function fetchList() {
  loading.value = true
  try {
    // TODO: 调用API获取数据
    pagination.total = 100
  } finally {
    loading.value = false
  }
}

function refreshList() {
  fetchList()
}

function handleSearch() {
  pagination.page = 1
  fetchList()
}

function resetFilters() {
  filters.level = ''
  filters.status = ''
  handleSearch()
}

function viewAlert(id: number) {
  router.push(`/alerts/${id}`)
}

function handleAlert(id: number) {
  router.push(`/alerts/${id}`)
}

onMounted(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
.alerts-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .filter-form {
    margin-bottom: 20px;
  }
}
</style>
