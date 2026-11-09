import { reactive } from 'vue'
import { api, setToken } from './api'

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
}

/** 管理员登录态（仅用于侧栏展示与路由守卫） */
export const admin = reactive({
  logged: !!localStorage.getItem('admin_token')
})

export function setAdminLogged(v) {
  admin.logged = !!v
}
