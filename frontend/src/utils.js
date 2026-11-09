export const TYPE_TEXT = { team: '找队友', join: '找队伍' }
export const TYPE_DESC = {
  team: '我在组建队伍，寻找志同道合的队友',
  join: '我想加入一支队伍，一起参加比赛'
}
export const STATUS_TEXT = {
  open: '招募中',
  full: '已招满',
  down: '已下架',
  expired: '已过期'
}
export const STATUS_CLASS = {
  open: 'pill-open',
  full: 'pill-full',
  down: 'pill-down',
  expired: 'pill-expired'
}
export const CONTACT_TEXT = { wechat: '微信', qq: 'QQ', phone: '手机号' }
export const CONTACT_PLACEHOLDER = {
  wechat: '请输入微信号，如 wxid_abc123',
  qq: '请输入 5–12 位 QQ 号',
  phone: '请输入 11 位手机号'
}

/** 后端返回的是 UTC 朴素时间（无 Z），需要补上时区标识 */
function parseTime(iso) {
  if (!iso) return new Date(0)
  return new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z')
}

export function isNew(iso) {
  return Date.now() - parseTime(iso).getTime() < 86400 * 1000
}

export function relTime(iso) {
  const t = parseTime(iso)
  const diff = (Date.now() - t.getTime()) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + ' 分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + ' 小时前'
  if (diff < 86400 * 7) return Math.floor(diff / 86400) + ' 天前'
  return fmtDate(iso)
}

export function fmtDate(iso) {
  const t = parseTime(iso)
  const p = (n) => String(n).padStart(2, '0')
  return `${t.getFullYear()}-${p(t.getMonth() + 1)}-${p(t.getDate())}`
}

/** 剩余天数（截止日期），无截止日期返回 null */
export function daysLeft(deadline) {
  if (!deadline) return null
  const end = new Date(deadline + 'T23:59:59')
  return Math.ceil((end.getTime() - Date.now()) / 86400000)
}

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (e) {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    let ok = false
    try {
      ok = document.execCommand('copy')
    } catch (e2) {
      ok = false
    }
    document.body.removeChild(ta)
    return ok
  }
}

/** 旧帖子的纯文本描述 → 富文本 HTML（保留换行） */
export function descToHtml(desc) {
  const raw = desc || ''
  // 含任意白名单标签（含图片）就按 HTML 原样输出，否则转义成纯文本
  if (/<\/?(b|i|u|br|img)\b/i.test(raw)) return raw
  return raw
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

/** 富文本 HTML → 纯文本 */
export function htmlToText(html) {
  const div = document.createElement('div')
  div.innerHTML = html || ''
  return (div.textContent || '').replace(/\s+/g, ' ').trim()
}

/** 纯文本 → 富文本 HTML（保留换行） */
export function textToHtml(text) {
  return (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

const GRADIENTS = [
  ['#eef1fb', '#dfe5f6'],
  ['#eefaf4', '#dcf1e6'],
  ['#fdf4e9', '#f8e6cf'],
  ['#f3effe', '#e7e0fa'],
  ['#fdeef1', '#f8dde3'],
  ['#eaf4fd', '#d9eafa']
]

export function gradientOf(seed) {
  const s = String(seed || 'x')
  let h = 0
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0
  return GRADIENTS[h % GRADIENTS.length]
}

export function initials(name) {
  const n = (name || '').trim()
  if (!n) return '?'
  return n.slice(-2)
}

export function initialsOne(name) {
  const n = (name || '').trim()
  if (!n) return '?'
  return n.slice(0, 1)
}

export function thousand(n) {
  return (n ?? 0).toLocaleString('en-US')
}

export function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n))
}
