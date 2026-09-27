import request from './request'

/**
 * 前台文章接口：后端 router prefix = /common-articles
 * 返回体形如 {"code":0,"message":"...","data":...}，信封已在 request.js 里拆掉。
 *
 * 后端分页契约（2026-09 起）：
 *   GET /common-articles/articles?page=1&size=10
 *   data = { total, total_pages, articles: [...] }
 *   - page 从 1 开始；total_pages 后端返回的是浮点数（total/size），前端需要自己取整
 *   - total 统计的是「全表」条数（含草稿），articles 只含已发布，所以 total 仅供粗略参考
 */

/** 把后端可能返回浮点数的 total_pages 归一成整数，并按 total/size 兜底 */
export function normalizeTotalPages(totalPages, total, size) {
  const pages = Number(totalPages)
  if (Number.isFinite(pages) && pages > 0) return Math.ceil(pages)
  const t = Number(total)
  if (Number.isFinite(t) && t > 0 && size > 0) return Math.ceil(t / size)
  return 0
}

/** 从列表响应里取出文章数组，兼容带信封/裸数组/键名变化 */
export function pickArticleList(payload) {
  if (Array.isArray(payload)) return payload
  return payload?.articles ?? payload?.items ?? []
}

/**
 * 获取已发布文章列表
 * @param {{ page?: number, size?: number }} [params] page 从 1 开始
 */
export function fetchArticles(params = {}) {
  const query = { page: params.page ?? 1 }
  if (params.size) query.size = params.size
  return request.get('/common-articles/articles', { params: query })
}

/**
 * 获取文章详情（后端会顺带把 view_count +1）
 * @param {string} slug
 */
export function fetchArticleDetail(slug) {
  return request.get(`/common-articles/articles/${encodeURIComponent(slug)}`)
}

/** 从详情响应里取出文章对象，兼容 {article:{...}} 与 {...} 两种返回结构 */
export function pickArticle(payload) {
  if (!payload) return null
  return payload.article ?? payload
}

/** 是否属于「页码越界」类错误（后端对超范围页码返回 404 + 40401） */
export function isPageNotFoundError(error) {
  return error?.status === 404 || error?.code === 40401
}
