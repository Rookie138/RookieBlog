<template>
  <section>
    <div class="head">
      <h1>文章列表</h1>
      <RouterLink :to="{ name: 'article-create' }" class="btn">写文章</RouterLink>
    </div>

    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="articles.length === 0" class="muted">还没有文章，先写一篇吧。</p>

    <table v-else class="table">
      <thead>
        <tr>
          <th>标题</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in articles" :key="item.slug">
          <td>
            <RouterLink :to="{ name: 'article-edit', params: { slug: item.slug } }">
              {{ item.title }}
            </RouterLink>
            <p class="summary">{{ item.summary }}</p>
          </td>
          <td>
            <span class="status" :class="item.status">{{ statusText(item.status) }}</span>
          </td>
          <td class="actions">
            <RouterLink :to="{ name: 'article-edit', params: { slug: item.slug } }">编辑</RouterLink>
            <button
              v-if="item.status !== 'published'"
              type="button"
              @click="changeStatus(item, 'published')"
            >
              发布
            </button>
            <button
              v-else
              type="button"
              @click="changeStatus(item, 'draft')"
            >
              撤回
            </button>
            <button type="button" class="danger" @click="onDelete(item)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { deleteArticle, fetchManageArticles, updateArticle } from '@/api/articles'

const articles = ref([])
const loading = ref(true)
const error = ref('')

const statusMap = {
  draft: '草稿',
  published: '已发布',
  deleted: '已删除',
}

function statusText(status) {
  return statusMap[status] || status || '草稿'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchManageArticles()
    articles.value = data.data || data.articles || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function changeStatus(item, status) {
  try {
    await updateArticle(item.slug, { status })
    item.status = status
  } catch (e) {
    error.value = e.message
  }
}

async function onDelete(item) {
  if (!confirm(`确定删除「${item.title}」吗？`)) return
  try {
    await deleteArticle(item.slug)
    articles.value = articles.value.filter((article) => article.slug !== item.slug)
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.head h1 {
  margin: 0;
  font-size: 1.4rem;
}

.btn {
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  background: #2d6a4f;
  color: #fff;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 1px solid #e4e2dc;
}

th,
td {
  padding: 0.85rem 1rem;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid #e4e2dc;
}

th {
  color: #5c5c5c;
  font-weight: 500;
  background: #faf9f6;
}

.summary {
  margin: 0.3rem 0 0;
  color: #5c5c5c;
  font-size: 0.9rem;
}

.status {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: 0.8rem;
  background: #eeece6;
  color: #5c5c5c;
}

.status.published {
  background: #e8f5ee;
  color: #2d6a4f;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  white-space: nowrap;
}

.actions button {
  border: none;
  background: none;
  color: #2d6a4f;
  cursor: pointer;
  padding: 0;
}

.actions .danger {
  color: #b91c1c;
}
</style>
