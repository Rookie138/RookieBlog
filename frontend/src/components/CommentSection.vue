<template>
  <section class="comments">
    <h2 class="section-title">
      评论
      <span v-if="total > 0" class="count">{{ total }}</span>
    </h2>

    <!-- 发表评论 -->
    <CommentForm
      ref="rootFormRef"
      :submitting="store.submitting"
      :error="rootError"
      :hint="store.hint"
      @submit="onSubmitRoot"
    />
    <p v-if="store.hint" class="notice muted">
      注意：后端尚未做评论审核，提交后会立即对所有访客可见。
    </p>

    <!-- 评论列表 -->
    <p v-if="store.loading" class="muted">评论加载中…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>
    <p v-else-if="comments.length === 0" class="muted empty">还没有评论，来说点什么吧。</p>

    <template v-else>
      <ul class="comment-list">
        <CommentItem
          v-for="node in comments"
          :key="node.id"
          :comment="node"
          :replying-to="replyingTo"
          :submitting="store.submitting"
          :reply-error="replyError"
          :reply-hint="store.hint"
          @reply="onReply"
          @submit-reply="onSubmitReply"
          @cancel-reply="onCancelReply"
        />
      </ul>

      <!-- 后端按「顶级评论」分页，每页 10 条 -->
      <div v-if="store.hasMore(slug)" class="more">
        <button type="button" class="more-btn" :disabled="store.loadingMore" @click="onLoadMore">
          {{ store.loadingMore ? '加载中…' : '加载更多评论' }}
        </button>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

import CommentForm from '@/components/CommentForm.vue'
import CommentItem from '@/components/CommentItem.vue'
import { useCommentStore } from '@/stores/comments'

const props = defineProps({
  /** 文章 slug */
  slug: { type: String, required: true },
})

const store = useCommentStore()

const loadError = ref('')
const rootError = ref('')
const replyError = ref('')
const replyingTo = ref(null)
const rootFormRef = ref(null)

const comments = computed(() => store.treeOf(props.slug))
/** 评论总数来自后端 total_comment（含回复），比本地统计更准 */
const total = computed(() => store.metaOf(props.slug).total)

async function load() {
  loadError.value = ''
  try {
    await store.load(props.slug, { force: true })
  } catch (error) {
    // 文章没有评论时后端返回 404，api 层已转成空列表，走到这里的都是真实错误
    loadError.value = error.message || '评论加载失败'
  }
}

async function onLoadMore() {
  loadError.value = ''
  try {
    await store.loadMore(props.slug)
  } catch (error) {
    loadError.value = error.message || '加载更多评论失败'
  }
}

async function onSubmitRoot(payload) {
  // 蜜罐命中：payload 为 null，静默忽略
  if (!payload) return
  rootError.value = ''
  try {
    await store.submit(props.slug, payload)
    rootFormRef.value?.reset()
  } catch (error) {
    rootError.value = error.message
  }
}

function onReply(comment) {
  replyError.value = ''
  replyingTo.value = replyingTo.value === comment.id ? null : comment.id
}

function onCancelReply() {
  replyingTo.value = null
  replyError.value = ''
}

async function onSubmitReply({ parent, payload }) {
  if (!payload) return
  replyError.value = ''
  try {
    await store.submit(props.slug, { ...payload, parent_id: parent.id })
    replyingTo.value = null
  } catch (error) {
    replyError.value = error.message
  }
}

defineExpose({ load })
</script>

<style scoped>
.comments {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e4e2dc;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem;
  font-size: 1.2rem;
}

.count {
  padding: 0 0.5rem;
  border-radius: 999px;
  background: #eeece6;
  color: #5c5c5c;
  font-size: 0.85rem;
  font-weight: 400;
}

.notice {
  margin: 0.6rem 0 0;
  font-size: 0.82rem;
}

.empty {
  margin-top: 1.25rem;
}

.comment-list {
  margin: 1.25rem 0 0;
  padding: 0;
  list-style: none;
}

.more {
  margin-top: 1.25rem;
  text-align: center;
}

.more-btn {
  padding: 0.45rem 1rem;
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

.error {
  color: #b91c1c;
}
</style>
