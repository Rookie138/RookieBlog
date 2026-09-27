<template>
  <div class="view">
    <h1>首页</h1>
    <p class="muted">记录学习与思考的地方。</p>

    <section class="latest">
      <div class="section-head">
        <h2>最近文章</h2>
        <RouterLink :to="{ name: 'articles' }">全部文章</RouterLink>
      </div>

      <p v-if="loading" class="muted">加载中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-else-if="latest.length === 0" class="muted">还没有已发布的文章。</p>
      <ul v-else class="article-list">
        <li v-for="item in latest" :key="item.slug" class="article-item">
          <h3>
            <RouterLink :to="{ name: 'article-detail', params: { slug: item.slug } }">
              {{ item.title }}
            </RouterLink>
          </h3>
          <p v-if="item.summary" class="summary">{{ item.summary }}</p>
          <p class="stats">
            <!-- 列表接口（ArticleSummary）不返回 created_at，只有 updated_time，所以这里显示更新时间 -->
            <span v-if="item.updated_time">更新于 {{ formatDate(item.updated_time) }}</span>
            <span v-if="item.view_count != null">· 阅读 {{ item.view_count }}</span>
            <span v-if="item.comment_count != null">· 评论 {{ item.comment_count }}</span>
          </p>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'

import { useArticleStore } from '@/stores/articles'
import { formatDate } from '@/utils/format'

const articleStore = useArticleStore()

const latest = computed(() => articleStore.latest)
const loading = computed(() => articleStore.loadingList)
const error = computed(() => articleStore.listError)

onMounted(() => {
  articleStore.loadList()
})
</script>

<style scoped>
.latest {
  margin-top: 2rem;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.section-head h2 {
  margin: 0;
  font-size: 1.15rem;
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

.summary {
  margin: 0 0 0.4rem;
  color: #5c5c5c;
}

.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin: 0;
  color: #8a8a8a;
  font-size: 0.82rem;
}

.error {
  color: #b91c1c;
}
</style>
