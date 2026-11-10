// 移动端截图脚本：CDP 驱动 headless Chrome，390x844 视口逐页截图
// 用法：node scripts/shots-mobile.mjs [outDir]
import fs from 'node:fs'
import path from 'node:path'

const OUT = process.argv[2] || '.shots-mobile'
const BASE = process.env.SHOT_BASE || 'http://localhost:5173'
const CDP = process.env.SHOT_CDP || 'http://127.0.0.1:9222'
const STUDENT = process.env.SHOT_SID || '2024413435'
const NAME = process.env.SHOT_NAME || '韩涛'

fs.mkdirSync(OUT, { recursive: true })
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function findTarget() {
  for (let i = 0; i < 60; i++) {
    try {
      const list = await (await fetch(CDP + '/json/list')).json()
      const page = list.find((t) => t.type === 'page')
      if (page?.webSocketDebuggerUrl) return page
    } catch (e) {
      /* Chrome 还没起来 */
    }
    await sleep(250)
  }
  throw new Error('找不到 CDP 页面目标，请确认 Chrome 已用 --remote-debugging-port=9222 启动')
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
  const r = await send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true })
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' ' + (r.result?.description || ''))
  return r.result?.value
}

async function goto(url, waitMs = 1200) {
  events.length = 0
  await send('Page.navigate', { url })
  for (let i = 0; i < 80; i++) {
    if (events.includes('Page.loadEventFired')) break
    await sleep(80)
  }
  await sleep(waitMs)
}

async function shot(name, fullPage = true) {
  const params = { format: 'png', captureBeyondViewport: fullPage }
  const { data } = await send('Page.captureScreenshot', params)
  const file = path.join(OUT, name + '.png')
  fs.writeFileSync(file, Buffer.from(data, 'base64'))
  console.log('saved', file)
}

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride', {
    width,
    height,
    deviceScaleFactor: mobile ? 2 : 1,
    mobile,
    screenWidth: width,
    screenHeight: height
  })
  if (mobile) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 })
}

await send('Page.enable')
await send('Runtime.enable')

// 登录拿到 token
await setViewport(390, 844, true)
await goto(BASE + '/login', 800)

const creds = await evaluate(`(async () => {
  const r = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: ${JSON.stringify(STUDENT)}, name: ${JSON.stringify(NAME)} })
  })
  return await r.json()
})()`)
if (!creds.token) throw new Error('登录失败：' + JSON.stringify(creds))
await evaluate(
  `localStorage.setItem('token', ${JSON.stringify(creds.token)});
   localStorage.setItem('user', ${JSON.stringify(JSON.stringify(creds.user))});`
)
console.log('logged in as', creds.user.name, 'id', creds.user.id)

const pages = [
  ['m-home', '/', 1600],
  ['m-posts', '/posts', 1500],
  ['m-posts-join', '/posts?type=join', 1400],
  ['m-detail', '/post/1', 1500],
  ['m-publish', '/publish', 1500],
  ['m-profile', '/profile', 1500],
  ['m-messages', '/messages', 1400],
  ['m-messages-chat', '/messages/6', 1400],
  ['m-my', '/my', 1400],
  ['m-favorites', '/favorites', 1200]
]

for (const [name, p, wait] of pages) {
  await goto(BASE + p, wait)
  await shot(name)
}

// 筛选面板展开态
await goto(BASE + '/posts', 1400)
const clicked = await evaluate(`(() => {
  const btns = [...document.querySelectorAll('button')]
  const b = btns.find((x) => x.textContent.trim().startsWith('筛选'))
  if (b) { b.click(); return true }
  return false
})()`)
console.log('filter opened:', clicked)
await sleep(700)
await shot('m-posts-filter', true)

// 桌面端回归
await setViewport(1440, 900, false)
await goto(BASE + '/', 1500)
await shot('d-home', false)
await goto(BASE + '/posts', 1400)
await shot('d-posts', false)
await goto(BASE + '/post/1', 1500)
await shot('d-detail', false)
await goto(BASE + '/profile', 1400)
await shot('d-profile', false)

ws.close()
console.log('done ->', OUT)
