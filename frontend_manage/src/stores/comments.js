import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { deleteComment, fetchAllComments } from '@/api/comments'
import { fetchManageArticles } from '@/api/articles'

/**
 * 管理端评论 store。
 *
 * 后端限制（导致这里必须「曲线救国」）：
 *   1. 没有「跨文章查询评论」的管理接口，只有 GET /comments/{slug}（按文章取评论树）
 *   2. 评论接口按「顶级评论」分页（默认 10 条/页），所以这里用 fetchAllComments 自动翻页
 *   3. 评论树接口不返回 email（邮箱只在库里，管理端接口尚未提供）
 *   4. DELETE /comments/manage/{slug}/{id} 需要 slug 参数，所以每条评论都要带上所属文章
 *
 * 做法：先取文章列表，再按文章并发拉取评论树，最后展平成一张全局评论表。
 * 文章多了以后这里会变成 N+1 请求；后端补一个管理端评论列表接口后应改成一次请求。
 */
export const useCommentStore = defineStore('manage-comments', () => {
  /** 同时并发的评论请求数（避免一次性把后端打满 / 触发限流） */
  const CONCURRENCY = 3

  /** 展平后的评论列表，按时间倒序 */
  const comments = ref([])
  /** slug -> 文章 { slug, title }，用于渲染「评论的是哪篇文章」 */
  const articleMap = ref({})

  const loading = ref(false)
  const loaded = ref(false)
  const error = ref('')

  /** 每个 slug 的评论总数（含回复） */
  const countByArticle = computed(() => {
    const result = {}
    for (const item of comments.value) {
      result[item.articleSlug] = (result[item.articleSlug] ?? 0) + 1
    }
    return result
  })

  const total = computed(() => comments.value.length)

  function flatten(nodes, article, out) {
    for (const node of nodes) {
      out.push({
        ...node,
        articleSlug: article.slug,
        articleTitle: article.title,
      })
      if (node.children?.length) flatten(node.children, article, out)
    }
  }

  /** 按 CONCURRENCY 分批并发执行，避免几十篇文章同时打后端 */
  async function mapWithLimit(items, limit, worker) {
    const results = []
    for (let i = 0; i < items.length; i += limit) {
      const batch = items.slice(i, i + limit)
      const settled = await Promise.allSettled(batch.map(worker))
      results.push(...settled)
    }
    return results
  }

  /**
   * 加载全部文章的评论
   * @param {{ force?: boolean }} [opts]
   */
  async function load({ force = false } = {}) {
    if (loaded.value && !force) return comments.value
    loading.value = true
    error.value = ''
    try {
      const raw = await fetchManageArticles()
      const articles = Array.isArray(raw) ? raw : raw?.data ?? raw?.items ?? []
      const map = {}
      for (const item of articles) {
        map[item.slug] = { slug: item.slug, title: item.title }
      }
      articleMap.value = map

      const results = await mapWithLimit(articles, CONCURRENCY, async (item) => {
        const { roots } = await fetchAllComments(item.slug)
        return { article: item, roots }
      })

      const out = []
      const failed = []
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          flatten(result.value.roots, result.value.article, out)
        } else {
          failed.push(articles[index].title)
        }
      })

      out.sort((a, b) => new Date(b.created_at ?? 0) - new Date(a.created_at ?? 0))
      comments.value = out
      loaded.value = true

      if (failed.length) {
        error.value = `以下文章的评论加载失败：${failed.join('、')}`
      }
      return comments.value
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  /** 收集某条评论及其全部下级 id（后端删除父评论时子回复会因外键失败，所以要先删子再删父） */
  function descendantsOf(slug, id) {
    const ids = [id]
    let frontier = [id]
    while (frontier.length) {
      const next = comments.value
        .filter((item) => item.articleSlug === slug && frontier.includes(item.parent_id))
        .map((item) => item.id)
      if (!next.length) break
      ids.push(...next)
      frontier = next
    }
    return ids
  }

  /**
   * 删除评论
   * @param {{ id: number, articleSlug: string }} comment
   * @param {{ withReplies?: boolean }} [opts] withReplies=true（默认）时连带删除其下所有回复
   */
  async function remove(comment, { withReplies = true } = {}) {
    const ids = withReplies ? descendantsOf(comment.articleSlug, comment.id) : [comment.id]
    for (const id of ids) {
      await deleteComment(comment.articleSlug, id)
    }
    comments.value = comments.value.filter((item) => !ids.includes(item.id))
  }

  return {
    comments,
    articleMap,
    loading,
    loaded,
    error,
    countByArticle,
    total,
    load,
    remove,
  }
})
