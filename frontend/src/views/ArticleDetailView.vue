<template>
  <div class="view">
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="article">
      <h1>{{ article.title }}</h1>
      <p v-if="publishedDate" class="meta">{{ publishedDate }}</p>
      <p v-if="article.summary" class="muted">{{ article.summary }}</p>
      <div class="markdown-body" v-html="html"></div>
      <RouterLink :to="{ name: 'articles' }">返回文章列表</RouterLink>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchArticleDetail } from '@/api/articles'
import { renderMarkdown } from '@/utils/markdown'
import { SITE_NAME } from '@/config'

const route = useRoute()
const article = ref(null)
const loading = ref(true)
const error = ref('')

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const html = computed(() => renderMarkdown(article.value?.context || ''))
const publishedDate = computed(() => formatDate(article.value?.created_at))

async function load(slug) {
  loading.value = true
  error.value = ''
  article.value = null
  try {
    const data = await fetchArticleDetail(slug)
    if (!data.article) {
      error.value = '文章不存在或尚未发布'
      return
    }
    article.value = data.article
    document.title = `${data.article.title} · ${SITE_NAME}`
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
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
  margin: -0.4rem 0 1rem;
  color: #8a8a8a;
  font-size: 0.88rem;
}

.markdown-body {
  margin: 1.5rem 0 2rem;
}
</style>
