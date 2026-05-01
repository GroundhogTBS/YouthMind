<template>
  <view class="admin-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack" title="返回">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">管理后台</text>
        <text class="header-subtitle">数据概览与监控</text>
      </view>
      <view class="header-right">
        <view class="refresh-btn" @click="loadAll" title="刷新数据">
          <text>↻</text>
        </view>
      </view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false">
      <view class="tabs">
        <view 
          v-for="tab in tabs" 
          :key="tab.key" 
          class="tab-item" 
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <text>{{ tab.label }}</text>
        </view>
      </view>

      <view v-if="activeTab === 'dashboard'" class="tab-content">
        <view class="stats-grid">
          <view class="stat-card" v-for="stat in statCards" :key="stat.label">
            <text class="stat-value">{{ stat.value }}</text>
            <text class="stat-label">{{ stat.label }}</text>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <text class="section-title">用户增长趋势</text>
          </view>
          <view class="chart-container">
            <view v-for="item in dashboard.user_growth" :key="item.date" class="chart-bar-item">
              <text class="chart-date">{{ formatDate(item.date) }}</text>
              <view class="chart-bar-bg">
                <view class="chart-bar-fill" :style="{ width: getBarWidth(item.count, maxUserGrowth) }"></view>
              </view>
              <text class="chart-count">{{ item.count }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <text class="section-title">消息趋势</text>
          </view>
          <view class="chart-container">
            <view v-for="item in dashboard.message_trend" :key="item.date" class="chart-bar-item">
              <text class="chart-date">{{ formatDate(item.date) }}</text>
              <view class="chart-bar-bg">
                <view class="chart-bar-fill message" :style="{ width: getBarWidth(item.count, maxMessageTrend) }"></view>
              </view>
              <text class="chart-count">{{ item.count }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <text class="section-title">情绪分布</text>
          </view>
          <view class="emotion-chart">
            <view v-for="(count, emotion) in dashboard.emotion_distribution" :key="emotion" class="emotion-bar-item">
              <text class="emotion-name">{{ getEmotionLabel(emotion as string) }}</text>
              <view class="emotion-bar-bg">
                <view class="emotion-bar-fill" :style="{ width: getBarWidth(count as number, maxEmotion) }"></view>
              </view>
              <text class="emotion-count">{{ count }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <text class="section-title">活跃用户TOP5</text>
          </view>
          <view class="top-users">
            <view v-for="(user, index) in dashboard.top_users" :key="user.id" class="top-user-item">
              <view class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</view>
              <text class="user-name">{{ user.nickname }}</text>
              <text class="session-count">{{ user.session_count }}次对话</text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="activeTab === 'crisis'" class="tab-content">
        <view class="filter-bar">
          <view class="filter-item" :class="{ active: crisisFilter === 'all' }" @click="crisisFilter = 'all'">
            <text>全部</text>
          </view>
          <view class="filter-item" :class="{ active: crisisFilter === 'unhandled' }" @click="crisisFilter = 'unhandled'">
            <text>未处理</text>
          </view>
          <view class="filter-item" :class="{ active: crisisFilter === 'handled' }" @click="crisisFilter = 'handled'">
            <text>已处理</text>
          </view>
        </view>

        <view v-if="crisisEvents.length === 0" class="empty-state">
          <text>暂无危机事件</text>
        </view>
        <view v-for="event in crisisEvents" :key="event.id" class="crisis-item">
          <view class="crisis-level" :class="event.risk_level">
            <text>{{ getRiskLabel(event.risk_level) }}</text>
          </view>
          <view class="crisis-info">
            <text class="crisis-user">用户: {{ event.user_id ? event.user_id.substring(0, 8) + '...' : '未知' }}</text>
            <text class="crisis-keywords" v-if="event.matched_keywords">关键词: {{ event.matched_keywords }}</text>
            <text class="crisis-time">{{ formatTime(event.created_at) }}</text>
          </view>
          <view class="crisis-action">
            <text v-if="event.handled" class="handled-tag">已处理</text>
            <view v-else class="handle-btn" @click="showHandleModal(event)" title="标记已处理">
              <text>处理</text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="activeTab === 'users'" class="tab-content">
        <view class="search-bar">
          <input 
            v-model="userSearch" 
            placeholder="搜索用户手机号或昵称" 
            class="search-input"
            @confirm="searchUsers"
          />
          <view class="search-btn" @click="searchUsers">
            <text>搜索</text>
          </view>
        </view>

        <view v-for="user in users" :key="user.id" class="user-item">
          <view class="user-avatar">
            <text>{{ (user.nickname || 'U').charAt(0).toUpperCase() }}</text>
          </view>
          <view class="user-detail">
            <view class="user-header">
              <text class="user-name">{{ user.nickname || '未设置昵称' }}</text>
              <view class="risk-badge" :class="'risk-' + user.risk_level">
                <text>{{ getRiskLevelText(user.risk_level) }}</text>
              </view>
            </view>
            <text class="user-meta">{{ user.phone }} · {{ user.age_group || '未设置年龄' }}</text>
            <text class="user-stats">对话{{ user.session_count }}次 · 测评{{ user.assessment_count }}次 · 情绪记录{{ user.emotion_record_count }}次</text>
          </view>
          <text class="user-time">{{ formatTime(user.last_active) }}</text>
        </view>
      </view>

      <view v-if="activeTab === 'logs'" class="tab-content">
        <view class="filter-bar">
          <view class="filter-item" :class="{ active: logAction === '' }" @click="logAction = ''">
            <text>全部</text>
          </view>
          <view class="filter-item" :class="{ active: logAction === 'login' }" @click="logAction = 'login'">
            <text>登录</text>
          </view>
          <view class="filter-item" :class="{ active: logAction === 'send_message' }" @click="logAction = 'send_message'">
            <text>消息</text>
          </view>
          <view class="filter-item" :class="{ active: logAction === 'handle_crisis' }" @click="logAction = 'handle_crisis'">
            <text>危机处理</text>
          </view>
        </view>

        <view v-for="log in operationLogs" :key="log.id" class="log-item">
          <view class="log-action" :class="'action-' + log.action">
            <text>{{ getActionLabel(log.action) }}</text>
          </view>
          <view class="log-info">
            <text class="log-user">用户: {{ log.user_id ? log.user_id.substring(0, 8) + '...' : '系统' }}</text>
            <text class="log-resource" v-if="log.resource_type">{{ log.resource_type }}: {{ log.resource_id }}</text>
            <text class="log-time">{{ formatTime(log.created_at) }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="modal-overlay" v-if="showModal" @click="showModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">处理危机事件</text>
          <view class="modal-close" @click="showModal = false">
            <text>×</text>
          </view>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">处理备注</text>
            <textarea class="form-textarea" v-model="handleNotes" placeholder="请输入处理情况说明..." />
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showModal = false">
            <text>取消</text>
          </view>
          <view class="confirm-btn" @click="confirmHandle">
            <text>确认处理</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '@/api/request'

const tabs = [
  { key: 'dashboard', label: '仪表盘' },
  { key: 'crisis', label: '预警管理' },
  { key: 'users', label: '用户管理' },
  { key: 'logs', label: '操作日志' }
]

const activeTab = ref('dashboard')
const crisisFilter = ref('all')
const logAction = ref('')
const userSearch = ref('')
const showModal = ref(false)
const handleNotes = ref('')
const selectedEvent = ref<any>(null)

const dashboard = ref<any>({
  stats: {},
  user_growth: [],
  message_trend: [],
  emotion_distribution: {},
  crisis_trend: [],
  assessment_distribution: {},
  top_users: []
})

const crisisEvents = ref<any[]>([])
const users = ref<any[]>([])
const operationLogs = ref<any[]>([])

const stats = computed(() => dashboard.value.stats || {})

const statCards = computed(() => [
  { label: '总用户', value: stats.value.total_users || 0 },
  { label: '今日新增', value: stats.value.new_users_today || 0 },
  { label: '今日活跃', value: stats.value.active_users_today || 0 },
  { label: '本周活跃', value: stats.value.active_users_week || 0 },
  { label: '今日消息', value: stats.value.messages_today || 0 },
  { label: '本周消息', value: stats.value.messages_week || 0 },
  { label: '危机事件', value: stats.value.crisis_events_count || 0 },
  { label: '未处理', value: stats.value.unhandled_crisis || 0 }
])

const maxUserGrowth = computed(() => Math.max(...(dashboard.value.user_growth?.map((u: any) => u.count) || [1]), 1))
const maxMessageTrend = computed(() => Math.max(...(dashboard.value.message_trend?.map((m: any) => m.count) || [1]), 1))
const maxEmotion = computed(() => Math.max(...Object.values(dashboard.value.emotion_distribution || {}) as number[], 1))

onMounted(() => {
  loadAll()
})

watch([crisisFilter], () => {
  loadCrisisEvents()
})

watch([logAction], () => {
  loadOperationLogs()
})

async function loadAll() {
  await Promise.all([
    loadDashboard(),
    loadCrisisEvents(),
    loadUsers(),
    loadOperationLogs()
  ])
}

async function loadDashboard() {
  try {
    dashboard.value = await api.admin.getDashboard()
  } catch (e) {
    console.error('加载仪表盘失败', e)
  }
}

async function loadCrisisEvents() {
  try {
    const status = crisisFilter.value === 'all' ? '' : crisisFilter.value
    crisisEvents.value = await api.admin.getCrisisEvents(status, '', 1, 50)
  } catch (e) {
    console.error('加载危机事件失败', e)
  }
}

async function loadUsers() {
  try {
    users.value = await api.admin.getUsers(1, 50, userSearch.value)
  } catch (e) {
    console.error('加载用户失败', e)
  }
}

async function searchUsers() {
  await loadUsers()
}

async function loadOperationLogs() {
  try {
    operationLogs.value = await api.admin.getOperationLogs('', logAction.value, 1, 100)
  } catch (e) {
    console.error('加载操作日志失败', e)
  }
}

function showHandleModal(event: any) {
  selectedEvent.value = event
  handleNotes.value = ''
  showModal.value = true
}

async function confirmHandle() {
  if (!selectedEvent.value) return
  
  try {
    await api.admin.handleCrisis(selectedEvent.value.id, handleNotes.value)
    uni.showToast({ title: '已标记处理', icon: 'success' })
    showModal.value = false
    loadCrisisEvents()
    loadDashboard()
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function getBarWidth(count: number, max: number): string {
  return `${Math.max((count / max) * 100, 5)}%`
}

function formatDate(date: string): string {
  if (!date) return ''
  const parts = date.split('-')
  return `${parts[1]}/${parts[2]}`
}

function formatTime(dateStr: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function getEmotionLabel(emotion: string): string {
  const map: Record<string, string> = {
    happy: '开心', sad: '难过', anxious: '焦虑', angry: '生气',
    fear: '恐惧', lonely: '孤独', confused: '迷茫', inferior: '自卑', neutral: '平静'
  }
  return map[emotion] || emotion
}

function getRiskLabel(level: string): string {
  const map: Record<string, string> = {
    red: '高危', orange: '中危', yellow: '低危', green: '正常'
  }
  return map[level] || level
}

function getRiskLevelText(level: string): string {
  const map: Record<string, string> = {
    high: '高风险', medium: '中风险', low: '低风险'
  }
  return map[level] || level
}

function getActionLabel(action: string): string {
  const map: Record<string, string> = {
    login: '登录', logout: '登出', send_message: '发消息',
    create_session: '创建会话', delete_session: '删除会话',
    submit_assessment: '提交测评', create_emotion: '记录情绪',
    handle_crisis: '处理危机', upload_file: '上传文件',
    update_profile: '更新资料', admin_login: '管理员登录',
    admin_view: '管理查看', admin_export: '数据导出'
  }
  return map[action] || action
}

function handleGoBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.admin-page {
  @extend .page-wrapper;
  flex-direction: column;
}

.page-header {
  @extend .page-header;
  background: $bg-primary;
}

.header-left, .header-right {
  width: 40px;
}

.back-btn, .refresh-btn {
  @extend .back-button;
}

.header-center {
  @include flex-column;
  align-items: center;
}

.header-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $text-primary;
}

.header-subtitle {
  font-size: $font-size-sm;
  color: $text-muted;
  margin-top: 2px;
}

.page-content {
  flex: 1;
  height: 0;
}

.tabs {
  display: flex;
  background: $bg-primary;
  border-bottom: 1px solid $border-light;
}

.tab-item {
  flex: 1;
  padding: $spacing-md;
  text-align: center;
  font-size: $font-size-sm;
  color: $text-muted;
  
  &.active {
    color: $primary-color;
    border-bottom: 2px solid $primary-color;
  }
}

.tab-content {
  padding: $spacing-md;
}

.stats-grid {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  margin-bottom: $spacing-lg;
}

.stat-card {
  width: calc(25% - 8px);
  padding: $spacing-md;
  background: $bg-primary;
  border-radius: $radius-lg;
  @include flex-column;
  align-items: center;
  border: 1px solid $border-light;
}

.stat-value {
  font-size: $font-size-xl;
  font-weight: 700;
  color: $primary-color;
}

.stat-label {
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: $spacing-xs;
}

.section {
  margin-bottom: $spacing-lg;
  background: $bg-primary;
  border-radius: $radius-xl;
  padding: $spacing-lg;
}

.section-header {
  margin-bottom: $spacing-md;
}

.section-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-primary;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.chart-bar-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.chart-date {
  width: 40px;
  font-size: $font-size-xs;
  color: $text-muted;
}

.chart-bar-bg {
  flex: 1;
  height: 16px;
  background: $bg-secondary;
  border-radius: 8px;
  overflow: hidden;
}

.chart-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary-color, rgba($primary-color, 0.6));
  border-radius: 8px;
  
  &.message {
    background: linear-gradient(90deg, $success-color, rgba($success-color, 0.6));
  }
}

.chart-count {
  width: 30px;
  font-size: $font-size-xs;
  color: $text-primary;
  text-align: right;
}

.emotion-chart {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.emotion-bar-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.emotion-name {
  width: 50px;
  font-size: $font-size-sm;
  color: $text-secondary;
  text-align: right;
}

.emotion-bar-bg {
  flex: 1;
  height: 20px;
  background: $bg-secondary;
  border-radius: 10px;
  overflow: hidden;
}

.emotion-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary-color, rgba($primary-color, 0.6));
  border-radius: 10px;
}

.emotion-count {
  width: 30px;
  font-size: $font-size-sm;
  color: $text-primary;
  font-weight: 600;
}

.top-users {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.top-user-item {
  display: flex;
  align-items: center;
  padding: $spacing-sm;
  background: $bg-secondary;
  border-radius: $radius-md;
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  @include flex-center;
  font-size: $font-size-xs;
  font-weight: 600;
  margin-right: $spacing-sm;
  background: $bg-primary;
  color: $text-muted;
  
  &.rank-1 { background: #FFD700; color: #fff; }
  &.rank-2 { background: #C0C0C0; color: #fff; }
  &.rank-3 { background: #CD7F32; color: #fff; }
}

.user-name {
  flex: 1;
  font-size: $font-size-sm;
  color: $text-primary;
}

.session-count {
  font-size: $font-size-xs;
  color: $text-muted;
}

.filter-bar {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
}

.filter-item {
  padding: $spacing-xs $spacing-md;
  background: $bg-primary;
  border-radius: $radius-full;
  font-size: $font-size-xs;
  color: $text-muted;
  
  &.active {
    background: $primary-color;
    color: #fff;
  }
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: $text-muted;
}

.crisis-item {
  display: flex;
  align-items: center;
  padding: $spacing-md;
  background: $bg-primary;
  border-radius: $radius-lg;
  margin-bottom: $spacing-sm;
}

.crisis-level {
  padding: 4px 10px;
  border-radius: $radius-sm;
  margin-right: $spacing-md;
  
  &.red {
    background: rgba($error-color, 0.15);
    text { color: $error-color; }
  }
  
  &.orange {
    background: rgba($warning-color, 0.15);
    text { color: $warning-color; }
  }
  
  &.yellow {
    background: rgba($primary-color, 0.15);
    text { color: $primary-color; }
  }
  
  text {
    font-size: $font-size-xs;
    font-weight: 600;
  }
}

.crisis-info {
  flex: 1;
}

.crisis-user {
  font-size: $font-size-sm;
  color: $text-primary;
  display: block;
}

.crisis-keywords {
  font-size: $font-size-xs;
  color: $text-muted;
  display: block;
  margin-top: 2px;
}

.crisis-time {
  font-size: $font-size-xs;
  color: $text-light;
}

.crisis-action {
  margin-left: $spacing-md;
}

.handled-tag {
  font-size: $font-size-xs;
  color: $success-color;
  background: rgba($success-color, 0.1);
  padding: 4px $spacing-md;
  border-radius: $radius-sm;
}

.handle-btn {
  padding: 6px $spacing-lg;
  background: $primary-color;
  border-radius: $radius-sm;
  @include btn-hover;
  
  text {
    font-size: $font-size-xs;
    color: #fff;
  }
}

.search-bar {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
}

.search-input {
  flex: 1;
  height: 36px;
  padding: 0 $spacing-md;
  background: $bg-primary;
  border-radius: $radius-full;
  font-size: $font-size-sm;
}

.search-btn {
  padding: 0 $spacing-lg;
  background: $primary-color;
  border-radius: $radius-full;
  @include flex-center;
  
  text {
    font-size: $font-size-sm;
    color: #fff;
  }
}

.user-item {
  display: flex;
  align-items: center;
  padding: $spacing-md;
  background: $bg-primary;
  border-radius: $radius-lg;
  margin-bottom: $spacing-sm;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: rgba($primary-color, 0.1);
  border-radius: 50%;
  @include flex-center;
  margin-right: $spacing-md;
  
  text {
    font-size: 16px;
    font-weight: 600;
    color: $primary-color;
  }
}

.user-detail {
  flex: 1;
}

.user-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.user-name {
  font-size: $font-size-sm;
  font-weight: 500;
  color: $text-primary;
}

.risk-badge {
  padding: 2px 6px;
  border-radius: $radius-sm;
  font-size: $font-size-xs;
  
  &.risk-high {
    background: rgba($error-color, 0.1);
    text { color: $error-color; }
  }
  
  &.risk-medium {
    background: rgba($warning-color, 0.1);
    text { color: $warning-color; }
  }
  
  &.risk-low {
    background: rgba($success-color, 0.1);
    text { color: $success-color; }
  }
}

.user-meta {
  font-size: $font-size-xs;
  color: $text-muted;
  display: block;
  margin-top: 2px;
}

.user-stats {
  font-size: $font-size-xs;
  color: $text-light;
  display: block;
  margin-top: 2px;
}

.user-time {
  font-size: $font-size-xs;
  color: $text-light;
}

.log-item {
  display: flex;
  align-items: center;
  padding: $spacing-sm $spacing-md;
  background: $bg-primary;
  border-radius: $radius-md;
  margin-bottom: $spacing-xs;
}

.log-action {
  padding: 2px 8px;
  border-radius: $radius-sm;
  margin-right: $spacing-sm;
  font-size: $font-size-xs;
  background: $bg-secondary;
  color: $text-muted;
  
  &.action-login, &.action-admin_login {
    background: rgba($success-color, 0.1);
    text { color: $success-color; }
  }
  
  &.action-handle_crisis {
    background: rgba($warning-color, 0.1);
    text { color: $warning-color; }
  }
  
  &.action-send_message {
    background: rgba($primary-color, 0.1);
    text { color: $primary-color; }
  }
}

.log-info {
  flex: 1;
}

.log-user {
  font-size: $font-size-xs;
  color: $text-primary;
}

.log-resource {
  font-size: $font-size-xs;
  color: $text-muted;
  margin-left: $spacing-sm;
}

.log-time {
  font-size: $font-size-xs;
  color: $text-light;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  @include flex-center;
}

.modal-content {
  width: 85%;
  max-width: 400px;
  background: $bg-primary;
  border-radius: $radius-xl;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-light;
}

.modal-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $text-primary;
}

.modal-close {
  width: 32px;
  height: 32px;
  @include flex-center;
  
  text {
    font-size: 24px;
    color: $text-muted;
  }
}

.modal-body {
  padding: $spacing-lg;
}

.form-item {
  margin-bottom: $spacing-md;
}

.form-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-bottom: $spacing-xs;
  display: block;
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  font-size: $font-size-base;
  color: $text-primary;
}

.modal-footer {
  display: flex;
  padding: $spacing-lg;
  gap: $spacing-md;
  border-top: 1px solid $border-light;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  height: 44px;
  border-radius: $radius-md;
  @include flex-center;
}

.cancel-btn {
  background: $bg-secondary;
  
  text {
    color: $text-secondary;
  }
}

.confirm-btn {
  background: $primary-color;
  
  text {
    color: #fff;
  }
}
</style>
