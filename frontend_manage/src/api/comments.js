import request from './request'

/**
 * 管理端评论接口（后端 prefix = /comments，与前台共用）
 *   GET    /comments/{slug}?page=1&size=10
 *          data = { total_comment, total_comment_pages, root: [...] }
 *          ⚠ 该文章没有评论时后端返回 404（total_comment_pages=0），要当成「空」处理
 *   DELETE /comments/manage/{slug}/{id}     删除评论（需登录）
 *
 * 后端目前没有「跨文章评论列表」接口，也没有评论审核状态，
 * 所以管理端只能逐篇文章拉取后在前端汇总，详见 stores/comments.js。
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

/** 取一页评论；文章没有评论时返回空列表而不是抛错 */
export async function fetchCommentPage(slug, { page = 1, size = 50 } = {}) {
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
    if (error?.status === 404 || error?.code === 40401) {
      return { roots: [], total: 0, totalPages: 0 }
    }
    throw error
  }
}

/**
 * 拉取某篇文章的全部评论（自动翻页）。
 * 后端按「顶级评论」分页，这里把每页的 root 合并后返回，供管理端汇总。
 */
export async function fetchAllComments(slug, { size = 50, maxPages = 20 } = {}) {
  const first = await fetchCommentPage(slug, { page: 1, size })
  const roots = [...first.roots]
  const pages = Math.min(first.totalPages, maxPages)

  for (let page = 2; page <= pages; page++) {
    const next = await fetchCommentPage(slug, { page, size })
    const seen = new Set(roots.map((node) => node.id))
    roots.push(...next.roots.filter((node) => !seen.has(node.id)))
  }

  return { roots, total: first.total }
}

export function deleteComment(slug, id) {
  return request.delete(`/comments/manage/${encodeURIComponent(slug)}/${id}`)
}
