import request from './request'

export function fetchManageArticles() {
  return request.get('/manage-articles/articles')
}

export function fetchManageArticle(slug) {
  return request.get(`/manage-articles/articles/${encodeURIComponent(slug)}`)
}

export function createArticle(payload) {
  return request.post('/manage-articles/articles', payload)
}

export function updateArticle(slug, payload) {
  return request.put(`/manage-articles/articles/${encodeURIComponent(slug)}`, payload)
}

export function deleteArticle(slug) {
  return request.delete(`/manage-articles/articles/${encodeURIComponent(slug)}`)
}
