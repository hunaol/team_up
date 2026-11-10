import { reactive } from 'vue'
import { api, getToken, setToken } from './api'

export const auth = reactive({
  user: JSON.parse(localStorage.getItem('user') || 'null')
})

export function setUser(u) {
  auth.user = u
  if (u) localStorage.setItem('user', JSON.stringify(u))
  else localStorage.removeItem('user')
}

export async function logout() {
  try {
    await api('/auth/logout', { method: 'POST' })
  } catch (e) {
    /* 令牌可能已失效，忽略 */
  }
  setToken('')
  setUser(null)
  badge.unread = 0
}

/** 未读私信数（底部标签栏 / 侧栏角标） */
export const badge = reactive({ unread: 0 })

export async function refreshUnread() {
  if (!getToken() || !auth.user) {
    badge.unread = 0
    return
  }
  try {
    const r = await api('/messages/unread')
    badge.unread = r.count || 0
  } catch (e) {
    /* 静默 */
  }
}

/** 管理员登录态（仅用于侧栏展示与路由守卫） */
export const admin = reactive({
  logged: !!localStorage.getItem('admin_token')
})

export function setAdminLogged(v) {
  admin.logged = !!v
}
