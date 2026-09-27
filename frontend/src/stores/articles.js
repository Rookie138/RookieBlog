import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  fetchArticleDetail,
  fetchArticles,
  normalizeTotalPages,
  pickArticle,
  pickArticleList,
} from '@/api/articles'

/**
 * 文章 store：集中管理文章列表与详情，避免首页/列表页/详情页各拉一次且状态互相看不见。
 * 采用 setup 语法（与 frontend_manage 的 stores/user.js 保持一致）。
 *
 * 后端分页契约：GET /common-articles/articles?page=1&size=10
 *   data = { total, total_pages, articles }
 *   - page 从 1 开始
 *   - 后端 total_pages 是浮点数，这里用 normalizeTotalPages 取整
 *   - 首页只取前 5 篇，所以默认一次拉 SIZE 篇即可；列表页需要更多时用 loadMore()
 */
export const useArticleStore = defineStore('articles', () => {
  /** 列表页每页条数（也是首次请求的 size） */
  const PAGE_SIZE = 10

  const list = ref([])
  const listLoaded = ref(false)
  const loadingList = ref(false)
  const loadingMore = ref(false)
  const listError = ref('')

  const page = ref(0)
  const totalPages = ref(0)
  const total = ref(0)

  const detail = ref(null)
  const loadingDetail = ref(false)

  /** 本地搜索结果（后端暂未提供搜索接口，先在前端过滤标题与摘要） */
  function search(keyword) {
    const q = String(keyword || '').trim().toLowerCase()
    if (!q) return list.value
    return list.value.filter((item) => {
      return (
        item.title?.toLowerCase().includes(q) || item.summary?.toLowerCase().includes(q)
      )
    })
  }

  /** 合并新一页文章，按 slug 去重，避免后端数据变动时出现重复项 */
  function mergeArticles(items) {
    const seen = new Set(list.value.map((item) => item.slug))
    const fresh = items.filter((item) => item?.slug && !seen.has(item.slug))
    list.value = [...list.value, ...fresh]
  }

  async function fetchPage(nextPage, { append }) {
    const data = await fetchArticles({ page: nextPage, size: PAGE_SIZE })
    const items = pickArticleList(data)
    if (append) mergeArticles(items)
    else list.value = items

    page.value = nextPage
    total.value = Number(data?.total ?? 0)
    totalPages.value = normalizeTotalPages(data?.total_pages, data?.total, PAGE_SIZE)
    return items
  }

  /**
   * 加载第一页
   * @param {{ force?: boolean }} [opts] force=true 时忽略缓存重新请求
   */
  async function loadList({ force = false } = {}) {
    if (listLoaded.value && !force) return list.value
    loadingList.value = true
    listError.value = ''
    try {
      await fetchPage(1, { append: false })
      listLoaded.value = true
      return list.value
    } catch (error) {
      // 这里不向外抛：页面只需要展示 listError，避免每个视图都写 try/catch
      listError.value = error.message || '文章加载失败'
      return list.value
    } finally {
      loadingList.value = false
    }
  }

  /** 是否还有下一页 */
  const hasMore = computed(() => {
    if (!totalPages.value) return false
    return page.value < totalPages.value
  })

  /** 加载下一页并追加（列表页「加载更多」用） */
  async function loadMore() {
    if (loadingMore.value || !hasMore.value) return list.value
    loadingMore.value = true
    listError.value = ''
    try {
      await fetchPage(page.value + 1, { append: true })
      return list.value
    } catch (error) {
      listError.value = error.message || '加载更多失败'
      return list.value
    } finally {
      loadingMore.value = false
    }
  }

  /**
   * 加载文章详情
   * @param {string} slug
   * @param {{ force?: boolean }} [opts]
   */
  async function loadDetail(slug, { force = false } = {}) {
    if (!force && detail.value?.slug === slug) return detail.value
    loadingDetail.value = true
    detail.value = null
    try {
      const data = await fetchArticleDetail(slug)
      detail.value = pickArticle(data)
      return detail.value
    } finally {
      loadingDetail.value = false
    }
  }

  const latest = computed(() => list.value.slice(0, 5))

  return {
    list,
    listLoaded,
    loadingList,
    loadingMore,
    listError,
    page,
    totalPages,
    total,
    hasMore,
    detail,
    loadingDetail,
    latest,
    search,
    loadList,
    loadMore,
    loadDetail,
  }
})
