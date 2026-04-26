<template>
  <view class="chat-list-page">
    <view class="header">
      <text class="title">我的对话</text>
      <view class="new-chat" @click="createNewChat">
        <text>+ 新对话</text>
      </view>
    </view>
    
    <view class="session-list">
      <view 
        v-for="session in sessions" 
        :key="session.id" 
        class="session-item"
        @click="goToChat(session.id)"
      >
        <view class="session-info">
          <text class="session-title">{{ session.title || '新对话' }}</text>
          <text class="session-time">{{ formatTime(session.lastMessageAt) }}</text>
        </view>
        <text class="session-preview">{{ session.lastMessage || '开始聊天吧...' }}</text>
      </view>
    </view>
    
    <view v-if="sessions.length === 0" class="empty-state">
      <text class="empty-text">还没有对话记录</text>
      <view class="start-btn" @click="createNewChat">
        <text>开始第一次对话</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Session {
  id: number
  title: string
  lastMessage: string
  lastMessageAt: string
}

const sessions = ref<Session[]>([])

onMounted(async () => {
  await loadSessions()
})

async function loadSessions() {
  sessions.value = []
}

function createNewChat() {
  uni.navigateTo({ url: '/pages/chat/index' })
}

function goToChat(sessionId: number) {
  uni.navigateTo({ url: `/pages/chat/index?sessionId=${sessionId}` })
}

function formatTime(time: string) {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<style lang="scss" scoped>
.chat-list-page {
  min-height: 100vh;
  background: #f8f8f8;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  background: #fff;
}

.title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.new-chat {
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
  border-radius: 30rpx;
  color: #fff;
  font-size: 26rpx;
}

.session-list {
  padding: 20rpx;
}

.session-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}

.session-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.session-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
}

.session-time {
  font-size: 24rpx;
  color: #999;
}

.session-preview {
  font-size: 26rpx;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.start-btn {
  padding: 24rpx 48rpx;
  background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
  border-radius: 40rpx;
  color: #fff;
  font-size: 28rpx;
}
</style>
