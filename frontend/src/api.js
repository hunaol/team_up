const BASE = '/api'

export function getToken() {
  return localStorage.getItem('token') || ''
}
export function setToken(t) {
  t ? localStorage.setItem('token', t) : localStorage.removeItem('token')
}
export function getAdminToken() {
  return localStorage.getItem('admin_token') || ''
}
export function setAdminToken(t) {
  t ? localStorage.setItem('admin_token', t) : localStorage.removeItem('admin_token')
}

function detailToMessage(detail) {
  if (!detail) return '请求失败，请稍后重试'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        if (typeof d === 'string') return d
        const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : ''
        return field && field !== 'body' ? `${d.msg}` : d.msg || JSON.stringify(d)
      })
      .join('；')
  }
  return JSON.stringify(detail)
}

export async function api(path, { method = 'GET', body, token } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  // 没登录学生账号时，只读请求带上管理员令牌：后端只把他当「只读查看者」，
  // 学生身份相关的接口照样会拒绝（get_optional_user 只认非管理员令牌），
  // 这样管理员审核内容时不会处处被要求登录。写操作不带，避免误用管理员身份。
  const tk = token !== undefined ? token : getToken() || (method === 'GET' ? getAdminToken() : '')
  if (tk) headers['Authorization'] = 'Bearer ' + tk

  let res
  try {
    res = await fetch(BASE + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined
    })
  } catch (e) {
    const error = new Error('网络异常，请检查后端服务是否启动')
    error.status = 0
    throw error
  }

  let data = null
  try {
    data = await res.json()
  } catch (e) {
    /* 无响应体 */
  }

  if (!res.ok) {
    const error = new Error(detailToMessage(data && data.detail))
    error.status = res.status
    throw error
  }
  return data
}

/** 管理端接口：401 时清空后台令牌并回到登录页 */
export function adminApi(path, opts = {}) {
  return api(path, { ...opts, token: getAdminToken() }).catch((err) => {
    if (err.status === 401) {
      setAdminToken('')
      if (!location.pathname.startsWith('/admin/login')) {
        location.assign('/admin/login')
      }
    }
    throw err
  })
}

/** 上传图片，返回可直接使用的 URL */
export async function uploadImage(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(BASE + '/uploads', {
    method: 'POST',
    headers: getToken() ? { Authorization: 'Bearer ' + getToken() } : {},
    body: form
  })
  let data = null
  try {
    data = await res.json()
  } catch (e) {
    /* ignore */
  }
  if (!res.ok) {
    throw new Error(detailToMessage(data && data.detail))
  }
  return data.url
}
