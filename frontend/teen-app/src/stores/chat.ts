import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message, Session } from '@/types'
import { api } from '@/api/request'

const STORAGE_KEY = 'chat_sessions'
const FALLBACK_RESPONSES = [
  '我理解你的感受，想和我多聊聊吗？',
  '听起来你有些烦恼，我在这里陪你。',
  '每个人都会有情绪波动的时候，这很正常。',
  '谢谢你愿意和我分享，我会认真倾听的。',
  '我在这里，随时准备倾听你的心声。'
]

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<number>(0)
  const isTyping = ref(false)
  const isOnline = ref(true)
  const backendSessionId = ref<string | null>(null)

  const currentSession = computed(() => 
    sessions.value.find(s => s.id === currentSessionId.value)
  )

  const currentMessages = computed(() => 
    currentSession.value?.messages || []
  )

  function loadFromStorage() {
    try {
      const stored = uni.getStorageSync(STORAGE_KEY)
      if (stored) {
        sessions.value = JSON.parse(stored)
      }
    } catch (e) {
      console.error('加载会话失败', e)
    }
  }

  function saveToStorage() {
    try {
      uni.setStorageSync(STORAGE_KEY, JSON.stringify(sessions.value))
    } catch (e) {
      console.error('保存会话失败', e)
    }
  }

  async function createSession(): Promise<number> {
    try {
      const result = await api.chat.createSession()
      backendSessionId.value = result.session_id
      
      const newSession: Session = {
        id: Date.now(),
        title: '新对话',
        messages: [],
        messageCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
      }
      sessions.value.unshift(newSession)
      currentSessionId.value = newSession.id
      saveToStorage()
      return newSession.id
    } catch (e) {
      console.error('创建会话失败', e)
      const newSession: Session = {
        id: Date.now(),
        title: '新对话',
        messages: [],
        messageCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
      }
      sessions.value.unshift(newSession)
      currentSessionId.value = newSession.id
      saveToStorage()
      return newSession.id
    }
  }

  function selectSession(sessionId: number) {
    currentSessionId.value = sessionId
  }

  function updateSessionTitle(sessionId: number, title: string) {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session && title.trim()) {
      session.title = title.trim()
      session.updatedAt = new Date()
      saveToStorage()
    }
  }

  function deleteSession(sessionId: number) {
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index > -1) {
      sessions.value.splice(index, 1)
      if (currentSessionId.value === sessionId) {
        if (sessions.value.length > 0) {
          currentSessionId.value = sessions.value[0].id
        } else {
          createSession()
        }
      }
      saveToStorage()
    }
  }

  function addMessage(sessionId: number, message: Message) {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.messages.push(message)
      session.messageCount = session.messages.length
      session.updatedAt = new Date()
      
      if (session.title === '新对话' && message.role === 'user') {
        session.title = message.content.substring(0, 15) + (message.content.length > 15 ? '...' : '')
      }
      saveToStorage()
    }
  }

  async function sendMessage(content: string): Promise<boolean> {
    if (!content.trim() || isTyping.value) return false

    let sessionId = currentSessionId.value
    if (!sessionId) {
      await createSession()
      sessionId = currentSessionId.value
    }

    if (!backendSessionId.value) {
      try {
        const result = await api.chat.createSession()
        backendSessionId.value = result.session_id
      } catch (e) {
        console.error('创建后端会话失败', e)
      }
    }

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      createdAt: new Date()
    }
    addMessage(sessionId, userMessage)

    isTyping.value = true

    try {
      const response = await sendToAPI(backendSessionId.value || 'default', content)
      
      const assistantMessage: Message = {
        id: `msg_${Date.now()}_bot`,
        role: 'assistant',
        content: response.content,
        emotion: response.emotion,
        createdAt: new Date()
      }
      addMessage(sessionId, assistantMessage)

      if (response.alert) {
        uni.showModal({
          title: '温馨提示',
          content: '如果你正在经历困难时期，请记住有人愿意帮助你。可以拨打心理援助热线：400-161-9995',
          showCancel: false
        })
      }

      return true
    } catch (e) {
      console.error('发送消息失败', e)
      
      const fallbackMessage: Message = {
        id: `msg_${Date.now()}_bot`,
        role: 'assistant',
        content: FALLBACK_RESPONSES[Math.floor(Math.random() * FALLBACK_RESPONSES.length)],
        createdAt: new Date()
      }
      addMessage(sessionId, fallbackMessage)
      
      return false
    } finally {
      isTyping.value = false
    }
  }

  async function sendToAPI(sessionId: string, content: string): Promise<{ content: string; emotion?: any; alert?: boolean }> {
    try {
      const result = await api.chat.sendMessage(sessionId, content)
      return {
        content: result.botMessage?.content || result.content || '我收到了你的消息。',
        emotion: result.botMessage?.emotion || result.emotion,
        alert: result.alert
      }
    } catch (e) {
      throw e
    }
  }

  function clearCurrentMessages() {
    const session = sessions.value.find(s => s.id === currentSessionId.value)
    if (session) {
      session.messages = []
      session.messageCount = 0
      saveToStorage()
    }
  }

  async function init() {
    loadFromStorage()
    if (sessions.value.length === 0) {
      await createSession()
    } else {
      currentSessionId.value = sessions.value[0].id
    }
  }

  return {
    sessions,
    currentSessionId,
    currentSession,
    currentMessages,
    isTyping,
    isOnline,
    init,
    createSession,
    selectSession,
    updateSessionTitle,
    deleteSession,
    sendMessage,
    clearCurrentMessages,
    loadFromStorage,
    saveToStorage
  }
})
