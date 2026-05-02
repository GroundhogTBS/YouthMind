<template>
  <view class="home-page">
    <view class="home-sidebar">
      <view class="sidebar-logo">
        <view class="logo-mark">Y</view>
        <text class="logo-text">YouthMind</text>
      </view>
      <view class="sidebar-nav">
        <view class="nav-item" :class="{ active: navStore.currentPage === 'home' }" @click="stayHome" title="首页">
          <view class="nav-icon">
            <text class="icon-text">H</text>
          </view>
          <text class="nav-text">首页</text>
        </view>
        <view class="nav-item" :class="{ active: navStore.currentPage === 'chat' }" @click="goToChat" title="AI对话">
          <view class="nav-icon">
            <text class="icon-text">C</text>
          </view>
          <text class="nav-text">AI对话</text>
        </view>
        <view class="nav-item" :class="{ active: navStore.currentPage === 'assessment' }" @click="goToAssessment" title="心理测评">
          <view class="nav-icon">
            <text class="icon-text">A</text>
          </view>
          <text class="nav-text">心理测评</text>
        </view>
        <view class="nav-item" :class="{ active: navStore.currentPage === 'resource' }" @click="goToResource" title="学习资源">
          <view class="nav-icon">
            <text class="icon-text">R</text>
          </view>
          <text class="nav-text">学习资源</text>
        </view>
      </view>
      <view class="sidebar-footer">
        <view class="user-info" @click="goToProfile" title="个人中心">
          <view class="user-avatar">
            <text class="avatar-text">{{ nickname.charAt(0) }}</text>
          </view>
          <text class="user-name">{{ nickname }}</text>
        </view>
      </view>
    </view>
    
    <scroll-view class="home-main" scroll-y :show-scrollbar="false">
      <view class="main-header">
        <view class="greeting">
          <text class="greeting-text">{{ greetingText }}，{{ nickname }}</text>
          <text class="greeting-sub">今天想聊点什么？</text>
        </view>
        <view class="action-btn" @click="goToChat" title="开始AI对话">
          <text class="btn-text">开始对话</text>
        </view>
      </view>
      
      <view class="main-content">
        <view class="feature-grid">
          <view class="feature-card" @click="goToChat" title="与AI心理助手对话">
            <view class="card-icon-wrapper purple">
              <text class="card-icon-letter">C</text>
            </view>
            <text class="card-title">AI心理助手</text>
            <text class="card-desc">随时倾诉心声，AI陪伴倾听你的烦恼</text>
            <text class="card-action">开始对话</text>
          </view>
          
          <view class="feature-card" @click="goToAssessment" title="进行心理测评">
            <view class="card-icon-wrapper pink">
              <text class="card-icon-letter">A</text>
            </view>
            <text class="card-title">心理测评</text>
            <text class="card-desc">专业量表测评，了解自己的心理状态</text>
            <text class="card-action">开始测评</text>
          </view>
          
          <view class="feature-card" @click="goToResource" title="浏览学习资源">
            <view class="card-icon-wrapper blue">
              <text class="card-icon-letter">R</text>
            </view>
            <text class="card-title">学习资源</text>
            <text class="card-desc">心理健康知识库，助力成长每一步</text>
            <text class="card-action">浏览资源</text>
          </view>
          
          <view class="feature-card" @click="goToEmotion" title="记录今日心情">
            <view class="card-icon-wrapper yellow">
              <text class="card-icon-letter">M</text>
            </view>
            <text class="card-title">今日心情</text>
            <text class="card-desc">记录你的情绪变化</text>
            <view class="mood-picker">
              <view class="mood-item" @click="selectMood('good')">良好</view>
              <view class="mood-item" @click="selectMood('normal')">一般</view>
              <view class="mood-item" @click="selectMood('bad')">不好</view>
            </view>
          </view>
        </view>
        
        <view class="section">
          <view class="section-header">
            <text class="section-title">我的日记</text>
            <text class="section-more" @click="goToDiary">查看全部</text>
          </view>
          <view class="diary-list" v-if="recentDiaries.length > 0">
            <view class="diary-card" v-for="diary in recentDiaries" :key="diary.id" @click="viewDiary(diary)">
              <view class="diary-header">
                <text class="diary-date">{{ formatDate(diary.createdAt) }}</text>
                <view v-if="diary.mood" class="diary-mood" :style="{ background: getMoodColor(diary.mood) }">
                  <text>{{ getMoodIcon(diary.mood) }}</text>
                </view>
              </view>
              <text class="diary-title" v-if="diary.title">{{ diary.title }}</text>
              <text class="diary-preview">{{ truncate(diary.content, 60) }}</text>
              <view class="diary-stats">
                <text class="word-count">{{ diary.content.length }}字</text>
              </view>
            </view>
          </view>
          <view class="empty-diary" v-else @click="goToDiary">
            <text class="empty-text">还没有日记</text>
            <text class="empty-action">点击开始记录 →</text>
          </view>
        </view>
        
        <view class="section">
          <view class="section-header">
            <text class="section-title">情绪趋势</text>
            <text class="section-more" @click="goToEmotion">详细分析</text>
          </view>
          <view class="emotion-chart-card">
            <view class="chart-container">
              <view class="chart-y-axis">
                <text v-for="i in [10, 7, 5, 2, 0]" :key="i" class="y-label">{{ i }}</text>
              </view>
              <view class="chart-area">
                <view class="chart-grid">
                  <view v-for="i in 5" :key="i" class="grid-line"></view>
                </view>
                <view class="chart-curve">
                  <view 
                    v-for="(point, index) in emotionPoints" 
                    :key="index" 
                    class="curve-point"
                    :style="{ 
                      left: (index * 100 / (emotionPoints.length - 1)) + '%',
                      bottom: (point.intensity * 10) + '%'
                    }"
                  >
                    <view class="point-dot" :style="{ background: point.color }"></view>
                    <text class="point-label">{{ point.label }}</text>
                  </view>
                </view>
                <svg class="curve-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <polyline 
                    :points="curvePoints" 
                    fill="none" 
                    stroke="#6366f1" 
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </view>
              <view class="chart-x-axis">
                <text v-for="day in emotionDays" :key="day" class="x-label">{{ day }}</text>
              </view>
            </view>
          </view>
        </view>
        
        <view class="section">
          <view class="section-header">
            <text class="section-title">推荐阅读</text>
            <text class="section-more" @click="goToResource">查看更多</text>
          </view>
          <view class="article-grid">
            <view class="article-card" v-for="(article, index) in articles" :key="index">
              <view class="article-tag">{{ article.category }}</view>
              <text class="article-title">{{ article.title }}</text>
              <text class="article-summary">{{ article.summary }}</text>
            </view>
          </view>
        </view>
        
        <view class="tips-card">
          <view class="tips-icon-wrapper">
            <text class="tips-icon-letter">T</text>
          </view>
          <view class="tips-content">
            <text class="tips-title">每日小贴士</text>
            <text class="tips-text">每天花几分钟关注自己的心理健康，让生活更美好。</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useNavStore } from '@/stores/nav'
import { useUserStore } from '@/stores/user'
import { api } from '@/api/request'

const navStore = useNavStore()
const userStore = useUserStore()

const recentDiaries = ref<any[]>([])
const emotionPoints = ref<any[]>([])

onMounted(async () => {
  navStore.resetToHome()
  userStore.checkLogin()
  
  if (!userStore.isLoggedIn) {
    uni.redirectTo({ url: '/pages/auth/login' })
    return
  }
  
  await Promise.all([
    loadRecentDiaries(),
    loadEmotionTrend()
  ])
})

const nickname = computed(() => userStore.userInfo?.nickname || '朋友')

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const emotionDays = computed(() => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }
  return days
})

const curvePoints = computed(() => {
  if (emotionPoints.value.length === 0) return '0,100 100,100'
  return emotionPoints.value.map((p, i) => {
    const x = i * 100 / (emotionPoints.value.length - 1)
    const y = 100 - p.intensity * 10
    return `${x},${y}`
  }).join(' ')
})

const articles = ref([
  { category: '情绪', title: '如何应对考试焦虑', summary: '考试前的紧张是正常的，学会这些方法让你轻松应对' },
  { category: '人际', title: '和朋友吵架了怎么办', summary: '友谊中的冲突可以这样化解，让关系更紧密' },
  { category: '成长', title: '提升自信心的方法', summary: '相信自己，你比想象中更优秀' }
])

async function loadRecentDiaries() {
  try {
    const data = await api.diary.getList(3)
    recentDiaries.value = data || []
  } catch (e) {
    console.error('加载日记失败', e)
  }
}

async function loadEmotionTrend() {
  try {
    const data = await api.emotionRecord.getTrend(7)
    const points: any[] = []
    const trend = data.daily_trend || []
    
    for (let i = 0; i < 7; i++) {
      const d = new Date()
      d.setDate(d.getDate() - (6 - i))
      const dateStr = d.toISOString().split('T')[0]
      const dayData = trend.find((t: any) => t.date === dateStr)
      
      if (dayData && dayData.emotions && dayData.emotions.length > 0) {
        const topEmotion = dayData.emotions.reduce((a: any, b: any) => a.intensity > b.intensity ? a : b)
        points.push({
          intensity: topEmotion.intensity,
          label: getEmotionLabel(topEmotion.type),
          color: getEmotionColor(topEmotion.type)
        })
      } else {
        points.push({ intensity: 5, label: '平静', color: '#3b82f6' })
      }
    }
    
    emotionPoints.value = points
  } catch (e) {
    console.error('加载情绪趋势失败', e)
    emotionPoints.value = Array(7).fill({ intensity: 5, label: '平静', color: '#3b82f6' })
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

function truncate(text: string, length: number): string {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

function getMoodIcon(type: string): string {
  const icons: Record<string, string> = {
    happy: '😊', calm: '😌', sad: '😢', anxious: '😰',
    angry: '😠', tired: '😴', confused: '🤔', lonely: '😔'
  }
  return icons[type] || '😐'
}

function getMoodColor(type: string): string {
  const colors: Record<string, string> = {
    happy: '#22c55e', calm: '#3b82f6', sad: '#6366f1', anxious: '#f59e0b',
    angry: '#ef4444', tired: '#8b5cf6', confused: '#ec4899', lonely: '#64748b'
  }
  return colors[type] || '#6366f1'
}

function getEmotionLabel(type: string): string {
  const labels: Record<string, string> = {
    happy: '开心', calm: '平静', sad: '难过', anxious: '焦虑',
    angry: '生气', tired: '疲惫', confused: '困惑', lonely: '孤独'
  }
  return labels[type] || '平静'
}

function getEmotionColor(type: string): string {
  return getMoodColor(type)
}

function stayHome() {
  navStore.setPage('home')
}

function goToChat() {
  navStore.setPage('chat')
  uni.navigateTo({ url: '/pages/chat/index' })
}

function goToAssessment() {
  navStore.setPage('assessment')
  uni.navigateTo({ url: '/pages/assessment/index' })
}

function goToResource() {
  navStore.setPage('resource')
  uni.navigateTo({ url: '/pages/resource/index' })
}

function goToProfile() {
  uni.navigateTo({ url: '/pages/profile/index' })
}

function goToEmotion() {
  uni.navigateTo({ url: '/pages/emotion/index' })
}

function goToDiary() {
  uni.navigateTo({ url: '/pages/diary/index' })
}

function viewDiary(diary: any) {
  uni.navigateTo({ url: `/pages/diary/index?id=${diary.id}` })
}

function selectMood(mood: string) {
  uni.navigateTo({ url: `/pages/emotion/index?mood=${mood}` })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.home-page {
  width: 100%;
  height: 100vh;
  background: $bg-secondary;
  display: flex;
  flex-direction: row;
}

.home-sidebar {
  width: 220px;
  height: 100vh;
  background: $bg-primary;
  border-right: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-logo {
  padding: 20px;
  border-bottom: 1px solid $border-light;
  display: flex;
  align-items: center;
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: $primary-color;
  border-radius: 8px;
  @include flex-center;
  margin-right: 12px;
  
  text {
    color: #fff;
    font-size: 18px;
    font-weight: 700;
  }
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
}

.sidebar-nav {
  flex: 1;
  padding: 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 4px;
  @include clickable;
  
  &.active {
    background: rgba($primary-color, 0.1);
    
    .nav-text {
      color: $primary-color;
      font-weight: 500;
    }
    
    .nav-icon {
      background: $primary-color;
      
      .icon-text {
        color: #fff;
      }
    }
  }
}

.nav-icon {
  width: 28px;
  height: 28px;
  background: $bg-secondary;
  border-radius: 6px;
  @include flex-center;
  margin-right: 12px;
}

.icon-text {
  font-size: 12px;
  font-weight: 600;
  color: $text-muted;
}

.nav-text {
  font-size: 14px;
  color: $text-secondary;
}

.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid $border-light;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  background: $bg-secondary;
  border-radius: 8px;
  @include clickable;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: $primary-color;
  border-radius: 50%;
  @include flex-center;
  margin-right: 10px;
}

.avatar-text {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.user-name {
  font-size: 14px;
  color: $text-primary;
}

.home-main {
  flex: 1;
  height: 100vh;
}

.main-header {
  background: $bg-primary;
  padding: 24px 32px;
  border-bottom: 1px solid $border-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.greeting-text {
  font-size: 22px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 4px;
}

.greeting-sub {
  font-size: 14px;
  color: $text-muted;
}

.action-btn {
  background: $primary-color;
  padding: 10px 20px;
  border-radius: 8px;
  @include btn-hover;
}

.btn-text {
  font-size: 14px;
  color: #fff;
  font-weight: 500;
}

.main-content {
  padding: 24px 32px;
}

.feature-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10px 24px;
}

.feature-card {
  width: calc(50% - 20px);
  margin: 0 10px 20px;
  background: $bg-primary;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid $border-light;
  @include card-hover;
}

.card-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  @include flex-center;
  margin-bottom: 12px;
  
  &.purple { background: rgba($primary-color, 0.1); }
  &.pink { background: rgba(#f093fb, 0.1); }
  &.blue { background: rgba(#00c6ff, 0.1); }
  &.yellow { background: rgba(#faad14, 0.1); }
}

.card-icon-letter {
  font-size: 16px;
  font-weight: 700;
  color: $primary-color;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: $text-muted;
  line-height: 1.5;
  display: block;
  margin-bottom: 12px;
}

.card-action {
  font-size: 13px;
  color: $primary-color;
  font-weight: 500;
}

.mood-picker {
  display: flex;
  gap: 8px;
}

.mood-item {
  padding: 6px 12px;
  background: $bg-secondary;
  border-radius: 16px;
  font-size: 12px;
  color: $text-secondary;
  @include clickable;
  
  &:hover {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }
}

.section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.section-more {
  font-size: 13px;
  color: $text-muted;
  @include clickable;
  
  &:hover {
    color: $primary-color;
  }
}

.article-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -8px;
}

.article-card {
  width: calc(33.33% - 16px);
  margin: 0 8px 16px;
  background: $bg-primary;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid $border-light;
  @include card-hover;
}

.article-tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba($primary-color, 0.1);
  border-radius: 4px;
  font-size: 11px;
  color: $primary-color;
  margin-bottom: 8px;
}

.article-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 6px;
}

.article-summary {
  font-size: 12px;
  color: $text-muted;
  line-height: 1.5;
}

.tips-card {
  background: $bg-primary;
  border-radius: 10px;
  padding: 16px 20px;
  border: 1px solid $border-light;
  display: flex;
  align-items: flex-start;
}

.tips-icon-wrapper {
  width: 32px;
  height: 32px;
  background: rgba(#faad14, 0.1);
  border-radius: 6px;
  @include flex-center;
  margin-right: 14px;
  flex-shrink: 0;
}

.tips-icon-letter {
  font-size: 14px;
  font-weight: 700;
  color: #faad14;
}

.tips-content {
  flex: 1;
}

.tips-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 4px;
}

.tips-text {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.5;
}

.diary-list {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -8px;
}

.diary-card {
  width: calc(33.33% - 16px);
  margin: 0 8px 16px;
  background: $bg-primary;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid $border-light;
  @include card-hover;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.diary-date {
  font-size: 12px;
  color: $text-muted;
}

.diary-mood {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  @include flex-center;
  
  text {
    font-size: 12px;
  }
}

.diary-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 6px;
}

.diary-preview {
  font-size: 12px;
  color: $text-secondary;
  line-height: 1.5;
  display: block;
  margin-bottom: 8px;
}

.diary-stats {
  display: flex;
  justify-content: flex-end;
}

.word-count {
  font-size: 11px;
  color: $primary-color;
  background: rgba($primary-color, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.empty-diary {
  background: $bg-primary;
  border-radius: 10px;
  padding: 32px;
  border: 1px dashed $border-light;
  text-align: center;
  @include clickable;
}

.empty-text {
  font-size: 14px;
  color: $text-muted;
  display: block;
  margin-bottom: 8px;
}

.empty-action {
  font-size: 13px;
  color: $primary-color;
}

.emotion-chart-card {
  background: $bg-primary;
  border-radius: 10px;
  padding: 20px;
  border: 1px solid $border-light;
}

.chart-container {
  display: flex;
  height: 120px;
}

.chart-y-axis {
  width: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 8px;
}

.y-label {
  font-size: 10px;
  color: $text-light;
  text-align: right;
}

.chart-area {
  flex: 1;
  position: relative;
}

.chart-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.grid-line {
  height: 1px;
  background: $border-light;
}

.chart-curve {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.curve-point {
  position: absolute;
  transform: translate(-50%, 50%);
  z-index: 2;
}

.point-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.point-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: $text-muted;
  white-space: nowrap;
}

.curve-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.chart-x-axis {
  display: flex;
  justify-content: space-between;
  padding-top: 8px;
  margin-left: 24px;
}

.x-label {
  font-size: 10px;
  color: $text-light;
}

@media screen and (max-width: 1200px) {
  .article-card, .diary-card {
    width: calc(50% - 16px);
  }
}

@media screen and (max-width: 900px) {
  .feature-card {
    width: calc(100% - 20px);
  }
  
  .article-card {
    width: calc(100% - 16px);
  }
}

@media screen and (max-width: 768px) {
  .home-page {
    flex-direction: column;
  }
  
  .home-sidebar {
    width: 100%;
    height: auto;
    flex-direction: row;
    padding: 10px;
    align-items: center;
  }
  
  .sidebar-logo {
    padding: 0 10px;
    border-bottom: none;
    margin-bottom: 0;
    margin-right: 16px;
  }
  
  .sidebar-nav {
    display: flex;
    flex: 1;
    justify-content: center;
    padding: 0;
  }
  
  .nav-item {
    padding: 8px 10px;
    margin-bottom: 0;
    margin-right: 6px;
  }
  
  .nav-text {
    display: none;
  }
  
  .sidebar-footer {
    display: none;
  }
  
  .home-main {
    height: auto;
    flex: 1;
  }
  
  .main-header {
    padding: 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .feature-card {
    width: 100%;
    margin: 0 0 12px;
  }
}
</style>
