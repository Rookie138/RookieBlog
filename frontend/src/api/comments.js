import request from './request'

/**
 * 前台评论接口：后端 router prefix = /comments
 *
 * 后端契约（2026-09 起，带分页）：
 *   GET  /comments/{slug}?page=1&size=10
 *        data = { total_comment, total_comment_pages, root: [评论树节点...] }
 *        节点：{ id, article_id, parent_id, nickname, content, created_at, children: [] }
 *        注意：不返回 email（后端已剔除）
 *        ⚠ 该文章评论数为 0 时，后端会返回 404（因为 total_comment_pages=0，page=1 > 0），
 *          前端必须把这种情况当成「没有评论」而不是报错
 *   POST /comments/{slug}
 *        请求体 { parent_id, nickname, email, content }（邮箱必填）
 *        data = CommentOutSchema（不含 email）
 *   DELETE /comments/manage/{slug}/{id}  需要登录（管理端使用）
 */

/** 后端总页数可能是浮点数，归一成整数 */
export function normalizeTotalPages(totalPages, total, size) {
  const pages = Number(totalPages)
  if (Number.isFinite(pages) && pages > 0) return Math.ceil(pages)
  const t = Number(total)
  if (Number.isFinite(t) && t > 0 && size > 0) return Math.ceil(t / size)
  return 0
}

/** 从评论响应里取出顶级评论数组，兼容新版 {root} 与旧版直接数组 */
export function pickCommentRoots(payload) {
  if (Array.isArray(payload)) return payload
  return payload?.root ?? payload?.roots ?? payload?.comments ?? []
}

/** 判断是否「文章没有评论」导致的 404（后端在 total_comment_pages=0 时的行为） */
export function isNoCommentError(error) {
  return error?.status === 404 || error?.code === 40401
}

/**
 * 获取某篇文章的评论（分页返回顶级评论，children 里含各自回复）
 * 文章没有任何评论时返回空列表，而不是抛错
 * @param {string} slug
 * @param {{ page?: number, size?: number }} [params] page 从 1 开始
 * @returns {Promise<{ roots: Array, total: number, totalPages: number }>}
 */
export async function fetchComments(slug, params = {}) {
  const page = params.page ?? 1
  const size = params.size ?? 10
  try {
    const data = await request.get(`/comments/${encodeURIComponent(slug)}`, {
      params: { page, size },
    })
    return {
      roots: pickCommentRoots(data),
      total: Number(data?.total_comment ?? 0),
      totalPages: normalizeTotalPages(data?.total_comment_pages, data?.total_comment, size),
    }
  } catch (error) {
    // 该文章还没有评论：后端用 404 表达，这里视为空列表
    if (isNoCommentError(error)) {
      return { roots: [], total: 0, totalPages: 0 }
    }
    throw error
  }
}

/**
 * 发表评论
 * @param {string} slug
 * @param {{ nickname: string, email: string, content: string, parent_id?: number|null }} payload
 */
export function createComment(slug, payload) {
  return request.post(`/comments/${encodeURIComponent(slug)}`, {
    parent_id: payload.parent_id ?? null,
    nickname: payload.nickname,
    email: payload.email,
    content: payload.content,
  })
}

/**
 * 删除评论（管理端）
 * @param {string} slug 评论所属文章的 slug（后端要求，但并未用它做归属校验）
 * @param {number} id 评论 id
 */
export function deleteComment(slug, id) {
  return request.delete(`/comments/manage/${encodeURIComponent(slug)}/${id}`)
}

/** 统计评论树里的评论总数（含各层回复） */
export function countComments(nodes) {
  if (!Array.isArray(nodes)) return 0
  return nodes.reduce((sum, node) => sum + 1 + countComments(node.children), 0)
}
