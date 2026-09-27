<template>
  <div class="view">
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <template v-else-if="article">
      <h1>{{ article.title }}</h1>

      <p class="meta">
        <span v-if="publishedDate">{{ publishedDate }}</span>
        <span v-if="article.view_count != null">· 阅读 {{ article.view_count }}</span>
        <span v-if="commentTotal != null">· 评论 {{ commentTotal }}</span>
      </p>

      <p v-if="article.summary" class="summary">{{ article.summary }}</p>

      <div class="markdown-body" v-html="html"></div>

      <RouterLink :to="{ name: 'articles' }">← 返回文章列表</RouterLink>

      <CommentSection ref="commentSectionRef" :slug="article.slug" />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import CommentSection from '@/components/CommentSection.vue'
import { SITE_NAME } from '@/config'
import { useArticleStore } from '@/stores/articles'
import { useCommentStore } from '@/stores/comments'
import { formatDate } from '@/utils/format'
import { renderMarkdown } from '@/utils/markdown'

const route = useRoute()
const articleStore = useArticleStore()
const commentStore = useCommentStore()

const error = ref('')
const commentSectionRef = ref(null)

const article = computed(() => articleStore.detail)
const loading = computed(() => articleStore.loadingDetail)
const html = computed(() => renderMarkdown(article.value?.context || ''))
const publishedDate = computed(() => formatDate(article.value?.created_at))
/** 评论总数用评论接口返回的 total_comment（文章表里的 comment_count 只在发表时 +1，删除不 -1，不准） */
const commentTotal = computed(() => commentStore.metaOf(route.params.slug).total)

async function load(slug) {
  error.value = ''
  try {
    const data = await articleStore.loadDetail(slug, { force: true })
    if (!data) {
      error.value = '文章不存在或尚未发布'
      return
    }
    document.title = `${data.title} · ${SITE_NAME}`
    // 评论数由评论区加载后统计：
    // 文章表里的 comment_count 只在发表评论时 +1，删除评论时不会 -1，并不可靠，所以不直接用它
    commentSectionRef.value?.load()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(() => load(route.params.slug))

watch(
  () => route.params.slug,
  (slug) => {
    if (slug) load(slug)
  },
)
</script>

<style scoped>
.error {
  color: #b91c1c;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: -0.4rem 0 1rem;
  color: #8a8a8a;
  font-size: 0.88rem;
}

.summary {
  margin: 0 0 1.5rem;
  padding: 0.75rem 1rem;
  background: #f1efe9;
  border-radius: 8px;
  color: #5c5c5c;
}

.markdown-body {
  margin: 1.5rem 0 2rem;
}
</style>
