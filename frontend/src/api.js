import axios from 'axios'

const API_BASE = 'http://localhost:8002'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Persona API
export const personaAPI = {
  create: (data) => api.post('/persona/', data),
  get: (userId) => api.get(`/persona/${userId}`),
  update: (userId, data) => api.put(`/persona/${userId}`, data),
  delete: (userId) => api.delete(`/persona/${userId}`),
  list: () => api.get('/persona/'),

  // KakaoTalk file parsing
  parseKakao: (file, myName = '나', maxExamples = 50) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('my_name', myName)
    formData.append('max_examples', maxExamples)
    return axios.post(`${API_BASE}/persona/parse-kakao`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Create persona directly from KakaoTalk file
  createFromKakao: (file, userId, name, myName = '나', maxExamples = 50) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId)
    formData.append('name', name)
    formData.append('my_name', myName)
    formData.append('max_examples', maxExamples)
    return axios.post(`${API_BASE}/persona/create-from-kakao`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// Auto Mode API
export const autoAPI = {
  respond: (data) => api.post('/auto/respond', data),
}

// Assist Mode API
export const assistAPI = {
  suggest: (data) => api.post('/assist/suggest', data),
  quickReply: (userId, situationType, relationship) =>
    api.post(`/assist/quick-reply?user_id=${userId}&situation_type=${situationType}&recipient_relationship=${relationship}`),
}

// Alibi Mode API
export const alibiAPI = {
  announce: (data) => api.post('/alibi/announce', data),
  generateImage: (data) => api.post('/alibi/image', data),
  quickAnnounce: (userId, announcement, groups) => {
    const params = new URLSearchParams({ user_id: userId, announcement })
    if (groups) groups.forEach(g => params.append('include_groups', g))
    return api.post(`/alibi/quick-announce?${params}`)
  },
}

// Chat History API
export const historyAPI = {
  get: (userId, limit = 20, offset = 0) =>
    api.get(`/history/${userId}?limit=${limit}&offset=${offset}`),
  getStats: (userId) => api.get(`/history/${userId}/stats`),
  clear: (userId) => api.delete(`/history/${userId}`),
  deleteMessage: (messageId) => api.delete(`/history/message/${messageId}`),
}

export default api
