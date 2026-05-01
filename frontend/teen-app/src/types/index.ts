export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  emotion?: EmotionResult
  createdAt: Date | string
}

export interface Session {
  id: string
  title: string
  messages: Message[]
  messageCount: number
  createdAt: Date | string
  updatedAt: Date | string
  lastMessageAt?: string
}

export interface EmotionResult {
  primary: string
  score: number
  secondary?: string
  secondaryScore?: number
}

export interface UserInfo {
  id: number
  phone: string
  nickname: string
  avatar: string
  userType: number
}

export interface Assessment {
  id: number
  title: string
  description: string
  icon: string
  questions: number
  time: number
  category: string
}

export interface Resource {
  id: number
  title: string
  description: string
  icon: string
  category: string
  categoryName: string
  views: number
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: number
}
