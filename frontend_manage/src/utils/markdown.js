import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({
  gfm: true,
  breaks: true,
})

export function renderMarkdown(source) {
  const html = marked.parse(source || '')
  return DOMPurify.sanitize(html)
}

export function toSlug(title) {
  const ascii = title
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
  return ascii || `post-${Date.now()}`
}
