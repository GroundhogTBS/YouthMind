<template>
  <div class="dashboard-page" v-loading="loading">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_users }}</div>
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
              <div class="stat-value">{{ stats.total_sessions }}</div>
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
              <div class="stat-value">{{ stats.unhandled_crisis }}</div>
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
              <div class="stat-value">{{ stats.active_users_today }}</div>
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
            <span>消息趋势</span>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>情绪分布</span>
          </template>
          <div class="chart-container" ref="emotionChartRef"></div>
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
            <el-table-column prop="user_id" label="用户ID" width="100" />
            <el-table-column prop="risk_level" label="等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getLevelType(row.risk_level)">
                  {{ getLevelText(row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk_score" label="风险分" width="80" />
            <el-table-column prop="matched_keywords" label="关键词" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="180">
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
import { api } from '@/api/request'

const router = useRouter()

const trendChartRef = ref<HTMLElement>()
const emotionChartRef = ref<HTMLElement>()
const loading = ref(false)

const stats = ref({
  total_users: 0,
  total_sessions: 0,
  unhandled_crisis: 0,
  active_users_today: 0,
  total_messages: 0,
  crisis_events_count: 0,
})

const recentAlerts = ref<any[]>([])
const messageTrend = ref<any[]>([])
const emotionDistribution = ref<Record<string, number>>({})

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

function goToAlerts() {
  router.push('/alerts')
}

function viewAlert(id: number) {
  router.push(`/alerts/${id}`)
}

async function loadDashboard() {
  loading.value = true
  try {
    const data = await api.admin.getDashboard()
    stats.value = data.stats
    messageTrend.value = data.message_trend || []
    emotionDistribution.value = data.emotion_distribution || {}
    recentAlerts.value = (data.crisis_trend || []).slice(0, 5)
  } catch (e) {
    console.error('加载仪表盘失败', e)
  } finally {
    loading.value = false
  }
}

async function loadAlerts() {
  try {
    const data = await api.admin.getCrisisEvents('unhandled', '', 1, 5)
    recentAlerts.value = data
  } catch (e) {
    console.error('加载预警失败', e)
  }
}

function initCharts() {
  if (trendChartRef.value && messageTrend.value.length > 0) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { 
        type: 'category', 
        data: messageTrend.value.map(d => d.date.substring(5)) 
      },
      yAxis: { type: 'value' },
      series: [
        { 
          name: '消息数', 
          type: 'line', 
          data: messageTrend.value.map(d => d.count),
          smooth: true,
          itemStyle: { color: '#6C5CE7' },
          areaStyle: { color: 'rgba(108, 92, 231, 0.1)' }
        },
      ],
    })
  }
  
  if (emotionChartRef.value && Object.keys(emotionDistribution.value).length > 0) {
    const chart = echarts.init(emotionChartRef.value)
    const emotionLabels: Record<string, string> = {
      happy: '开心', sad: '难过', anxious: '焦虑', angry: '生气',
      fear: '恐惧', lonely: '孤独', confused: '迷茫', inferior: '自卑', neutral: '平静'
    }
    const colors: Record<string, string> = {
      happy: '#22c55e', sad: '#6366f1', anxious: '#f59e0b', angry: '#ef4444',
      fear: '#8b5cf6', lonely: '#64748b', confused: '#ec4899', inferior: '#0ea5e9', neutral: '#3b82f6'
    }
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: Object.entries(emotionDistribution.value).map(([key, value]) => ({
          value,
          name: emotionLabels[key] || key,
          itemStyle: { color: colors[key] || '#909399' }
        })),
      }],
    })
  }
}

onMounted(async () => {
  await loadDashboard()
  await loadAlerts()
  initCharts()
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
