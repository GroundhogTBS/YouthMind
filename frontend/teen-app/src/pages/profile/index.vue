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
        <view class="avatar-wrapper" @click="chooseAvatar">
          <image v-if="avatarUrl" class="avatar-image" :src="avatarUrl" mode="aspectFill" />
          <text v-else class="avatar-letter">{{ userInfo.nickname ? userInfo.nickname.charAt(0).toUpperCase() : 'U' }}</text>
          <view class="avatar-edit-icon">
            <text>+</text>
          </view>
        </view>
        <view class="user-info">
          <text class="username">{{ userInfo.nickname || '用户' }}</text>
          <text class="user-desc">{{ userInfo.signature || '每天进步一点点' }}</text>
        </view>
        <view class="edit-btn" @click="showEditModal = true">
          <text>编辑</text>
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
          <text class="stat-value">{{ stats.emotionRecords }}</text>
          <text class="stat-label">情绪记录</text>
        </view>
      </view>

      <view class="menu-section">
        <view class="menu-item" @click="handleMenuClick('diary')">
          <view class="menu-icon-wrapper diary-icon">
            <text class="menu-icon-text">D</text>
          </view>
          <text class="menu-text">我的日记</text>
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
        <view class="menu-item" @click="handleMenuClick('emotions')">
          <view class="menu-icon-wrapper">
            <text class="menu-icon-text">E</text>
          </view>
          <text class="menu-text">情绪趋势</text>
          <text class="menu-arrow">›</text>
        </view>
        <view v-if="isAdmin" class="menu-item admin-item" @click="handleMenuClick('admin')">
          <view class="menu-icon-wrapper admin-icon">
            <text class="menu-icon-text">A</text>
          </view>
          <text class="menu-text">管理后台</text>
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

    <view class="modal-overlay" v-if="showEditModal" @click="showEditModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑资料</text>
          <view class="modal-close" @click="showEditModal = false">
            <text>×</text>
          </view>
        </view>
        <view class="modal-body">
          <view class="form-item avatar-edit-item">
            <text class="form-label">头像</text>
            <view class="avatar-edit-wrapper" @click="chooseAvatarInModal">
              <image v-if="editForm.avatar" class="avatar-edit-image" :src="editForm.avatar" mode="aspectFill" />
              <view v-else class="avatar-edit-placeholder">
                <text>{{ editForm.nickname ? editForm.nickname.charAt(0).toUpperCase() : 'U' }}</text>
              </view>
              <text class="avatar-edit-hint">点击更换</text>
            </view>
          </view>
          <view class="form-item">
            <text class="form-label">昵称</text>
            <input class="form-input" v-model="editForm.nickname" placeholder="请输入昵称" />
          </view>
          <view class="form-item">
            <text class="form-label">个性签名</text>
            <textarea class="form-textarea" v-model="editForm.signature" placeholder="写一句话介绍自己" />
          </view>
          <view class="form-item">
            <text class="form-label">年龄段</text>
            <picker mode="selector" :value="ageGroupIndex" :range="ageGroups" @change="onAgeGroupChange">
              <view class="form-picker">
                <text>{{ ageGroups[ageGroupIndex] }}</text>
                <text class="picker-arrow">▼</text>
              </view>
            </picker>
          </view>
        </view>
        <view class="modal-footer">
          <view class="cancel-btn" @click="showEditModal = false">
            <text>取消</text>
          </view>
          <view class="confirm-btn" @click="saveProfile">
            <text>保存</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useNavStore } from '@/stores/nav'
import { useUserStore } from '@/stores/user'
import { api } from '@/api/request'

const navStore = useNavStore()
const userStore = useUserStore()

const userInfo = ref({
  nickname: '',
  signature: '',
  age_group: ''
})

const stats = ref({
  chatDays: 0,
  assessments: 0,
  emotionRecords: 0
})

const isAdmin = ref(false)
const showEditModal = ref(false)
const ageGroups = ['未选择', '12岁以下', '12-15岁', '15-18岁', '18-25岁', '25岁以上']
const ageGroupIndex = ref(0)
const avatarUrl = ref('')

const editForm = reactive({
  nickname: '',
  signature: '',
  age_group: '',
  avatar: ''
})

onMounted(async () => {
  userStore.checkLogin()
  
  if (!userStore.isLoggedIn) {
    uni.redirectTo({ url: '/pages/auth/login' })
    return
  }
  
  await loadUserInfo()
  await loadStats()
})

async function loadUserInfo() {
  try {
    const data = await api.user.getProfile()
    userInfo.value = {
      nickname: data.nickname || '',
      signature: data.signature || '',
      age_group: data.age_group || ''
    }
    editForm.nickname = data.nickname || ''
    editForm.signature = data.signature || ''
    editForm.age_group = data.age_group || ''
    editForm.avatar = data.avatar || ''
    
    const idx = ageGroups.indexOf(data.age_group || '未选择')
    ageGroupIndex.value = idx >= 0 ? idx : 0
    
    isAdmin.value = data.phone === 'admin' || data.phone === '13800138000' || data.user_type === 'admin'
    avatarUrl.value = data.avatar || ''
  } catch (e) {
    console.error('加载用户信息失败', e)
    uni.showToast({ title: '网络错误，请检查连接', icon: 'none' })
  }
}

async function loadStats() {
  try {
    const data = await api.user.getStats()
    stats.value = {
      chatDays: data.chat_days || 0,
      assessments: data.assessments || 0,
      emotionRecords: data.emotion_records || 0
    }
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
}

function onAgeGroupChange(e: any) {
  const index = parseInt(e.detail.value)
  ageGroupIndex.value = index
  editForm.age_group = ageGroups[index]
  console.log('年龄段选择:', index, editForm.age_group)
}

async function saveProfile() {
  try {
    await api.user.updateProfile({
      nickname: editForm.nickname,
      signature: editForm.signature,
      age_group: editForm.age_group,
      avatar: editForm.avatar
    })
    
    userInfo.value = { 
      nickname: editForm.nickname,
      signature: editForm.signature,
      age_group: editForm.age_group
    }
    avatarUrl.value = editForm.avatar
    userStore.updateUserInfo(editForm)
    
    showEditModal.value = false
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

function handleGoBack() {
  navStore.resetToHome()
  uni.navigateBack()
}

function handleMenuClick(page: string) {
  if (page === 'diary') {
    uni.navigateTo({ url: '/pages/diary/index' })
  } else if (page === 'history') {
    uni.navigateTo({ url: '/pages/assessment/index' })
  } else if (page === 'favorites') {
    uni.navigateTo({ url: '/pages/resource/index?tab=favorites' })
  } else if (page === 'emotions') {
    uni.navigateTo({ url: '/pages/emotion/index' })
  } else if (page === 'admin') {
    uni.navigateTo({ url: '/pages/admin/index' })
  }
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

function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0]
      try {
        uni.showLoading({ title: '上传中...' })
        const uploadRes = await uploadAvatarFile(tempFilePath)
        avatarUrl.value = uploadRes.file_path
        await api.user.updateProfile({ avatar: uploadRes.file_path })
        uni.showToast({ title: '头像已更新', icon: 'success' })
      } catch (e) {
        console.error('上传头像失败', e)
        uni.showToast({ title: '上传失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    }
  })
}

function chooseAvatarInModal() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0]
      try {
        uni.showLoading({ title: '上传中...' })
        const uploadRes = await uploadAvatarFile(tempFilePath)
        editForm.avatar = uploadRes.file_path
        uni.showToast({ title: '头像已上传，请保存', icon: 'none' })
      } catch (e) {
        console.error('上传头像失败', e)
        uni.showToast({ title: '上传失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    }
  })
}

async function uploadAvatarFile(filePath: string): Promise<any> {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: 'http://localhost:9000/ai/upload/avatar',
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${userStore.token}`
      },
      success: (uploadRes) => {
        try {
          const data = JSON.parse(uploadRes.data)
          resolve(data)
        } catch (e) {
          reject(e)
        }
      },
      fail: reject
    })
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
  position: relative;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-letter {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.avatar-edit-icon {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 20px;
  height: 20px;
  background: $primary-color;
  border-radius: 50%;
  @include flex-center;
  border: 2px solid #fff;
  
  text {
    font-size: 12px;
    color: #fff;
    line-height: 1;
  }
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

.edit-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: $radius-md;
  
  text {
    font-size: $font-size-sm;
    color: #fff;
  }
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

.admin-item {
  background: rgba($primary-color, 0.05);
}

.admin-icon {
  background: rgba($primary-color, 0.15);
}

.diary-icon {
  background: rgba($warning-color, 0.15);
  
  .menu-icon-text {
    color: $warning-color;
  }
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  @include flex-center;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  width: 85%;
  max-width: 400px;
  background: $bg-primary;
  border-radius: $radius-xl;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { 
    transform: translateY(20px);
    opacity: 0;
  }
  to { 
    transform: translateY(0);
    opacity: 1;
  }
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
  margin-bottom: $spacing-lg;
}

.avatar-edit-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-edit-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-md;
}

.avatar-edit-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
}

.avatar-edit-placeholder {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, $primary-color, rgba($primary-color, 0.8));
  border-radius: 50%;
  @include flex-center;
  
  text {
    font-size: 32px;
    font-weight: 700;
    color: #fff;
  }
}

.avatar-edit-hint {
  font-size: $font-size-xs;
  color: $primary-color;
  margin-top: $spacing-sm;
}

.form-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-bottom: $spacing-sm;
  display: block;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  font-size: $font-size-base;
  color: $text-primary;
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

.form-picker {
  width: 100%;
  height: 44px;
  padding: 0 $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: $font-size-base;
  color: $text-primary;
}

.picker-arrow {
  font-size: 12px;
  color: $text-muted;
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
