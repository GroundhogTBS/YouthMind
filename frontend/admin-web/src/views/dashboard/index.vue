<template>
  <div class="dashboard-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalUsers }}</div>
              <div class="stat-label">注册用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sessions">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalSessions }}</div>
              <div class="stat-label">对话会话</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card alert">
          <div class="stat-content">
            <div class="stat-icon alerts">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingAlerts }}</div>
              <div class="stat-label">待处理预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon today">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayActive }}</div>
              <div class="stat-label">今日活跃</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>预警趋势</span>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>预警等级分布</span>
          </template>
          <div class="chart-container" ref="levelChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>最新预警</span>
              <el-button type="primary" link @click="goToAlerts">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentAlerts" style="width: 100%">
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
            <el-table-column prop="createdAt" label="时间" width="180" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewAlert(row.id)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

const trendChartRef = ref<HTMLElement>()
const levelChartRef = ref<HTMLElement>()

const stats = ref({
  totalUsers: 1234,
  totalSessions: 5678,
  pendingAlerts: 12,
  todayActive: 89,
})

const recentAlerts = ref([
  { id: 1, userId: 101, alertLevel: 'red', alertType: 'crisis_intervention', triggerSource: 'chat', createdAt: '2024-01-15 10:30:00', status: 'pending' },
  { id: 2, userId: 205, alertLevel: 'orange', alertType: 'high_risk_warning', triggerSource: 'assessment', createdAt: '2024-01-15 09:45:00', status: 'processing' },
  { id: 3, userId: 308, alertLevel: 'yellow', alertType: 'attention_needed', triggerSource: 'emotion', createdAt: '2024-01-15 08:20:00', status: 'resolved' },
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

function goToAlerts() {
  router.push('/alerts')
}

function viewAlert(id: number) {
  router.push(`/alerts/${id}`)
}

onMounted(() => {
  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['红色', '橙色', '黄色'] },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [
        { name: '红色', type: 'line', data: [2, 1, 3, 2, 1, 0, 1], itemStyle: { color: '#f56c6c' } },
        { name: '橙色', type: 'line', data: [5, 4, 6, 3, 4, 2, 3], itemStyle: { color: '#e6a23c' } },
        { name: '黄色', type: 'line', data: [12, 15, 10, 8, 14, 9, 11], itemStyle: { color: '#909399' } },
      ],
    })
  }
  
  if (levelChartRef.value) {
    const chart = echarts.init(levelChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 5, name: '红色', itemStyle: { color: '#f56c6c' } },
          { value: 15, name: '橙色', itemStyle: { color: '#e6a23c' } },
          { value: 45, name: '黄色', itemStyle: { color: '#909399' } },
        ],
      }],
    })
  }
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
    }
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      
      .el-icon {
        font-size: 28px;
        color: #fff;
      }
      
      &.users { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
      &.sessions { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
      &.alerts { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
      &.today { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    }
    
    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #333;
      }
      
      .stat-label {
        font-size: 14px;
        color: #999;
        margin-top: 4px;
      }
    }
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>
