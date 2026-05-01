import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message, Session } from '@/types'
import { api } from '@/api/request'
import { useUserStore } from './user'

const FALLBACK_RESPONSES = [
  '我理解你的感受，想和我多聊聊吗？',
  '听起来你有些烦恼，我在这里陪你。',
  '每个人都会有情绪波动的时候，这很正常。',
  '谢谢你愿意和我分享，我会认真倾听的。',
  '我在这里，随时准备倾听你的心声。'
]

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string>('')
  const isTyping = ref(false)
  const typingSessionId = ref<string>('')
  const isOnline = ref(true)
  const sidebarVisible = ref(false)

  const currentSession = computed(() => 
    sessions.value.find(s => s.id === currentSessionId.value)
  )

  const currentMessages = computed(() => 
    currentSession.value?.messages || []
  )

  const isCurrentSessionTyping = computed(() => 
    isTyping.value && typingSessionId.value === currentSessionId.value
  )

  function toggleSidebar() {
    sidebarVisible.value = !sidebarVisible.value
  }

  function hideSidebar() {
    sidebarVisible.value = false
  }

  async function loadSessions(): Promise<void> {
    const userStore = useUserStore()
    if (!userStore.isLoggedIn) {
      sessions.value = []
      currentSessionId.value = ''
      return
    }

    try {
      const result = await api.chat.getSessions()
      sessions.value = result.map((s: any) => ({
        id: s.session_id,
        title: s.title || '新对话',
        messages: [],
        messageCount: s.message_count || 0,
        createdAt: new Date(s.created_at),
        updatedAt: new Date(s.updated_at)
      }))
      
      if (sessions.value.length > 0 && !currentSessionId.value) {
        currentSessionId.value = sessions.value[0].id
      }
    } catch (e) {
      console.error('加载会话列表失败', e)
    }
  }

  async function loadHistory(sessionId: string): Promise<void> {
    try {
      const result = await api.chat.getHistory(sessionId)
      const session = sessions.value.find(s => s.id === sessionId)
      if (session && result.messages) {
        session.messages = result.messages.map((m: any) => ({
          id: String(m.id),
          role: m.role,
          content: m.content,
          emotion: typeof m.emotion === 'string' ? { primary: m.emotion } : m.emotion,
          createdAt: new Date(m.createdAt)
        }))
      }
    } catch (e) {
      console.error('加载历史消息失败', e)
    }
  }

  async function createSession(): Promise<string> {
    const userStore = useUserStore()
    
    try {
      const result = await api.chat.createSession()
      const newSession: Session = {
        id: result.session_id,
        title: result.title || '新对话',
        messages: [],
        messageCount: 0,
        createdAt: new Date(result.created_at),
        updatedAt: new Date(result.updated_at)
      }
      sessions.value.unshift(newSession)
      currentSessionId.value = newSession.id
      return newSession.id
    } catch (e) {
      console.error('创建会话失败', e)
      if (!userStore.isLoggedIn) {
        uni.showToast({ title: '请先登录', icon: 'none' })
      }
      throw e
    }
  }

  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
    const session = sessions.value.find(s => s.id === sessionId)
    if (session && session.messages.length === 0) {
      await loadHistory(sessionId)
    }
    hideSidebar()
  }

  async function updateSessionTitle(sessionId: string, title: string) {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session && title.trim()) {
      try {
        await api.chat.updateSession(sessionId, title.trim())
        session.title = title.trim()
        session.updatedAt = new Date()
      } catch (e) {
        console.error('更新会话标题失败', e)
      }
    }
  }

  async function deleteSession(sessionId: string) {
    try {
      await api.chat.deleteSession(sessionId)
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
      }
    } catch (e) {
      console.error('删除会话失败', e)
    }
  }

  function addMessage(sessionId: string, message: Message) {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.messages.push(message)
      session.messageCount = session.messages.length
      session.updatedAt = new Date()
      
      if (session.title === '新对话' && message.role === 'user') {
        session.title = message.content.substring(0, 15) + (message.content.length > 15 ? '...' : '')
      }
    }
  }

  async function sendMessage(content: string): Promise<boolean> {
    if (!content.trim()) return false

    const userStore = useUserStore()
    if (!userStore.isLoggedIn) {
      uni.showModal({
        title: '提示',
        content: '请先登录后再开始对话',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            uni.navigateTo({ url: '/pages/auth/login' })
          }
        }
      })
      return false
    }

    let sessionId = currentSessionId.value
    if (!sessionId) {
      try {
        sessionId = await createSession()
      } catch (e) {
        return false
      }
    }

    const sessionTyping = isTyping.value && typingSessionId.value === sessionId
    if (sessionTyping) return false

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      createdAt: new Date()
    }
    addMessage(sessionId, userMessage)

    isTyping.value = true
    typingSessionId.value = sessionId

    try {
      const result = await api.chat.sendMessage(sessionId, content)
      
      const assistantMessage: Message = {
        id: `msg_${Date.now()}_bot`,
        role: 'assistant',
        content: result.content || '我收到了你的消息。',
        emotion: result.emotion,
        createdAt: new Date()
      }
      addMessage(sessionId, assistantMessage)

      if (result.alert) {
        uni.showModal({
          title: '温馨提示',
          content: '如果你正在经历困难时期，请记住有人愿意帮助你。可以拨打心理援助热线：400-161-9995',
          showCancel: false
        })
      }

      uni.vibrateShort({ type: 'light' })
      uni.showToast({ 
        title: 'AI已回复', 
        icon: 'none', 
        duration: 1500 
      })

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
      typingSessionId.value = ''
    }
  }

  function clearCurrentMessages() {
    const session = sessions.value.find(s => s.id === currentSessionId.value)
    if (session) {
      session.messages = []
      session.messageCount = 0
    }
  }

  async function init() {
    const userStore = useUserStore()
    userStore.checkLogin()
    
    if (userStore.isLoggedIn) {
      await loadSessions()
      if (sessions.value.length === 0) {
        await createSession()
      } else {
        currentSessionId.value = sessions.value[0].id
        await loadHistory(currentSessionId.value)
      }
    }
  }

  return {
    sessions,
    currentSessionId,
    currentSession,
    currentMessages,
    isTyping,
    isCurrentSessionTyping,
    typingSessionId,
    isOnline,
    sidebarVisible,
    toggleSidebar,
    hideSidebar,
    init,
    loadSessions,
    loadHistory,
    createSession,
    selectSession,
    updateSessionTitle,
    deleteSession,
    sendMessage,
    clearCurrentMessages
  }
})
