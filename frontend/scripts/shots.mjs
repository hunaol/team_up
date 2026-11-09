// 开发期截图脚本：通过 CDP 驱动 headless Chrome，逐页截图用于视觉核对
// 用法：node scripts/shots.mjs [outDir]
import fs from 'node:fs'
import path from 'node:path'

const OUT = process.argv[2] || '.shots'
const BASE = 'http://localhost:5173'
const CDP = 'http://127.0.0.1:9222'

fs.mkdirSync(OUT, { recursive: true })

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function findTarget() {
  for (let i = 0; i < 40; i++) {
    try {
      const list = await (await fetch(CDP + '/json/list')).json()
      const page = list.find((t) => t.type === 'page')
      if (page && page.webSocketDebuggerUrl) return page
    } catch (e) {
      /* 等 Chrome 起来 */
    }
    await sleep(250)
  }
  throw new Error('找不到 CDP 页面目标')
}

const target = await findTarget()
const ws = new WebSocket(target.webSocketDebuggerUrl)
let seq = 0
const pending = new Map()
const events = []

ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data)
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id)
    pending.delete(msg.id)
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result)
  } else if (msg.method) {
    events.push(msg.method)
  }
})

await new Promise((res, rej) => {
  ws.addEventListener('open', res, { once: true })
  ws.addEventListener('error', rej, { once: true })
})

function send(method, params = {}) {
  const id = ++seq
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })
}

async function evaluate(expression, awaitPromise = true) {
  const r = await send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true
  })
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' ' + (r.result?.description || ''))
  return r.result?.value
}

async function goto(url, waitMs = 1200) {
  events.length = 0
  await send('Page.navigate', { url })
  for (let i = 0; i < 60; i++) {
    if (events.includes('Page.loadEventFired')) break
    await sleep(100)
  }
  await sleep(waitMs)
}

async function shot(name, fullPage = true) {
  const params = { format: 'png' }
  if (fullPage) params.captureBeyondViewport = true
  else params.clip = { x: 0, y: 0, width: 1440, height: 900, scale: 1 }
  const { data } = await send('Page.captureScreenshot', params)
  const file = path.join(OUT, name + '.png')
  fs.writeFileSync(file, Buffer.from(data, 'base64'))
  console.log('saved', file)
}

await send('Page.enable')
await send('Runtime.enable')
await send('Emulation.setDeviceMetricsOverride', {
  width: 1440,
  height: 900,
  deviceScaleFactor: 1,
  mobile: false
})

await goto(BASE + '/')

// 取用户令牌 + 管理员令牌，写入 localStorage
const creds = await evaluate(`(async () => {
  const out = {}
  try {
    const r = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: '2024413435', name: '韩涛' })
    })
    const d = await r.json()
    if (d.token) out.user = d
  } catch (e) { out.userErr = String(e) }
  try {
    const r = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'admin', password: 'admin123' })
    })
    const d = await r.json()
    if (d.token) out.admin = d
  } catch (e) { out.adminErr = String(e) }
  return out
})()`)

console.log('login:', JSON.stringify(creds).slice(0, 200))

if (creds.user) {
  await evaluate(
    `localStorage.setItem('token', ${JSON.stringify(creds.user.token)});
     localStorage.setItem('user', ${JSON.stringify(JSON.stringify(creds.user.user))});`
  )
}
if (creds.admin) {
  await evaluate(`localStorage.setItem('admin_token', ${JSON.stringify(creds.admin.token)});`)
}

const pages = [
  ['home', '/'],
  ['posts', '/posts'],
  ['my', '/my'],
  ['publish', '/publish'],
  ['favorites', '/favorites'],
  ['detail', '/post/1'],
  ['detail-other', '/post/3'],
  ['admin', '/admin'],
  ['admin-users', '/admin/users'],
  ['admin-posts', '/admin/posts']
]

for (const [name, p] of pages) {
  await goto(BASE + p, 1500)
  await shot(name)
}

// 登录页需要清掉登录态才会显示（登录页本身可直达）
await goto(BASE + '/login', 900)
await shot('login', false)
await goto(BASE + '/admin/login', 900)
await shot('admin-login', false)

ws.close()
