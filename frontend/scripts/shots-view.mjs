// 视口截图（非整页），便于逐屏核对视觉细节
// 用法：node scripts/shots-view.mjs
import fs from 'node:fs'
import path from 'node:path'

const OUT = '.shots-view'
const BASE = 'http://localhost:5173'
const CDP = 'http://127.0.0.1:9222'
fs.mkdirSync(OUT, { recursive: true })
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const list = await (await fetch(CDP + '/json/list')).json()
const page = list.find((t) => t.type === 'page')
const ws = new WebSocket(page.webSocketDebuggerUrl)
let seq = 0
const pending = new Map()
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data)
  if (m.id && pending.has(m.id)) {
    const { resolve, reject } = pending.get(m.id)
    pending.delete(m.id)
    m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result)
  }
})
await new Promise((res) => ws.addEventListener('open', res, { once: true }))
const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const id = ++seq
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })
  return r.result?.value
}

await send('Page.enable')
await send('Runtime.enable')
await send('Emulation.setDeviceMetricsOverride', {
  width: 390, height: 844, deviceScaleFactor: 2, mobile: true, screenWidth: 390, screenHeight: 844
})

await send('Page.navigate', { url: BASE + '/login' })
await sleep(1200)
const creds = await evaluate(`(async () => {
  const r = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: '2024413435', name: '韩涛' }) })
  return await r.json()
})()`)
await evaluate(`localStorage.setItem('token', ${JSON.stringify(creds.token)});
  localStorage.setItem('user', ${JSON.stringify(JSON.stringify(creds.user))});`)

async function shot(name, url, opts = {}) {
  await send('Page.navigate', { url: BASE + url })
  await sleep(opts.wait || 1500)
  if (opts.scroll) await evaluate(`window.scrollTo(0, ${opts.scroll})`)
  if (opts.click) {
    await evaluate(opts.click)
    await sleep(600)
  }
  const { data } = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync(path.join(OUT, name + '.png'), Buffer.from(data, 'base64'))
  console.log('saved', name)
}

const clickFilter = `(() => {
  const b = [...document.querySelectorAll('button')].find((x) => x.textContent.trim().startsWith('筛选'))
  b && b.click()
})()`

await shot('v-home-top', '/')
await shot('v-posts', '/posts')
await shot('v-filter', '/posts', { click: clickFilter })
await shot('v-detail-top', '/post/1')
await shot('v-profile', '/profile')
await shot('v-messages', '/messages')
await shot('v-publish-top', '/publish')
ws.close()
