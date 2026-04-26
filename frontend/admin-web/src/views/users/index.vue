<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <span>用户管理</span>
      </template>
      
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="手机号/昵称" clearable />
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="filters.riskLevel" placeholder="全部" clearable>
            <el-option label="红色" value="red" />
            <el-option label="橙色" value="orange" />
            <el-option label="黄色" value="yellow" />
            <el-option label="绿色" value="green" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="userList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="riskLevel" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.riskLevel)">
              {{ getRiskText(row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginAt" label="最后登录" width="180" />
        <el-table-column prop="createdAt" label="注册时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewUser(row.id)">查看</el-button>
            <el-button type="warning" link @click="viewUserAlerts(row.id)">预警</el-button>
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
  keyword: '',
  riskLevel: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const userList = ref([
  { id: 1, phone: '138****1234', nickname: '小明', riskLevel: 'green', lastLoginAt: '2024-01-15 10:30:00', createdAt: '2024-01-01 09:00:00', status: 'active' },
  { id: 2, phone: '139****5678', nickname: '小红', riskLevel: 'yellow', lastLoginAt: '2024-01-15 09:45:00', createdAt: '2024-01-02 14:30:00', status: 'active' },
  { id: 3, phone: '137****9012', nickname: '小华', riskLevel: 'orange', lastLoginAt: '2024-01-14 16:20:00', createdAt: '2024-01-03 11:15:00', status: 'active' },
])

function getRiskType(level: string) {
  const types: Record<string, string> = { red: 'danger', orange: 'warning', yellow: 'info', green: 'success' }
  return types[level] || 'info'
}

function getRiskText(level: string) {
  const texts: Record<string, string> = { red: '红色', orange: '橙色', yellow: '黄色', green: '绿色' }
  return texts[level] || level
}

async function fetchList() {
  loading.value = true
  try {
    // TODO: 调用API
    pagination.total = 100
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchList()
}

function resetFilters() {
  filters.keyword = ''
  filters.riskLevel = ''
  handleSearch()
}

function viewUser(id: number) {
  router.push(`/users/${id}`)
}

function viewUserAlerts(id: number) {
  router.push({ path: '/alerts', query: { userId: id } })
}

onMounted(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
.users-page {
  .filter-form {
    margin-bottom: 20px;
  }
}
</style>
