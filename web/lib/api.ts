import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  me: () => api.get('/api/auth/me'),
}

export const eventsApi = {
  list: (params?: any) => api.get('/api/events/', { params }),
  get: (id: number) => api.get(`/api/events/${id}`),
  update: (id: number, data: any) => api.put(`/api/events/${id}`, data),
  delete: (id: number) => api.delete(`/api/events/${id}`),
  publish: (id: number) => api.post(`/api/events/${id}/publish`),
  getCities: () => api.get('/api/events/cities/list'),
  getCategories: () => api.get('/api/events/categories/list'),
  bulkPublish: (eventIds: number[]) => api.post('/api/events/bulk/publish', { event_ids: eventIds }),
  bulkDelete: (eventIds: number[]) => api.post('/api/events/bulk/delete', { event_ids: eventIds }),
}

export const tasksApi = {
  list: (params?: any) => api.get('/api/tasks/', { params }),
  get: (id: number) => api.get(`/api/tasks/${id}`),
  extract: (urls: string[]) => api.post('/api/tasks/extract', { urls }),
}

export const statsApi = {
  get: () => api.get('/api/stats/'),
}

export default api
