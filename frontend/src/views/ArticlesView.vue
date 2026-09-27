<template>
  <div class="view">
    <h1>文章</h1>

    <label class="search">
      <span class="sr-only">搜索文章</span>
      <input v-model.trim="keyword" type="search" placeholder="搜索标题或摘要" />
    </label>

    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="filtered.length === 0" class="muted">
      {{ keyword ? '没有找到相关文章。' : '还没有已发布的文章。' }}
    </p>
    <template v-else>
      <ul class="article-list">
        <li v-for="item in filtered" :key="item.slug" class="article-item">
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

      <!-- 后端按页返回（默认每页 10 篇），本地搜索只覆盖已加载的部分 -->
      <div v-if="!keyword && articleStore.hasMore" class="more">
        <button type="button" class="more-btn" :disabled="articleStore.loadingMore" @click="onLoadMore">
          {{ articleStore.loadingMore ? '加载中…' : '加载更多' }}
        </button>
      </div>
      <p v-else-if="!keyword && articleStore.list.length > 0" class="muted end">已经到底了</p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { useArticleStore } from '@/stores/articles'
import { formatDate } from '@/utils/format'

const articleStore = useArticleStore()
const keyword = ref('')

const loading = computed(() => articleStore.loadingList)
const error = computed(() => articleStore.listError)
const filtered = computed(() => articleStore.search(keyword.value))

function onLoadMore() {
  articleStore.loadMore()
}

onMounted(() => {
  articleStore.loadList()
})
</script>

<style scoped>
.more {
  margin-top: 1.25rem;
  text-align: center;
}

.more-btn {
  padding: 0.5rem 1.1rem;
  border: 1px solid #e4e2dc;
  border-radius: 8px;
  background: #fff;
  color: #2d6a4f;
  cursor: pointer;
}

.more-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.end {
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.85rem;
}

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

.summary {
  margin: 0 0 0.4rem;
  color: #5c5c5c;
  font-size: 0.95rem;
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
