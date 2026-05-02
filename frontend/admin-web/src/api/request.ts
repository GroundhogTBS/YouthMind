const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9000'

const getToken = (): string => {
  return localStorage.getItem('admin_token') || ''
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  headers?: Record<string, string>
}

async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', data, headers = {} } = options
  
  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  headers['Content-Type'] = 'application/json'

  const response = await fetch(`${BASE_URL}${url}`, {
    method,
    headers,
    body: method !== 'GET' && data ? JSON.stringify(data) : undefined,
  })

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export const api = {
  admin: {
    getDashboard: () => request('/ai/admin/dashboard'),
    getStats: () => request('/ai/admin/stats'),
    getUsers: (page = 1, pageSize = 20, search = '') => 
      request(`/ai/admin/users?page=${page}&page_size=${pageSize}&search=${search}`),
    getCrisisEvents: (status = '', riskLevel = '', page = 1, pageSize = 20) => 
      request(`/ai/admin/crisis-events?status=${status}&risk_level=${riskLevel}&page=${page}&page_size=${pageSize}`),
    handleCrisis: (eventId: number, notes?: string) => 
      request(`/ai/admin/crisis-events/${eventId}/handle`, { method: 'PUT', data: { notes } }),
    getOperationLogs: (userId = '', action = '', page = 1, pageSize = 50) => 
      request(`/ai/admin/operation-logs?user_id=${userId}&action=${action}&page=${page}&page_size=${pageSize}`),
    getEmotionTrend: (days = 7) => request(`/ai/admin/emotion-trend?days=${days}`),
    getAssessmentStats: (days = 30) => request(`/ai/admin/assessment-stats?days=${days}`),
    exportUsers: () => request('/ai/admin/export/users'),
  },
  
  auth: {
    login: (phone: string, password: string) => 
      request('/ai/user/login', { method: 'POST', data: { phone, password } }),
    logout: () => request('/ai/user/logout', { method: 'POST' }),
    getMe: () => request('/ai/user/me'),
  }
}

export default api
