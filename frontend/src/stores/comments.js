import { ref } from 'vue'
import { defineStore } from 'pinia'

import { createComment, deleteComment, fetchComments } from '@/api/comments'

/**
 * 评论 store（按文章 slug 组织）。
 *
 * 后端契约（2026-09 起带分页）：
 *   GET /comments/{slug}?page=1&size=10
 *   data = { total_comment, total_comment_pages, root: [ {id, nickname, content, created_at, children:[]} ] }
 *   注意两点：
 *     1. 结构是 data.root，不再是直接数组
 *     2. 该文章评论数为 0 时后端返回 404（api/comments.js 已把它转成空列表）
 *
 * 评论没有审核状态字段；提交后立即对所有访客可见。
 */
export const useCommentStore = defineStore('comments', () => {
  /** 评论区默认一次取多少条顶级评论 */
  const PAGE_SIZE = 10

  const trees = ref({})
  const meta = ref({})

  const loading = ref(false)
  const loadingMore = ref(false)
  const submitting = ref(false)

  /** 提交成功后的提示文案，展示在表单下方 */
  const hint = ref('')

  function treeOf(slug) {
    return trees.value[slug] ?? []
  }

  function metaOf(slug) {
    return meta.value[slug] ?? { total: 0, totalPages: 0, page: 0 }
  }

  function normalizeNode(node) {
    return { ...node, children: (node.children ?? []).map(normalizeNode) }
  }

  /** 按 id 去重合并顶级评论（回复已随节点一起返回，整棵树替换） */
  function mergeRoots(current, incoming) {
    const seen = new Set(current.map((node) => node.id))
    return [...current, ...incoming.filter((node) => !seen.has(node.id))]
  }

  /**
   * 加载第一页评论
   * @param {string} slug
   * @param {{ force?: boolean }} [opts]
   */
  async function load(slug, { force = false } = {}) {
    if (!force && trees.value[slug]) return trees.value[slug]
    loading.value = true
    try {
      const { roots, total, totalPages } = await fetchComments(slug, { page: 1, size: PAGE_SIZE })
      trees.value[slug] = roots.map(normalizeNode)
      meta.value[slug] = { total, totalPages, page: 1 }
      return trees.value[slug]
    } finally {
      loading.value = false
    }
  }

  /** 是否还有下一页顶级评论 */
  function hasMore(slug) {
    const m = metaOf(slug)
    return m.totalPages > 0 && m.page < m.totalPages
  }

  /** 加载下一页顶级评论并追加 */
  async function loadMore(slug) {
    if (loadingMore.value || !hasMore(slug)) return treeOf(slug)
    loadingMore.value = true
    try {
      const next = metaOf(slug).page + 1
      const { roots, total, totalPages } = await fetchComments(slug, { page: next, size: PAGE_SIZE })
      trees.value[slug] = mergeRoots(treeOf(slug), roots.map(normalizeNode))
      meta.value[slug] = { total, totalPages, page: next }
      return trees.value[slug]
    } finally {
      loadingMore.value = false
    }
  }

  /**
   * 发表评论或回复
   * @param {string} slug 文章 slug
   * @param {{ nickname: string, email: string, content: string, parent_id?: number|null }} payload
   */
  async function submit(slug, payload) {
    submitting.value = true
    hint.value = ''
    try {
      const created = await createComment(slug, payload)
      const node = normalizeNode({
        ...created,
        nickname: created?.nickname ?? payload.nickname,
        content: created?.content ?? payload.content,
      })

      if (node.parent_id) {
        const attached = appendReply(treeOf(slug), node.parent_id, node)
        // 父评论不在当前页（被分页挡在后面）时，给出提示而不是让评论「凭空消失」
        if (!attached) {
          hint.value = '回复已提交，展开对应评论后可见'
          bumpTotal(slug)
          return node
        }
      } else {
        trees.value[slug] = [node, ...treeOf(slug)]
      }
      hint.value = node.parent_id ? '回复已提交' : '评论已提交'
      bumpTotal(slug)
      return node
    } finally {
      submitting.value = false
    }
  }

  function bumpTotal(slug) {
    const m = metaOf(slug)
    meta.value[slug] = { ...m, total: m.total + 1 }
  }

  /** 把新回复挂到对应父节点下 */
  function appendReply(nodes, parentId, node) {
    for (const item of nodes) {
      if (item.id === parentId) {
        item.children = [...(item.children ?? []), node]
        return true
      }
      if (item.children?.length && appendReply(item.children, parentId, node)) return true
    }
    return false
  }

  /**
   * 删除评论（管理端复用的能力）
   * 后端是物理删除，若被删的是回复，其子回复会因外键约束而失败，因此这里按实际结果处理。
   */
  async function remove(slug, id) {
    await deleteComment(slug, id)
    trees.value[slug] = removeNode(treeOf(slug), id)
    const m = metaOf(slug)
    meta.value[slug] = { ...m, total: Math.max(0, m.total - 1) }
  }

  function removeNode(nodes, id) {
    return nodes
      .filter((item) => item.id !== id)
      .map((item) => ({ ...item, children: removeNode(item.children ?? [], id) }))
  }

  return {
    PAGE_SIZE,
    trees,
    meta,
    loading,
    loadingMore,
    submitting,
    hint,
    treeOf,
    metaOf,
    hasMore,
    load,
    loadMore,
    submit,
    remove,
  }
})
