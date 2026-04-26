<template>
  <view class="home-page">
    <view class="home-sidebar">
      <view class="sidebar-logo">
        <view class="logo-mark">Y</view>
        <text class="logo-text">YouthMind</text>
      </view>
      <view class="sidebar-nav">
        <view class="nav-item" :class="{ active: navStore.currentPage === 'home' }" @click="stayHome">
          <view class="nav-icon">
            <text class="icon-text">H</text>
          </view>
          <text class="nav-text">首页</text>
        </view>
        <view class="nav-item" :class="{ active: navStore.currentPage === 'chat' }" @click="goToChat">
          <view class="nav-icon">
            <text class="icon-text">C</text>
          </view>
          <text class="nav-text">AI对话</text>
        </view>
        <view class="nav-item" :class="{ active: navStore.currentPage === 'assessment' }" @click="goToAssessment">
          <view class="nav-icon">
            <text class="icon-text">A</text>
          </view>
          <text class="nav-text">心理测评</text>
        </view>
        <view class="nav-item" :class="{ active: navStore.currentPage === 'resource' }" @click="goToResource">
          <view class="nav-icon">
            <text class="icon-text">R</text>
          </view>
          <text class="nav-text">学习资源</text>
        </view>
      </view>
      <view class="sidebar-footer">
        <view class="user-info" @click="goToProfile">
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
        <view class="action-btn" @click="goToChat">
          <text class="btn-text">开始对话</text>
        </view>
      </view>
      
      <view class="main-content">
        <view class="feature-grid">
          <view class="feature-card" @click="goToChat">
            <view class="card-icon-wrapper purple">
              <text class="card-icon-letter">C</text>
            </view>
            <text class="card-title">AI心理助手</text>
            <text class="card-desc">随时倾诉心声，AI陪伴倾听你的烦恼</text>
            <text class="card-action">开始对话</text>
          </view>
          
          <view class="feature-card" @click="goToAssessment">
            <view class="card-icon-wrapper pink">
              <text class="card-icon-letter">A</text>
            </view>
            <text class="card-title">心理测评</text>
            <text class="card-desc">专业量表测评，了解自己的心理状态</text>
            <text class="card-action">开始测评</text>
          </view>
          
          <view class="feature-card" @click="goToResource">
            <view class="card-icon-wrapper blue">
              <text class="card-icon-letter">R</text>
            </view>
            <text class="card-title">学习资源</text>
            <text class="card-desc">心理健康知识库，助力成长每一步</text>
            <text class="card-action">浏览资源</text>
          </view>
          
          <view class="feature-card">
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

const navStore = useNavStore()
const userStore = useUserStore()

onMounted(() => {
  navStore.resetToHome()
  userStore.checkLogin()
  
  if (!userStore.isLoggedIn) {
    uni.redirectTo({ url: '/pages/auth/login' })
  }
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

const articles = ref([
  { category: '情绪', title: '如何应对考试焦虑', summary: '考试前的紧张是正常的，学会这些方法让你轻松应对' },
  { category: '人际', title: '和朋友吵架了怎么办', summary: '友谊中的冲突可以这样化解，让关系更紧密' },
  { category: '成长', title: '提升自信心的方法', summary: '相信自己，你比想象中更优秀' }
])

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

function selectMood(mood: string) {
  uni.showToast({ title: '已记录心情', icon: 'success' })
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

@media screen and (max-width: 1200px) {
  .article-card {
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
