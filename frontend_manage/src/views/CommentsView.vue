<template>
  <section>
    <div class="head">
      <h1>评论管理</h1>
      <button type="button" class="btn ghost" :disabled="store.loading" @click="reload">
        {{ store.loading ? '加载中…' : '刷新' }}
      </button>
    </div>

    <p class="notice muted">
      后端评论暂无审核状态，发表后即公开可见；这里只提供浏览与删除。
      评论接口不返回邮箱，所以列表里看不到邮箱。
    </p>

    <div class="toolbar">
      <label class="filter">
        <span class="sr-only">按文章筛选</span>
        <select v-model="articleFilter">
          <option value="">全部文章</option>
          <option v-for="item in articleOptions" :key="item.slug" :value="item.slug">
            {{ item.title }}（{{ store.countByArticle[item.slug] ?? 0 }}）
          </option>
        </select>
      </label>
      <span v-if="!store.loading" class="muted count">
        共 {{ filtered.length }} 条评论 / {{ articleOptions.length }} 篇文章
      </span>
    </div>

    <p v-if="store.loading" class="muted">加载中…</p>
    <p v-else-if="store.error" class="error">{{ store.error }}</p>
    <p v-else-if="actionError" class="error">{{ actionError }}</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <p v-if="!store.loading && filtered.length === 0" class="muted">还没有评论。</p>

    <table v-else-if="!store.loading" class="table">
      <thead>
        <tr>
          <th class="col-nick">昵称</th>
          <th>内容</th>
          <th class="col-article">文章</th>
          <th class="col-time">时间</th>
          <th class="col-ops">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in filtered" :key="item.id">
          <td>
            <span class="nickname">{{ item.nickname }}</span>
            <span v-if="item.parent_id" class="reply-flag">回复</span>
          </td>
          <td>
            <p class="content">{{ item.content }}</p>
          </td>
          <td>
            <RouterLink
              v-if="item.articleSlug"
              :to="{ name: 'article-edit', params: { slug: item.articleSlug } }"
            >
              {{ item.articleTitle }}
            </RouterLink>
          </td>
          <td class="time">{{ formatDateTime(item.created_at) }}</td>
          <td class="ops">
            <button type="button" class="danger" :disabled="deletingId === item.id" @click="onDelete(item)">
              {{ deletingId === item.id ? '删除中…' : '删除' }}
            </button>
            <button
              v-if="hasReplies(item)"
              type="button"
              class="link"
              :disabled="deletingId === item.id"
              @click="onDeleteOnly(item)"
            >
              仅删这条
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { useCommentStore } from '@/stores/comments'

const store = useCommentStore()

const articleFilter = ref('')
const error = ref('')
const actionError = ref('')
const deletingId = ref(null)

const articleOptions = computed(() => Object.values(store.articleMap))

const filtered = computed(() => {
  if (!articleFilter.value) return store.comments
  return store.comments.filter((item) => item.articleSlug === articleFilter.value)
})

/** 这条评论下面还有没有回复 */
function hasReplies(item) {
  return store.comments.some(
    (other) => other.articleSlug === item.articleSlug && other.parent_id === item.id,
  )
}

function formatDateTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
    `${pad(date.getHours())}:${pad(date.getMinutes())}`
  )
}

async function reload() {
  error.value = ''
  actionError.value = ''
  try {
    await store.load({ force: true })
  } catch (e) {
    error.value = e.message
  }
}

async function onDelete(item) {
  const tip = hasReplies(item)
    ? `确定删除「${item.nickname}」的这条评论及其全部回复吗？删除后不可恢复。`
    : `确定删除「${item.nickname}」的这条评论吗？删除后不可恢复。`
  if (!window.confirm(tip)) return
  await doDelete(item, { withReplies: true })
}

async function onDeleteOnly(item) {
  if (!window.confirm('仅删除这一条（它的回复会保留，并可能与文章不再对应），继续吗？')) return
  await doDelete(item, { withReplies: false })
}

async function doDelete(item, opts) {
  actionError.value = ''
  deletingId.value = item.id
  try {
    await store.remove(item, opts)
  } catch (e) {
    actionError.value = `删除失败：${e.message}`
  } finally {
    deletingId.value = null
  }
}

onMounted(reload)
</script>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.head h1 {
  margin: 0;
  font-size: 1.4rem;
}

.notice {
  margin: 0 0 1rem;
  font-size: 0.85rem;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter select {
  padding: 0.35rem 0.6rem;
  border: 1px solid #e4e2dc;
  border-radius: 6px;
  background: #fff;
}

.count {
  font-size: 0.88rem;
  white-space: nowrap;
}

.btn {
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn.ghost {
  border: 1px solid #e4e2dc;
  background: #fff;
}

.btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 1px solid #e4e2dc;
}

th,
td {
  padding: 0.75rem 0.9rem;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid #e4e2dc;
}

th {
  color: #5c5c5c;
  font-weight: 500;
  background: #faf9f6;
}

.col-nick {
  width: 120px;
}

.col-article {
  width: 160px;
}

.col-time {
  width: 140px;
  white-space: nowrap;
}

.col-ops {
  width: 130px;
  white-space: nowrap;
}

.nickname {
  font-weight: 600;
}

.reply-flag {
  display: inline-block;
  margin-left: 0.35rem;
  padding: 0 0.35rem;
  border-radius: 4px;
  background: #eeece6;
  color: #5c5c5c;
  font-size: 0.72rem;
}

.content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.time {
  color: #8a8a8a;
  font-size: 0.85rem;
}

.ops {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  align-items: flex-start;
}

.ops button {
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
}

.ops .danger {
  color: #b91c1c;
}

.ops .link {
  color: #5c5c5c;
}

.ops button:disabled {
  opacity: 0.6;
  cursor: wait;
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
