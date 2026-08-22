import request, { TOKEN_KEY } from './request'
import { isTokenExpired, userFromAccessToken } from '@/utils/jwt'

export async function loginApi(credentials) {
  const body = new URLSearchParams()
  body.append('username', credentials.username.trim())
  body.append('password', credentials.password)

  const data = await request.post('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  const token = data.access_token
  if (!token) {
    throw new Error('登录响应缺少 access_token')
  }

  return {
    token,
    user: userFromAccessToken(token),
  }
}

export function readStoredUser() {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token || isTokenExpired(token)) return null
  return userFromAccessToken(token)
}
