import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000,
})

// Auto-attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('certmind_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-redirect to login on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('certmind_token')
      // Only redirect if not already on login page
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (body) => api.post('/auth/register', body).then(r => r.data),
  login: (body) => api.post('/auth/login', body).then(r => r.data),
  me: () => api.get('/auth/me').then(r => r.data),
  updateProfile: (body) => api.put('/auth/profile', body).then(r => r.data),
}

export const certAPI = {
  list: () => api.get('/rag/certifications').then(r => r.data),
}

export const questionsAPI = {
  list: (params) => api.get('/questions/', { params }).then(r => r.data),
  topics: (certId) => api.get('/questions/topics', { params: { cert_id: certId } }).then(r => r.data),
  wrong: (certId) => api.get('/questions/wrong', { params: { cert_id: certId } }).then(r => r.data),
}

export const examAPI = {
  start: (body) => api.post('/exam/start', body).then(r => r.data),
  answer: (sessionId, body) => api.post(`/exam/${sessionId}/answer`, body).then(r => r.data),
  finish: (sessionId, timeTakenS) => api.post(`/exam/${sessionId}/finish`, null, { params: { time_taken_s: timeTakenS } }).then(r => r.data),
  replay: (sessionId) => api.get(`/exam/${sessionId}/replay`).then(r => r.data),
  sessions: (certId) => api.get('/exam/sessions', { params: { cert_id: certId } }).then(r => r.data),
}

export const analyticsAPI = {
  overview: (certId) => api.get('/analytics/overview', { params: { cert_id: certId } }).then(r => r.data),
  topics: (certId) => api.get('/analytics/topics', { params: { cert_id: certId } }).then(r => r.data),
  history: (certId) => api.get('/analytics/history', { params: { cert_id: certId } }).then(r => r.data),
  trend: (certId) => api.get('/analytics/accuracy-trend', { params: { cert_id: certId } }).then(r => r.data),
  confidence: (certId) => api.get('/analytics/confidence', { params: { cert_id: certId } }).then(r => r.data),
  recommendations: (certId) => api.get('/analytics/recommendations', { params: { cert_id: certId } }).then(r => r.data),
  streak: (certId) => api.get('/analytics/streak', { params: { cert_id: certId } }).then(r => r.data),
}

export const ragAPI = {
  explain: (body) => api.post('/rag/explain', body).then(r => r.data),
  learn: (body) => api.post('/rag/learn', body).then(r => r.data),
  generate: (body) => api.post('/rag/generate', body).then(r => r.data),
  tutor: (body) => api.post('/rag/tutor', body).then(r => r.data),
  uploadKnowledge: (file, certId) => {
    const form = new FormData()
    form.append('file', file)
    if (certId) form.append('cert_id', certId)
    return api.post('/rag/knowledge/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
  },
  knowledgeSources: () => api.get('/rag/knowledge/sources').then(r => r.data),
  evaluate: (body) => api.post('/rag/evaluate', body).then(r => r.data),
  experiment: (body) => api.post('/rag/experiment', body).then(r => r.data),
  runPrompt: (body) => api.post('/rag/run-prompt', body).then(r => r.data),
  compareModels: (body) => api.post('/rag/compare-models', body).then(r => r.data),
  runs: (limit = 50) => api.get('/rag/runs', { params: { limit } }).then(r => r.data),
  observability: () => api.get('/rag/observability').then(r => r.data),
}

export const dumpsAPI = {
  upload: (file, certId) => {
    const form = new FormData()
    form.append('file', file)
    form.append('cert_id', certId)
    return api.post('/dumps/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  process: (bankId) => api.post(`/dumps/${bankId}/process`).then(r => r.data),
  status: (bankId) => api.get(`/dumps/${bankId}/status`).then(r => r.data),
  list: (certId) => api.get('/dumps/', { params: { cert_id: certId } }).then(r => r.data),
  save: (bankId) => api.put(`/dumps/${bankId}/save`).then(r => r.data),
  delete: (bankId) => api.delete(`/dumps/${bankId}`).then(r => r.data),
}

export default api

