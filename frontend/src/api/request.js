import axios from 'axios'

/**
 * 后端统一响应格式：{ code, message, data }
 * 但后端目前并非所有接口都遵循（详见 backend/docs/04-后端改造需求-评论与统一响应.md）：
 *   - 文章/评论接口：{"code":0,"message":"success","data":...}
 *   - 登录接口：{"access_token":"...","token_type":"bearer"}（OAuth2 裸格式）
 *   - 由 HTTPException 抛出的错误：{"detail":"..."}
 * 因此这里同时兼容「带信封」和「裸数据」两种成功响应。
 */

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
})

/** 带业务码的请求错误，方便调用方按 code 分支处理 */
export class ApiError extends Error {
  constructor(message, { code = -1, status = 0, data = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.data = data
  }

  /** 是否为请求频率过高（后端后续加防刷后会返回 429） */
  get isRateLimited() {
    return this.status === 429 || String(this.code).startsWith('429')
  }

  /** 限流时需要等待的秒数（后端在 data.retry_after 里给出），拿不到返回 null */
  get retryAfter() {
    const value = this.data?.retry_after
    return typeof value === 'number' ? value : null
  }
}

function extractErrorMessage(error) {
  const data = error.response?.data
  if (typeof data?.message === 'string' && data.message) return data.message
  if (typeof data?.detail === 'string') return data.detail
  if (Array.isArray(data?.detail) && data.detail[0]?.msg) return data.detail[0].msg
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') return '请求超时，请稍后重试'
  return error.message || '请求失败'
}

request.interceptors.response.use(
  (response) => {
    const body = response.data
    // 带信封：{ code, message, data }
    if (body !== null && typeof body === 'object' && !Array.isArray(body) && 'code' in body) {
      if (body.code !== 0) {
        throw new ApiError(body.message || '请求失败', {
          code: body.code,
          status: response.status,
          data: body.data,
        })
      }
      return body.data
    }
    // 裸格式（如登录接口）
    return body
  },
  (error) => {
    if (error instanceof ApiError) return Promise.reject(error)
    return Promise.reject(
      new ApiError(extractErrorMessage(error), {
        code: error.response?.data?.code ?? -1,
        status: error.response?.status ?? 0,
        data: error.response?.data?.data ?? error.response?.data ?? null,
      }),
    )
  },
)

export default request
