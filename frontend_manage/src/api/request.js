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

function redirectToLogin() {
  const base = import.meta.env.BASE_URL || '/'
  // 已在登录页时不重复跳转（如登录失败 401），错误由页面自身展示
  if (window.location.pathname.startsWith(`${base}login`)) return
  const redirect = encodeURIComponent(window.location.pathname + window.location.search)
  window.location.replace(`${base}login?redirect=${redirect}`)
}

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      redirectToLogin()
    }
    return Promise.reject(new Error(extractErrorMessage(error)))
  },
)

export default request
