<template>
  <div class="view">
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="article">
      <h1>{{ article.title }}</h1>
      <p class="muted">{{ article.summary }}</p>
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

const route = useRoute()
const article = ref(null)
const loading = ref(true)
const error = ref('')

const html = computed(() => renderMarkdown(article.value?.context || ''))

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
    document.title = `${data.article.title} · 学习笔记`
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

.markdown-body {
  margin: 1.5rem 0 2rem;
}
</style>
