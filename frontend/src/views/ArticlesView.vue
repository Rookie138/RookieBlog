<template>
  <div class="view">
    <h1>文章</h1>

    <label class="search">
      <span class="sr-only">搜索文章</span>
      <input v-model.trim="keyword" type="search" placeholder="搜索标题或摘要" />
    </label>

    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="filtered.length === 0" class="muted">没有找到相关文章。</p>
    <ul v-else class="article-list">
      <li v-for="item in filtered" :key="item.slug" class="article-item">
        <h3>
          <RouterLink :to="{ name: 'article-detail', params: { slug: item.slug } }">
            {{ item.title }}
          </RouterLink>
        </h3>
        <p>{{ item.summary }}</p>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchArticles } from '@/api/articles'

const articles = ref([])
const keyword = ref('')
const loading = ref(true)
const error = ref('')

const filtered = computed(() => {
  const q = keyword.value.toLowerCase()
  if (!q) return articles.value
  return articles.value.filter((item) => {
    return (
      item.title?.toLowerCase().includes(q) || item.summary?.toLowerCase().includes(q)
    )
  })
})

onMounted(async () => {
  try {
    const data = await fetchArticles()
    articles.value = data.articles || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.search {
  display: block;
  margin: 0 0 1.25rem;
}

.search input {
  width: 100%;
  padding: 0.55rem 0.8rem;
  border: 1px solid #e4e2dc;
  border-radius: 8px;
  background: #fff;
}

.article-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.article-item {
  padding: 1rem 0;
  border-bottom: 1px solid #e4e2dc;
}

.article-item h3 {
  margin: 0 0 0.35rem;
  font-size: 1.1rem;
}

.article-item h3 a {
  color: #1a1a1a;
  text-decoration: none;
}

.article-item h3 a:hover {
  color: #2d6a4f;
}

.article-item p {
  margin: 0;
  color: #5c5c5c;
  font-size: 0.95rem;
}

.error {
  color: #b91c1c;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
