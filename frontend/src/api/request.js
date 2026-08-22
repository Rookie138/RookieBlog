import axios from 'axios'

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

request.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(new Error(extractErrorMessage(error))),
)

export default request
