<template>
  <view class="login-page">
    <view class="logo-section">
      <view class="logo-icon-wrapper">
        <text class="logo-icon-text">Y</text>
      </view>
      <text class="logo-text">YouthMind</text>
      <text class="slogan">你的心理陪伴伙伴</text>
    </view>

    <view class="form-section">
      <view class="input-group">
        <input 
          ref="phoneInput"
          v-model="phone"
          class="input"
          type="number"
          placeholder="请输入手机号"
          maxlength="11"
          :focus="true"
        />
      </view>

      <view class="login-btn" :class="{ disabled: !canSubmit || loading }" @click="handleLogin">
        <text>{{ loading ? '登录中...' : '登录 / 注册' }}</text>
      </view>

      <view class="tips">
        <text class="tips-text">首次登录将自动创建账号</text>
      </view>
    </view>

    <view class="footer">
      <text class="agreement">登录即表示同意《用户协议》和《隐私政策》</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { api } from '@/api/request'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const phone = ref('')
const loading = ref(false)

const canSubmit = computed(() => {
  return phone.value.length === 11
})

async function handleLogin() {
  if (!canSubmit.value || loading.value) return
  
  loading.value = true
  
  try {
    const result = await api.auth.login(phone.value)
    
    if (!result.token) {
      throw new Error('登录失败：未获取到令牌')
    }
    
    userStore.setToken(result.token, '')
    userStore.setUserInfo(result.user)
    
    uni.showToast({ title: '登录成功', icon: 'success' })
    
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/home/index' })
    }, 800)
  } catch (e: any) {
    console.error('登录失败', e)
    uni.showToast({ 
      title: e.message || '登录失败', 
      icon: 'none' 
    })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.login-page {
  min-height: 100vh;
  background: $bg-secondary;
  padding: 0 $spacing-2xl;
  display: flex;
  flex-direction: column;
}

.logo-section {
  padding-top: 80px;
  text-align: center;
  margin-bottom: 60px;
}

.logo-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  border-radius: 50%;
  @include flex-center;
  margin: 0 auto $spacing-md;
}

.logo-icon-text {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  color: $primary-color;
  display: block;
  margin-bottom: $spacing-sm;
}

.slogan {
  font-size: $font-size-base;
  color: $text-muted;
}

.form-section {
  flex: 1;
}

.input-group {
  margin-bottom: $spacing-lg;
  position: relative;
}

.input {
  width: 100%;
  height: 52px;
  background: $bg-primary;
  border-radius: $radius-lg;
  padding: 0 $spacing-lg;
  font-size: $font-size-lg;
  color: $text-primary;
  border: 1px solid $border-light;
  box-sizing: border-box;
}

.login-btn {
  width: 100%;
  height: 52px;
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  border-radius: $radius-full;
  @include flex-center;
  margin-top: $spacing-xl;
  
  text {
    font-size: $font-size-lg;
    color: #fff;
    font-weight: 500;
  }
  
  &.disabled {
    opacity: 0.5;
  }
}

.tips {
  text-align: center;
  margin-top: $spacing-lg;
}

.tips-text {
  font-size: $font-size-sm;
  color: $text-muted;
}

.footer {
  padding: $spacing-2xl 0;
  text-align: center;
}

.agreement {
  font-size: $font-size-xs;
  color: $text-muted;
}
</style>
