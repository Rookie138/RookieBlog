<template>
  <form class="comment-form" @submit.prevent="onSubmit">
    <p v-if="title" class="form-title">{{ title }}</p>

    <div class="row">
      <label class="field">
        <span>昵称 <em>*</em></span>
        <input
          v-model.trim="form.nickname"
          type="text"
          maxlength="25"
          placeholder="怎么称呼你"
          autocomplete="nickname"
          required
        />
      </label>

      <label class="field">
        <span>邮箱 <em>*</em></span>
        <input
          v-model.trim="form.email"
          type="email"
          maxlength="120"
          placeholder="不会公开显示"
          autocomplete="email"
          required
        />
      </label>
    </div>

    <label class="field">
      <span>评论内容 <em>*</em></span>
      <textarea
        v-model="form.content"
        rows="4"
        maxlength="2000"
        :placeholder="placeholder"
        required
      ></textarea>
      <small class="counter">{{ form.content.length }} / 2000</small>
    </label>

    <!--
      蜜罐字段：真实用户看不见也不会填，脚本会无脑填。
      CSS 隐藏（不是 display:none，某些脚本会跳过 display:none 的字段）。
      后端目前还没有校验它，等防刷做完后直接生效；前端先埋好，避免以后改表单结构。
    -->
    <div class="hp" aria-hidden="true">
      <label>
        请勿填写此项
        <input v-model="form.hp" type="text" tabindex="-1" autocomplete="off" />
      </label>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="actions">
      <button type="submit" class="primary" :disabled="submitting">
        {{ submitting ? '提交中…' : submitText }}
      </button>
      <button v-if="showCancel" type="button" class="ghost" :disabled="submitting" @click="$emit('cancel')">
        取消
      </button>
      <span v-if="hint" class="hint muted">{{ hint }}</span>
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'

defineProps({
  /** 表单标题，比如「发表评论」「回复 张三」 */
  title: { type: String, default: '发表评论' },
  placeholder: { type: String, default: '说点什么…' },
  submitText: { type: String, default: '提交评论' },
  /** 是否显示取消按钮（回复场景为 true） */
  showCancel: { type: Boolean, default: false },
  /** 按钮下方的一行提示，可用于显示「已提交」之类的结果 */
  hint: { type: String, default: '' },
  /** 是否处于提交中（由父组件控制） */
  submitting: { type: Boolean, default: false },
  /** 父组件传入的提交错误信息 */
  error: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  nickname: readStored('comment_author_nickname'),
  email: readStored('comment_author_email'),
  content: '',
  hp: '',
})

const mountedAt = ref(Date.now())

function readStored(key) {
  try {
    return localStorage.getItem(key) || ''
  } catch {
    return ''
  }
}

function writeStored(key, value) {
  try {
    localStorage.setItem(key, value)
  } catch {
    // 隐私模式下 localStorage 可能不可用，忽略即可
  }
}

function onSubmit() {
  // 蜜罐被填 -> 直接静默丢弃，不给脚本任何反馈
  if (form.hp) {
    emit('submit', null)
    return
  }

  const nickname = form.nickname.trim()
  const email = form.email.trim()
  const content = form.content.trim()

  if (!nickname) return
  if (!email) return
  if (!content) return

  writeStored('comment_author_nickname', nickname)
  writeStored('comment_author_email', email)

  emit('submit', {
    nickname,
    email,
    content,
    // 提交耗时：后端做防刷时可用来识别「秒填秒交」的脚本（目前后端未使用）
    elapsed_ms: Date.now() - mountedAt.value,
  })
}

/** 提交成功后由父组件调用：清空内容并重置计时，保留昵称/邮箱方便连续评论 */
function reset() {
  form.content = ''
  mountedAt.value = Date.now()
}

defineExpose({ reset })
</script>

<style scoped>
.comment-form {
  padding: 1rem 1.1rem;
  background: #fff;
  border: 1px solid #e4e2dc;
  border-radius: 10px;
}

.form-title {
  margin: 0 0 0.85rem;
  font-weight: 600;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-bottom: 0.85rem;
}

.field > span {
  font-size: 0.88rem;
  color: #5c5c5c;
}

.field em {
  color: #b91c1c;
  font-style: normal;
}

.field input,
.field textarea {
  width: 100%;
  padding: 0.5rem 0.7rem;
  border: 1px solid #e4e2dc;
  border-radius: 8px;
  background: #fff;
  font: inherit;
}

.field textarea {
  resize: vertical;
  line-height: 1.7;
}

.counter {
  align-self: flex-end;
  font-size: 0.78rem;
  color: #8a8a8a;
}

/* 蜜罐：移出可视区域，真人看不到、tab 也聚焦不到 */
.hp {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.primary,
.ghost {
  padding: 0.45rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
}

.primary {
  border: none;
  background: #2d6a4f;
  color: #fff;
}

.ghost {
  border: 1px solid #e4e2dc;
  background: #fff;
}

.primary:disabled,
.ghost:disabled {
  opacity: 0.7;
  cursor: wait;
}

.hint {
  font-size: 0.85rem;
}

.error {
  margin: 0 0 0.6rem;
  color: #b91c1c;
  font-size: 0.9rem;
}

@media (max-width: 640px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
