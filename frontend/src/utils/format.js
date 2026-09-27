/**
 * 时间格式化：后端返回的是 ISO 字符串或 "2026-09-19T14:24:58" 形式，
 * 这里统一做了「非法值不显示」的防御，避免页面上出现 Invalid Date。
 */

/** 格式化为 2026年9月19日 */
export function formatDate(value) {
  const date = parseDate(value)
  if (!date) return ''
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/** 格式化为 2026-09-19 14:24 */
export function formatDateTime(value) {
  const date = parseDate(value)
  if (!date) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
    `${pad(date.getHours())}:${pad(date.getMinutes())}`
  )
}

/** 在一周内显示「x分钟前 / x小时前 / x天前」，更早显示日期 */
export function formatRelative(value) {
  const date = parseDate(value)
  if (!date) return ''
  const diff = Date.now() - date.getTime()
  if (diff < 0) return formatDateTime(value)

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour

  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)} 分钟前`
  if (diff < day) return `${Math.floor(diff / hour)} 小时前`
  if (diff < 7 * day) return `${Math.floor(diff / day)} 天前`
  return formatDate(value)
}

function parseDate(value) {
  if (!value) return null
  const date = value instanceof Date ? value : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}
