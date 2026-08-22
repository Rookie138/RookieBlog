import axios from 'axios'

export const TOKEN_KEY = 'manage_access_token'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
})

function extractErrorMessage(error) {
  const data = error.response?.data
  if (typeof data?.detail === 'string') return data.detail
  if (Array.isArray(data?.detail) && data.detail[0]?.msg) return data.detail[0].msg
  return data?.message || error.message || '请求失败'
}

request.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
    }
    return Promise.reject(new Error(extractErrorMessage(error)))
  },
)

export default request
