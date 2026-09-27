<template>
  <li class="comment-item" :class="{ 'is-root': depth === 0 }">
    <div class="head">
      <span class="nickname">{{ comment.nickname }}</span>
      <span class="time" :title="formatDateTime(comment.created_at)">
        {{ formatRelative(comment.created_at) }}
      </span>
    </div>

    <p class="content">{{ comment.content }}</p>

    <div class="ops">
      <button type="button" class="link-btn" @click="$emit('reply', comment)">
        回复
      </button>
      <button
        v-if="deletable"
        type="button"
        class="link-btn danger"
        @click="$emit('delete', comment)"
      >
        删除
      </button>
      <button
        v-if="hasChildren"
        type="button"
        class="link-btn"
        @click="expanded = !expanded"
      >
        {{ expanded ? '收起回复' : `展开 ${replies.length} 条回复` }}
      </button>
    </div>

    <!-- 内联回复表单：同一时刻只展开一个（由父组件通过 replyingTo 控制） -->
    <CommentForm
      v-if="replyingTo === comment.id"
      class="reply-form"
      :title="`回复 ${comment.nickname}`"
      placeholder="回复点什么…"
      submit-text="提交回复"
      show-cancel
      :submitting="submitting"
      :error="replyError"
      :hint="replyHint"
      @submit="$emit('submit-reply', { parent: comment, payload: $event })"
      @cancel="$emit('cancel-reply')"
    />

    <!-- 展开的回复列表：递归渲染 -->
    <ul v-if="hasChildren && expanded" class="children">
      <CommentItem
        v-for="child in replies"
        :key="child.id"
        :comment="child"
        :depth="depth + 1"
        :deletable="deletable"
        :submitting="submitting"
        :replying-to="replyingTo"
        :reply-error="replyError"
        :reply-hint="replyHint"
        @reply="$emit('reply', $event)"
        @delete="$emit('delete', $event)"
        @submit-reply="$emit('submit-reply', $event)"
        @cancel-reply="$emit('cancel-reply')"
      />
    </ul>
  </li>
</template>

<script setup>
import { computed, ref } from 'vue'

import CommentForm from './CommentForm.vue'
import { formatDateTime, formatRelative } from '@/utils/format'

defineOptions({ name: 'CommentItem' })

const props = defineProps({
  /** 评论节点：{ id, article_id, parent_id, nickname, content, created_at, children } */
  comment: { type: Object, required: true },
  /** 嵌套深度，用于视觉缩进 */
  depth: { type: Number, default: 0 },
  /** 是否显示删除按钮（管理端为 true） */
  deletable: { type: Boolean, default: false },
  /** 是否有回复正在提交（透传给回复表单以禁用按钮） */
  submitting: { type: Boolean, default: false },
  /** 当前正在回复的评论 id（同一时刻只允许展开一个回复框） */
  replyingTo: { type: [Number, String], default: null },
  /** 回复提交失败信息 */
  replyError: { type: String, default: '' },
  /** 回复提交成功提示 */
  replyHint: { type: String, default: '' },
})

// 事件在模板里以 $emit 触发，这里只做声明（供 Vue 校验事件名）
defineEmits(['reply', 'delete', 'submit-reply', 'cancel-reply'])

const expanded = ref(false)

const replies = computed(() => props.comment.children ?? [])
const hasChildren = computed(() => replies.value.length > 0)
</script>

<style scoped>
.comment-item {
  padding: 0.9rem 0;
  border-bottom: 1px solid #efece6;
}

.comment-item:last-child {
  border-bottom: none;
}

.head {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  margin-bottom: 0.35rem;
}

.nickname {
  font-weight: 600;
}

.time {
  font-size: 0.8rem;
  color: #8a8a8a;
}

.content {
  margin: 0 0 0.4rem;
  white-space: pre-wrap;
  word-break: break-word;
}

.ops {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.link-btn {
  padding: 0;
  border: none;
  background: none;
  color: #2d6a4f;
  cursor: pointer;
  font-size: 0.85rem;
}

.link-btn:hover {
  text-decoration: underline;
}

.link-btn.danger {
  color: #b91c1c;
}

.children {
  margin: 0.6rem 0 0 0.25rem;
  padding-left: 0.9rem;
  list-style: none;
  border-left: 2px solid #e4e2dc;
}

.children .children {
  padding-left: 0.6rem;
}

.reply-form {
  margin-top: 0.75rem;
}
</style>
