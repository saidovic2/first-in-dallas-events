import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_CMS_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface EventSubmissionData {
  title: string
  primary_url?: string
  format: 'in-person' | 'online' | 'hybrid'
  country: string
  venue?: string
  address?: string
  city?: string
  state?: string
  zip_code?: string
  start_date: string
  end_date?: string
  price?: number
  price_tier: 'free' | 'paid'
  image_url?: string
  description?: string
  organizer_contact?: string
  submission_type: 'free' | 'paid'
  organizer_id: string
  organizer_email: string
}

export const submissionsApi = {
  create: (data: EventSubmissionData) => 
    api.post('/submissions', data),
  
  getByOrganizer: (organizerId: string) =>
    api.get(`/submissions/by-organizer/${organizerId}`),
  
  getById: (id: string) =>
    api.get(`/submissions/${id}`),
}

export const eventsApi = {
  list: (params?: any) => api.get('/events/', { params }),
  getCities: () => api.get('/events/cities/list'),
}

export default api
