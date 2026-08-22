import request from './request'

export function fetchArticles() {
  return request.get('/common-articles/articles')
}

export function fetchArticleDetail(slug) {
  return request.get(`/common-articles/articles/${encodeURIComponent(slug)}`)
}
