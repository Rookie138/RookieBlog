<template>
  <section>
    <div class="head">
      <h1>{{ isCreate ? '写文章' : '编辑文章' }}</h1>
      <p v-if="hint" class="muted">{{ hint }}</p>
    </div>

    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <form v-else class="editor" @submit.prevent="onSave('draft')">
      <label class="field">
        标题
        <input v-model.trim="form.title" type="text" required @blur="syncSlug" />
      </label>

      <label class="field">
        链接 slug
        <input
          v-model.trim="form.slug"
          type="text"
          required
          :disabled="!isCreate"
          @input="slugTouched = true"
        />
        <span v-if="!isCreate" class="hint">slug 用于定位文章，创建后不可修改</span>
      </label>

      <label class="field">
        摘要
        <textarea v-model.trim="form.summary" rows="2" />
      </label>

      <div class="md-wrap">
        <label class="field grow">
          Markdown 正文
          <textarea v-model="form.context" class="md-input" spellcheck="false" />
        </label>
        <div class="field grow">
          <span>预览</span>
          <div class="preview markdown-body" v-html="previewHtml"></div>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="actions">
        <button type="submit" class="ghost" :disabled="saving">
          {{ saving ? '保存中…' : '保存草稿' }}
        </button>
        <button type="button" class="primary" :disabled="saving" @click="onSave('published')">
          发布
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createArticle, fetchManageArticle, updateArticle } from '@/api/articles'
import { renderMarkdown, toSlug } from '@/utils/markdown'

const route = useRoute()
const router = useRouter()

const isCreate = computed(() => route.name === 'article-create')
const previewHtml = computed(() => renderMarkdown(form.context))

const form = reactive({
  title: '',
  slug: '',
  summary: '',
  context: '',
  status: 'draft',
})

const loading = ref(!isCreate.value)
const saving = ref(false)
const error = ref('')
const loadError = ref('')
const hint = ref('')
const slugTouched = ref(false)

function syncSlug() {
  if (!isCreate.value || slugTouched.value || !form.title) return
  form.slug = toSlug(form.title)
}

async function load() {
  if (isCreate.value) return
  loading.value = true
  try {
    const data = await fetchManageArticle(route.params.slug)
    const article = data.article
    if (!article) {
      loadError.value = '文章不存在'
      return
    }
    form.title = article.title || ''
    form.slug = article.slug || route.params.slug
    form.summary = article.summary || ''
    form.context = article.context || ''
    form.status = article.status || 'draft'
  } catch (e) {
    loadError.value = e.message
  } finally {
    loading.value = false
  }
}

async function onSave(status) {
  error.value = ''
  hint.value = ''
  saving.value = true
  form.status = status
  if (isCreate.value && !form.slug) form.slug = toSlug(form.title)

  const payload = {
    slug: form.slug,
    title: form.title,
    summary: form.summary,
    context: form.context,
    status,
  }

  try {
    if (isCreate.value) {
      await createArticle(payload)
      hint.value = status === 'published' ? '已发布' : '草稿已保存'
      router.replace({ name: 'article-edit', params: { slug: form.slug } })
    } else {
      await updateArticle(route.params.slug, payload)
      hint.value = status === 'published' ? '已发布' : '草稿已保存'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.head h1 {
  margin: 0;
  font-size: 1.4rem;
}

.editor {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field input,
.field textarea {
  width: 100%;
  padding: 0.55rem 0.75rem;
  border: 1px solid #e4e2dc;
  border-radius: 8px;
  background: #fff;
}

.field input:disabled {
  background: #f2f0eb;
  color: #5c5c5c;
}

.hint {
  font-size: 0.82rem;
  color: #8a8a8a;
}

.md-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  min-height: 420px;
}

.md-input,
.preview {
  min-height: 420px;
}

.md-input {
  resize: vertical;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92rem;
  line-height: 1.7;
}

.preview {
  overflow: auto;
  padding: 0.85rem 1rem;
  background: #fff;
  border: 1px solid #e4e2dc;
  border-radius: 8px;
}

.actions {
  display: flex;
  gap: 0.75rem;
}

.ghost,
.primary {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
}

.ghost {
  border: 1px solid #e4e2dc;
  background: #fff;
}

.primary {
  border: none;
  background: #2d6a4f;
  color: #fff;
}

.ghost:disabled,
.primary:disabled {
  opacity: 0.7;
  cursor: wait;
}

@media (max-width: 900px) {
  .md-wrap {
    grid-template-columns: 1fr;
  }
}
</style>
