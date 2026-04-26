<template>
  <view class="profile-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">个人中心</text>
      </view>
      <view class="header-right"></view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false">
      <view class="user-card">
        <view class="avatar-wrapper">
          <text class="avatar-letter">{{ userInfo.nickname ? userInfo.nickname.charAt(0).toUpperCase() : 'U' }}</text>
        </view>
        <view class="user-info">
          <text class="username">{{ userInfo.nickname || '用户' }}</text>
          <text class="user-desc">{{ userInfo.signature || '每天进步一点点' }}</text>
        </view>
      </view>

      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ stats.chatDays }}</text>
          <text class="stat-label">倾诉天数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.assessments }}</text>
          <text class="stat-label">测评次数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.resources }}</text>
          <text class="stat-label">学习资源</text>
        </view>
      </view>

      <view class="menu-section">
        <view class="menu-item" @click="handleMenuClick('profile')">
          <view class="menu-icon-wrapper">
            <text class="menu-icon-text">P</text>
          </view>
          <text class="menu-text">个人资料</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="handleMenuClick('history')">
          <view class="menu-icon-wrapper">
            <text class="menu-icon-text">H</text>
          </view>
          <text class="menu-text">测评记录</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="handleMenuClick('favorites')">
          <view class="menu-icon-wrapper">
            <text class="menu-icon-text">F</text>
          </view>
          <text class="menu-text">我的收藏</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="handleMenuClick('feedback')">
          <view class="menu-icon-wrapper">
            <text class="menu-icon-text">B</text>
          </view>
          <text class="menu-text">意见反馈</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="handleMenuClick('settings')">
          <view class="menu-icon-wrapper">
            <text class="menu-icon-text">S</text>
          </view>
          <text class="menu-text">设置</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="help-section">
        <view class="help-card" @click="handleCallHotline">
          <view class="help-icon-wrapper">
            <text class="help-icon-text">!</text>
          </view>
          <view class="help-info">
            <text class="help-title">心理援助热线</text>
            <text class="help-desc">400-161-9995（24小时）</text>
          </view>
        </view>
      </view>

      <view class="logout-section">
        <view class="logout-btn" @click="handleLogout">
          <text>退出登录</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useNavStore } from '@/stores/nav'
import { useUserStore } from '@/stores/user'

const navStore = useNavStore()
const userStore = useUserStore()

const userInfo = ref({
  nickname: '',
  signature: ''
})

const stats = ref({
  chatDays: 0,
  assessments: 0,
  resources: 0
})

onMounted(() => {
  userStore.checkLogin()
  if (userStore.userInfo) {
    userInfo.value = {
      nickname: userStore.userInfo.nickname || '',
      signature: userStore.userInfo.signature || ''
    }
  }
})

function handleGoBack() {
  navStore.resetToHome()
  uni.navigateBack()
}

function handleMenuClick(page: string) {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function handleCallHotline() {
  uni.makePhoneCall({ phoneNumber: '4001619995' })
}

function handleLogout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.profile-page {
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

.back-btn {
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

.page-content {
  flex: 1;
  height: 0;
}

.user-card {
  margin: $spacing-lg;
  padding: $spacing-xl;
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  border-radius: $radius-xl;
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  @include flex-center;
  border: 2px solid rgba(255, 255, 255, 0.3);
  margin-right: $spacing-lg;
  flex-shrink: 0;
}

.avatar-letter {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.user-info {
  flex: 1;
}

.username {
  font-size: $font-size-xl;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: $spacing-xs;
}

.user-desc {
  font-size: $font-size-sm;
  color: rgba(255, 255, 255, 0.8);
}

.stats-card {
  margin: 0 $spacing-lg $spacing-lg;
  padding: $spacing-lg;
  background: $bg-primary;
  border-radius: $radius-xl;
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.stat-item {
  @include flex-column;
  align-items: center;
}

.stat-value {
  font-size: $font-size-2xl;
  font-weight: 700;
  color: $primary-color;
}

.stat-label {
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: $spacing-xs;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: $border-light;
}

.menu-section {
  margin: 0 $spacing-lg;
  background: $bg-primary;
  border-radius: $radius-xl;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-light;
  
  &:last-child {
    border-bottom: none;
  }
}

.menu-icon-wrapper {
  width: 32px;
  height: 32px;
  background: $bg-secondary;
  border-radius: $radius-md;
  @include flex-center;
  margin-right: $spacing-md;
  flex-shrink: 0;
}

.menu-icon-text {
  font-size: 14px;
  font-weight: 600;
  color: $primary-color;
}

.menu-text {
  flex: 1;
  font-size: $font-size-base;
  color: $text-primary;
}

.menu-arrow {
  font-size: $font-size-lg;
  color: $text-light;
}

.help-section {
  margin: $spacing-lg;
}

.help-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: rgba($warning-color, 0.1);
  border-radius: $radius-xl;
  border: 1px solid rgba($warning-color, 0.2);
}

.help-icon-wrapper {
  width: 40px;
  height: 40px;
  background: rgba($warning-color, 0.2);
  border-radius: $radius-md;
  @include flex-center;
  margin-right: $spacing-md;
  flex-shrink: 0;
}

.help-icon-text {
  font-size: 20px;
  font-weight: 700;
  color: $warning-color;
}

.help-info {
  flex: 1;
}

.help-title {
  font-size: $font-size-base;
  font-weight: 500;
  color: $text-primary;
  display: block;
}

.help-desc {
  font-size: $font-size-sm;
  color: $text-muted;
}

.logout-section {
  margin: $spacing-lg;
  padding-bottom: $spacing-2xl;
}

.logout-btn {
  width: 100%;
  height: 48px;
  background: $bg-primary;
  border-radius: $radius-xl;
  @include flex-center;
  border: 1px solid $danger-color;
  
  text {
    font-size: $font-size-base;
    color: $danger-color;
  }
}
</style>
