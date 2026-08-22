export function parseJwtPayload(token) {
  if (!token || typeof token !== 'string') return null
  const parts = token.split('.')
  if (parts.length < 2) return null
  try {
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4)
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

export function userFromAccessToken(accessToken) {
  const payload = parseJwtPayload(accessToken)
  if (!payload?.sub) return null
  return {
    id: Number(payload.sub),
    username: payload.name ?? '',
  }
}

export function isTokenExpired(accessToken) {
  const payload = parseJwtPayload(accessToken)
  if (!payload?.exp) return false
  return Date.now() >= payload.exp * 1000
}
