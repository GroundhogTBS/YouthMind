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
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="userList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="age_group" label="年龄段" width="100" />
        <el-table-column prop="session_count" label="会话数" width="80" />
        <el-table-column prop="message_count" label="消息数" width="80" />
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk_level)">
              {{ getRiskText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_active" label="最后活跃" width="180">
          <template #default="{ row }">
            {{ formatTime(row.last_active) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
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
import { ElMessage } from 'element-plus'
import { api } from '@/api/request'

const router = useRouter()
const loading = ref(false)

const filters = reactive({
  keyword: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const userList = ref<any[]>([])

function getRiskType(level: string) {
  const types: Record<string, string> = { high: 'danger', medium: 'warning', low: 'success' }
  return types[level] || 'info'
}

function getRiskText(level: string) {
  const texts: Record<string, string> = { high: '高风险', medium: '中风险', low: '低风险' }
  return texts[level] || level
}

function formatTime(time: string) {
  if (!time) return ''
  return time.replace('T', ' ').substring(0, 19)
}

async function fetchList() {
  loading.value = true
  try {
    const data = await api.admin.getUsers(pagination.page, pagination.pageSize, filters.keyword)
    userList.value = data
    pagination.total = data.length
  } catch (e) {
    console.error('加载用户列表失败', e)
    ElMessage.error('加载用户列表失败')
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
  handleSearch()
}

function viewUser(id: string) {
  router.push(`/users/${id}`)
}

function viewUserAlerts(id: string) {
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
