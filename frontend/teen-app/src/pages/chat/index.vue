<template>
  <view class="chat-page">
    <view class="sidebar-overlay" v-if="chatStore.sidebarVisible" @click="chatStore.hideSidebar"></view>
    
    <view class="chat-sidebar" :class="{ visible: chatStore.sidebarVisible }">
      <view class="sidebar-header">
        <text class="sidebar-title">对话记录</text>
        <view class="new-chat-btn" @click="handleNewChat" title="新建对话">
          <text>+ 新对话</text>
        </view>
      </view>
      <scroll-view class="session-list" scroll-y :show-scrollbar="false">
        <view v-if="chatStore.sessions.length === 0" class="empty-state">
          <text class="empty-text">暂无对话记录</text>
          <text class="empty-hint">点击"新对话"开始聊天</text>
        </view>
        <view 
          v-for="session in chatStore.sessions" 
          :key="session.id"
          class="session-item"
          :class="{ active: chatStore.currentSessionId === session.id }"
          @click="handleSelectSession(session.id)"
        >
          <view class="session-info">
            <text class="session-title" v-if="editingId !== session.id">{{ session.title || '新对话' }}</text>
            <input 
              v-else
              class="session-title-input"
              v-model="editingTitle"
              :focus="true"
              @blur="handleSaveTitle"
              @confirm="handleSaveTitle"
            />
            <text class="session-time">{{ formatTime(session.updatedAt) }}</text>
          </view>
          <view class="session-actions" v-if="chatStore.currentSessionId === session.id">
            <text class="action-btn" @click.stop="handleEditTitle(session)">编辑</text>
            <text class="action-btn delete" @click.stop="handleDeleteSession(session.id)">删除</text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <view class="chat-main">
      <view class="chat-header">
        <view class="header-left">
          <view class="menu-btn" @click="chatStore.toggleSidebar" title="对话列表">
            <text class="menu-icon">☰</text>
          </view>
          <view class="back-btn" @click="handleGoBack">
            <text class="back-arrow">←</text>
          </view>
        </view>
        <view class="header-center">
          <text class="header-title">AI心理助手</text>
          <text class="header-subtitle">我在这里倾听你的心声</text>
        </view>
        <view class="header-right"></view>
      </view>
      
      <scroll-view 
        class="message-list"
        scroll-y
        :scroll-top="scrollTop"
        :scroll-with-animation="true"
        :show-scrollbar="false"
      >
        <view class="message-container">
          <view v-if="chatStore.currentMessages.length === 0" class="welcome-section">
            <view class="welcome-icon">
              <text class="icon-letter">AI</text>
            </view>
            <text class="welcome-title">你好，我是你的心理健康伙伴</text>
            <text class="welcome-desc">有什么想和我聊聊的吗？我会认真倾听你的心声</text>
            <view class="quick-topics">
              <view class="topic-item" @click="handleQuickMessage('今天心情不太好')">
                <text>心情不好</text>
              </view>
              <view class="topic-item" @click="handleQuickMessage('最近学习压力很大')">
                <text>学习压力</text>
              </view>
              <view class="topic-item" @click="handleQuickMessage('想找人聊聊天')">
                <text>想聊聊天</text>
              </view>
            </view>
          </view>
          
          <view 
            v-for="msg in chatStore.currentMessages" 
            :key="msg.id"
            class="message-item"
            :class="msg.role"
          >
            <view v-if="msg.role === 'user'" class="message-content user" @tap="handleCopy(msg.content)">
              <text selectable="true">{{ msg.content }}</text>
            </view>
            <view v-else class="message-content assistant">
              <view class="assistant-avatar">
                <text class="avatar-letter">AI</text>
              </view>
              <view class="message-bubble" @tap="handleCopy(msg.content)">
                <text selectable="true">{{ msg.content }}</text>
                <view v-if="msg.emotion" class="emotion-indicator">
                  <text class="emotion-text">检测到{{ getEmotionText(msg.emotion.primary) }}情绪</text>
                </view>
              </view>
            </view>
          </view>
          
          <view v-if="chatStore.isCurrentSessionTyping" class="typing-indicator">
            <view class="assistant-avatar">
              <text class="avatar-letter">AI</text>
            </view>
            <view class="typing-bubble">
              <view class="typing-dots">
                <view class="dot"></view>
                <view class="dot"></view>
                <view class="dot"></view>
              </view>
              <text>正在思考中...</text>
            </view>
          </view>
        </view>
      </scroll-view>
      
      <view class="input-area">
        <view class="input-wrapper">
          <input 
            ref="inputRef"
            v-model="inputText"
            class="text-input"
            placeholder="说点什么，我在听..."
            :maxlength="2000"
            confirm-type="send"
            :adjust-position="true"
            :always-embed="true"
            :hold-keyboard="true"
            @confirm="handleSend"
          />
        </view>
        <view class="send-btn" :class="{ disabled: !canSend }" @click="handleSend" title="发送消息">
          <text class="send-text">发送</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useNavStore } from '@/stores/nav'
import { useUserStore } from '@/stores/user'

const chatStore = useChatStore()
const navStore = useNavStore()

const inputText = ref('')
const scrollTop = ref(0)
const editingId = ref<string | null>(null)
const editingTitle = ref('')
const inputRef = ref<any>(null)

const canSend = computed(() => inputText.value.trim().length > 0 && !chatStore.isTyping)

onMounted(() => {
  const userStore = useUserStore()
  userStore.checkLogin()
  
  if (!userStore.isLoggedIn) {
    uni.redirectTo({ url: '/pages/auth/login' })
    return
  }
  
  navStore.setPage('chat')
  chatStore.init()
})

function handleGoBack() {
  navStore.resetToHome()
  uni.navigateBack()
}

async function handleNewChat() {
  await chatStore.createSession()
  chatStore.hideSidebar()
}

function handleSelectSession(id: string) {
  chatStore.selectSession(id)
}

function handleEditTitle(session: any) {
  editingId.value = session.id
  editingTitle.value = session.title || '新对话'
}

function handleSaveTitle() {
  if (editingId.value && editingTitle.value.trim()) {
    chatStore.updateSessionTitle(editingId.value, editingTitle.value)
  }
  editingId.value = null
  editingTitle.value = ''
}

function handleDeleteSession(id: string) {
  chatStore.deleteSession(id)
}

async function handleSend() {
  if (!canSend.value) return
  
  const content = inputText.value.trim()
  inputText.value = ''
  
  await chatStore.sendMessage(content)
  scrollToBottom()
}

function handleQuickMessage(content: string) {
  inputText.value = content
  handleSend()
}

function scrollToBottom() {
  nextTick(() => {
    const oldTop = scrollTop.value
    scrollTop.value = oldTop
    nextTick(() => { scrollTop.value = 99999 })
  })
}

function formatTime(date: any): string {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function getEmotionText(emotion: string): string {
  const map: Record<string, string> = {
    happy: '开心', sad: '难过', anxious: '焦虑', angry: '生气',
    fear: '恐惧', lonely: '孤独', confused: '迷茫', inferior: '自卑'
  }
  return map[emotion] || '平和'
}

function handleCopy(content: string) {
  uni.setClipboardData({
    data: content,
    success: () => {
      uni.showToast({ title: '已复制到剪贴板', icon: 'success', duration: 1500 })
    },
    fail: () => {
      uni.showToast({ title: '复制失败', icon: 'none', duration: 1500 })
    }
  })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.chat-page {
  width: 100%;
  height: 100vh;
  background: $bg-secondary;
  display: flex;
  flex-direction: row;
  position: relative;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
}

.chat-sidebar {
  width: 260px;
  height: 100vh;
  background: $bg-primary;
  border-right: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid $border-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
}

.new-chat-btn {
  padding: 8px 14px;
  background: $primary-color;
  border-radius: 8px;
  @include btn-hover;
  
  text {
    font-size: 13px;
    color: #fff;
    font-weight: 500;
  }
}

.session-list {
  flex: 1;
  padding: 8px;
  height: 0;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-text {
  font-size: 14px;
  color: $text-muted;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 12px;
  color: $text-light;
}

.session-item {
  padding: 12px 14px;
  border-radius: 8px;
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  @include clickable;
  
  &.active {
    background: rgba($primary-color, 0.1);
  }
}

.session-info {
  flex: 1;
  overflow: hidden;
}

.session-title {
  font-size: 14px;
  color: $text-primary;
  display: block;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-title-input {
  font-size: 14px;
  color: $text-primary;
  background: $bg-primary;
  border: 1px solid $primary-color;
  border-radius: 4px;
  padding: 4px 8px;
  width: 100%;
}

.session-time {
  font-size: 11px;
  color: $text-muted;
}

.session-actions {
  display: flex;
  gap: 8px;
  margin-left: 8px;
}

.action-btn {
  font-size: 11px;
  color: $primary-color;
  padding: 4px 8px;
  @include clickable;
  
  &.delete {
    color: $error-color;
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-width: 0;
}

.chat-header {
  background: $bg-primary;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid $border-light;
  flex-shrink: 0;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-btn {
  width: 36px;
  height: 36px;
  display: none;
  align-items: center;
  justify-content: center;
  background: $bg-secondary;
  border-radius: 8px;
}

.menu-icon {
  font-size: 18px;
  color: $text-primary;
}

.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-secondary;
  border-radius: 8px;
}

.back-arrow {
  font-size: 18px;
  color: $text-primary;
}

.header-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.header-subtitle {
  font-size: 12px;
  color: $text-muted;
  margin-top: 2px;
}

.message-list {
  flex: 1;
  width: 100%;
  height: 0;
}

.message-container {
  padding: 16px;
  min-height: 100%;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.welcome-icon {
  width: 64px;
  height: 64px;
  background: rgba($primary-color, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.icon-letter {
  font-size: 20px;
  font-weight: 700;
  color: $primary-color;
}

.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 10px;
}

.welcome-desc {
  font-size: 14px;
  color: $text-secondary;
  margin-bottom: 24px;
}

.quick-topics {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.topic-item {
  padding: 10px 16px;
  background: $bg-primary;
  border-radius: 20px;
  border: 1px solid $border-color;
  font-size: 13px;
  color: $text-secondary;
  @include clickable;
  
  &:hover {
    background: rgba($primary-color, 0.05);
    border-color: $primary-color;
    color: $primary-color;
  }
}

.message-item {
  margin-bottom: 16px;
  
  &.user {
    display: flex;
    justify-content: flex-end;
  }
  
  &.assistant {
    display: flex;
    justify-content: flex-start;
  }
}

.message-content.user {
  max-width: 70%;
  padding: 12px 16px;
  background: $primary-color;
  color: #fff;
  border-radius: 16px 16px 4px 16px;
  font-size: 14px;
  line-height: 1.6;
  @include clickable;
}

.message-content.assistant {
  display: flex;
  align-items: flex-start;
  max-width: 80%;
}

.assistant-avatar {
  width: 32px;
  height: 32px;
  background: rgba($primary-color, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  flex-shrink: 0;
}

.avatar-letter {
  font-size: 12px;
  font-weight: 700;
  color: $primary-color;
}

.message-bubble {
  background: $bg-primary;
  padding: 12px 16px;
  border-radius: 16px 16px 16px 4px;
  font-size: 14px;
  line-height: 1.6;
  color: $text-primary;
  border: 1px solid $border-light;
  @include clickable;
}

.emotion-indicator {
  display: flex;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid $border-light;
}

.emotion-text {
  font-size: 12px;
  color: $text-muted;
}

.typing-indicator {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
}

.typing-bubble {
  display: flex;
  align-items: center;
  background: $bg-primary;
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid $border-light;
  font-size: 13px;
  color: $text-muted;
}

.typing-dots {
  display: flex;
  margin-right: 10px;
  
  .dot {
    width: 6px;
    height: 6px;
    background: $primary-color;
    border-radius: 50%;
    margin-right: 4px;
    animation: typing 1.4s infinite ease-in-out both;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
}

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: $bg-primary;
  border-top: 1px solid $border-light;
  flex-shrink: 0;
  gap: 12px;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: $bg-secondary;
  border-radius: 20px;
  padding: 0 16px;
  height: 44px;
}

.text-input {
  flex: 1;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
  color: $text-primary;
  background: transparent;
}

.send-btn {
  width: 44px;
  height: 44px;
  background: $primary-color;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  @include btn-hover;
  
  &.disabled {
    opacity: 0.5;
  }
}

.send-text {
  color: #fff;
  font-size: 12px;
  font-weight: 500;
}

@media screen and (max-width: 768px) {
  .sidebar-overlay {
    display: block;
    opacity: 0;
    animation: fadeIn 0.3s ease forwards;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  .chat-sidebar {
    position: fixed;
    top: 0;
    left: -260px;
    z-index: 200;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateX(0);
    
    &.visible {
      transform: translateX(260px);
    }
  }
  
  .menu-btn {
    display: flex;
  }
}
</style>
