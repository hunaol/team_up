// 移动端布局体检：检测横向溢出、关键元素尺寸、控制台错误
// 用法：node scripts/probe-mobile.mjs
import fs from 'node:fs'

const BASE = process.env.SHOT_BASE || 'http://localhost:5173'
const CDP = process.env.SHOT_CDP || 'http://127.0.0.1:9222'
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const list = await (await fetch(CDP + '/json/list')).json()
const page = list.find((t) => t.type === 'page')
const ws = new WebSocket(page.webSocketDebuggerUrl)
let seq = 0
const pending = new Map()
let errors = []
let failed = []

ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data)
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id)
    pending.delete(msg.id)
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result)
  } else if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
    errors.push(msg.params.args.map((a) => a.value ?? a.description ?? a.type).join(' '))
  } else if (msg.method === 'Runtime.exceptionThrown') {
    errors.push('EXCEPTION ' + (msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text))
  } else if (msg.method === 'Network.loadingFailed') {
    failed.push(msg.params.errorText)
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

async function evaluate(expression) {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text)
  return r.result?.value
}

await send('Page.enable')
await send('Runtime.enable')
await send('Network.enable')
await send('Emulation.setDeviceMetricsOverride', {
  width: 390,
  height: 844,
  deviceScaleFactor: 2,
  mobile: true,
  screenWidth: 390,
  screenHeight: 844
})
await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 })

await send('Page.navigate', { url: BASE + '/login' })
await sleep(1200)

const creds = await evaluate(`(async () => {
  const r = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: '2024413435', name: '韩涛' })
  })
  return await r.json()
})()`)
await evaluate(
  `localStorage.setItem('token', ${JSON.stringify(creds.token)});
   localStorage.setItem('user', ${JSON.stringify(JSON.stringify(creds.user))});
   localStorage.removeItem('admin_token');`
)

const pages = ['/', '/posts', '/competitions', '/post/1', '/publish', '/profile', '/messages', '/my', '/favorites']
const report = {}

for (const p of pages) {
  errors = []
  failed = []
  await send('Page.navigate', { url: BASE + p })
  await sleep(1700)
  const info = await evaluate(`(() => {
    const de = document.documentElement
    const overflow = de.scrollWidth - window.innerWidth
    const wide = []
    document.querySelectorAll('body *').forEach((el) => {
      const r = el.getBoundingClientRect()
      if (r.width > window.innerWidth + 1 && r.height > 0 && getComputedStyle(el).position !== 'fixed') {
        wide.push({ tag: el.tagName, cls: (el.className || '').toString().slice(0, 60), w: Math.round(r.width) })
      }
    })
    const tabs = document.querySelector('.m-tabbar')
    const side = document.querySelector('.sidebar')
    return {
      path: location.pathname + location.search,
      docWidth: de.scrollWidth,
      viewport: window.innerWidth,
      overflow,
      wide: wide.slice(0, 6),
      tabbarVisible: tabs ? getComputedStyle(tabs).display !== 'none' : false,
      sidebarVisible: side ? getComputedStyle(side).display !== 'none' : false,
      title: document.title
    }
  })()`)
  report[p] = { ...info, errors: errors.slice(0, 5), failed: failed.slice(0, 5) }
}

// 统计卡片列数
await send('Page.navigate', { url: BASE + '/' })
await sleep(1600)
const stats = await evaluate(`(() => {
  const cards = [...document.querySelectorAll('.home-stats .stat-card')]
  return {
    count: cards.length,
    tops: cards.map((c) => Math.round(c.getBoundingClientRect().top)),
    widths: cards.map((c) => Math.round(c.getBoundingClientRect().width)),
    gridCols: getComputedStyle(document.querySelector('.home-stats')).gridTemplateColumns
  }
})()`)

console.log(JSON.stringify({ report, stats }, null, 2))
fs.writeFileSync('.shots-mobile/probe.json', JSON.stringify({ report, stats }, null, 2))
ws.close()
