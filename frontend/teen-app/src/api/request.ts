const BASE_URL = 'http://localhost:9000'

interface RequestConfig {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  showLoading?: boolean
  showError?: boolean
}

class Request {
  private baseUrl: string

  constructor() {
    this.baseUrl = BASE_URL
  }

  private getToken(): string {
    const token = uni.getStorageSync('token')
    return token || ''
  }

  private showLoading(title: string = '加载中...') {
    uni.showLoading({ title, mask: true })
  }

  private hideLoading() {
    uni.hideLoading()
  }

  private showError(message: string) {
    uni.showToast({
      title: message || '请求失败',
      icon: 'none',
      duration: 2000
    })
  }

  async request<T = any>(config: RequestConfig): Promise<T> {
    const { url, method = 'GET', data, header = {}, showLoading: show = false, showError = true } = config

    if (show) {
      this.showLoading()
    }

    const token = this.getToken()
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
    header['Content-Type'] = header['Content-Type'] || 'application/json'

    console.log('[Request]', method, url, 'Token:', token ? 'exists' : 'none')

    return new Promise((resolve, reject) => {
      uni.request({
        url: `${this.baseUrl}${url}`,
        method,
        data,
        header,
        success: (res: any) => {
          if (show) {
            this.hideLoading()
          }

          console.log('[Response]', res.statusCode, url, res.data)

          if (res.statusCode === 200 || res.statusCode === 201) {
            resolve(res.data)
          } else if (res.statusCode === 400 || res.statusCode === 401) {
            const message = res.data?.detail || res.data?.message || '请求失败'
            if (showError) {
              this.showError(message)
            }
            reject(new Error(message))
          } else {
            const message = res.data?.detail || res.data?.message || '网络请求失败'
            if (showError) {
              this.showError(message)
            }
            reject(new Error(message))
          }
        },
        fail: (err: any) => {
          if (show) {
            this.hideLoading()
          }
          console.error('[Request Failed]', url, err)
          if (showError) {
            this.showError('网络连接失败')
          }
          reject(err)
        }
      })
    })
  }

  get<T = any>(url: string, params?: any, config?: Partial<RequestConfig>): Promise<T> {
    const queryString = params
      ? '?' + Object.keys(params)
          .map(key => `${key}=${encodeURIComponent(params[key])}`)
          .join('&')
      : ''
    return this.request<T>({
      url: `${url}${queryString}`,
      method: 'GET',
      ...config
    })
  }

  post<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({
      url,
      method: 'POST',
      data,
      ...config
    })
  }

  put<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({
      url,
      method: 'PUT',
      data,
      ...config
    })
  }

  delete<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({
      url,
      method: 'DELETE',
      data,
      ...config
    })
  }

  upload<T = any>(url: string, formData: FormData, config?: Partial<RequestConfig>): Promise<T> {
    const header = config?.header || {}
    delete header['Content-Type']

    return this.request<T>({
      url,
      method: 'POST',
      data: formData,
      header,
      ...config
    })
  }
}

export const request = new Request()

export const api = {
  auth: {
    sendSms: (phone: string) => request.post('/ai/user/sms', { phone }),
    login: (phone: string, code?: string) => request.post('/ai/user/login', { phone, code }),
    logout: () => request.post('/ai/user/logout'),
    getMe: () => request.get('/ai/user/me')
  },

  chat: {
    createSession: () => request.post('/ai/chat/session'),
    getSessions: () => request.get('/ai/chat/sessions'),
    getHistory: (sessionId: string) => request.get(`/ai/chat/history/${sessionId}`),
    sendMessage: (sessionId: string, content: string) => 
      request.post('/ai/chat/send', { session_id: sessionId, content }),
    deleteSession: (sessionId: string) => 
      request.delete(`/ai/chat/session/${sessionId}`),
    updateSession: (sessionId: string, title: string) => 
      request.put(`/ai/chat/session/${sessionId}`, { title }),
    getEmotionTrend: (sessionId: string) => 
      request.get(`/ai/chat/trend/${sessionId}`)
  },

  emotion: {
    analyze: (text: string) => 
      request.post('/ai/emotion/analyze', { text }),
    getTrend: (sessionId: string) => 
      request.get(`/ai/emotion/trend/${sessionId}`)
  },

  emotionRecord: {
    create: (data: { emotionType: string; intensity: number; triggers?: string; thoughts?: string; copingMethods?: string }) => 
      request.post('/ai/emotions', data),
    getRecent: (limit?: number) => 
      request.get('/ai/emotions/recent', limit ? { limit } : {}),
    getTrend: (days?: number) => 
      request.get('/ai/emotions/trend', days ? { days } : {}),
    getById: (id: number) => 
      request.get(`/ai/emotions/${id}`)
  },

  assessment: {
    getScales: () => 
      request.get('/ai/assessment/scales'),
    getScale: (scaleType: string) => 
      request.get(`/ai/assessment/scales/${scaleType}`),
    submit: (scaleType: string, answers: number[]) => 
      request.post('/ai/assessment/submit', { scaleType, answers }),
    getHistory: (limit?: number) => 
      request.get('/ai/assessment/history', limit ? { limit } : {}),
    getById: (id: number) => 
      request.get(`/ai/assessment/${id}`)
  },

  article: {
    getCategories: () => 
      request.get('/ai/articles/categories'),
    getList: (category?: string, limit?: number, offset?: number) => 
      request.get('/ai/articles', { ...(category && { category }), ...(limit && { limit }), ...(offset && { offset }) }),
    getById: (id: number) => 
      request.get(`/ai/articles/${id}`),
    favorite: (id: number) => 
      request.post(`/ai/articles/${id}/favorite`),
    unfavorite: (id: number) => 
      request.delete(`/ai/articles/${id}/favorite`),
    getFavorites: () => 
      request.get('/ai/articles/user/favorites')
  },

  user: {
    getProfile: () => 
      request.get('/ai/user/me'),
    updateProfile: (data: { nickname?: string; signature?: string; age_group?: string; avatar?: string }) => 
      request.put('/ai/user/profile', data),
    getStats: () => 
      request.get('/ai/user/stats')
  },

  crisis: {
    detect: (text: string) => 
      request.post('/ai/crisis/detect', { text }),
    getResources: () => 
      request.get('/ai/crisis/resources')
  },

  admin: {
    getDashboard: () => 
      request.get('/ai/admin/dashboard'),
    getStats: () => 
      request.get('/ai/admin/stats'),
    getUsers: (page?: number, pageSize?: number, search?: string) => 
      request.get('/ai/admin/users', { ...(page && { page }), ...(pageSize && { page_size: pageSize }), ...(search && { search }) }),
    getCrisisEvents: (status?: string, riskLevel?: string, page?: number, pageSize?: number) => 
      request.get('/ai/admin/crisis-events', { ...(status && { status }), ...(riskLevel && { risk_level: riskLevel }), ...(page && { page }), ...(pageSize && { page_size: pageSize }) }),
    handleCrisis: (eventId: number, notes?: string) => 
      request.put(`/ai/admin/crisis-events/${eventId}/handle`, { notes }),
    getOperationLogs: (userId?: string, action?: string, page?: number, pageSize?: number) => 
      request.get('/ai/admin/operation-logs', { ...(userId && { user_id: userId }), ...(action && { action }), ...(page && { page }), ...(pageSize && { page_size: pageSize }) }),
    getEmotionTrend: (days?: number) => 
      request.get('/ai/admin/emotion-trend', days ? { days } : {}),
    getAssessmentStats: (days?: number) => 
      request.get('/ai/admin/assessment-stats', days ? { days } : {}),
    exportUsers: () => 
      request.get('/ai/admin/export/users')
  },

  upload: {
    avatar: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return request.upload('/ai/upload/avatar', formData)
    },
    voice: (file: File, sessionId?: string) => {
      const formData = new FormData()
      formData.append('file', file)
      if (sessionId) formData.append('session_id', sessionId)
      return request.upload('/ai/upload/voice', formData)
    },
    deleteFile: (fileId: number) => 
      request.delete(`/ai/upload/${fileId}`)
  },

  diary: {
    create: (data: { title?: string; content: string; mood?: string; weather?: string }) => 
      request.post('/ai/diary', data),
    getList: (limit?: number, offset?: number) => 
      request.get('/ai/diary', { ...(limit && { limit }), ...(offset && { offset }) }),
    getById: (id: number) => 
      request.get(`/ai/diary/${id}`),
    update: (id: number, data: { title?: string; content?: string; mood?: string; weather?: string }) => 
      request.put(`/ai/diary/${id}`, data),
    delete: (id: number) => 
      request.delete(`/ai/diary/${id}`),
    getStats: (days?: number) => 
      request.get('/ai/diary/stats/summary', days ? { days } : {})
  }
}

export default request
