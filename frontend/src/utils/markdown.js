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
