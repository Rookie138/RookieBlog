import request, { TOKEN_KEY } from './request'
import { isTokenExpired, userFromAccessToken } from '@/utils/jwt'

// 后端当前登录端点（OAuth2 表单提交）。后端若改回 /auth/login，只改这一行即可。
export const LOGIN_ENDPOINT = '/auth/token'

// 兼容两种响应形态：
//   扁平：{ access_token, token_type }
//   嵌套：{ user_info: {...}, token: { access_token, token_type } }
function pickToken(data) {
  return data?.token?.access_token || data?.access_token || ''
}

function pickUser(data, token) {
  if (data?.user_info) {
    return {
      id: data.user_info.id,
      username: data.user_info.username,
      name: data.user_info.name ?? data.user_info.username ?? '',
    }
  }
  return userFromAccessToken(token)
}

export async function loginApi(credentials) {
  const body = new URLSearchParams()
  body.append('username', credentials.username.trim())
  body.append('password', credentials.password)

  const data = await request.post(LOGIN_ENDPOINT, body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  const token = pickToken(data)
  if (!token) {
    throw new Error('登录响应缺少 access_token')
  }

  return {
    token,
    user: pickUser(data, token),
  }
}

export function readStoredUser() {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token || isTokenExpired(token)) return null
  return userFromAccessToken(token)
}
