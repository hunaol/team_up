// 开发期探针：在 headless Chrome 里打开某个页面并执行一段 JS，打印结果
// 用法：node scripts/probe.mjs /publish "document.querySelector('.editor').getBoundingClientRect().height"
import { setTimeout as sleep } from 'node:timers/promises'

const BASE = 'http://localhost:5173'
const CDP = 'http://127.0.0.1:9222'
const path = process.argv[2] || '/'
const expr = process.argv[3] || 'document.title'

const list = await (await fetch(CDP + '/json/list')).json()
const page = list.find((t) => t.type === 'page')
const ws = new WebSocket(page.webSocketDebuggerUrl)
let seq = 0
const pending = new Map()
const events = []

ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data)
  if (msg.id && pending.has(msg.id)) {
    const p = pending.get(msg.id)
    pending.delete(msg.id)
    msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result)
  } else if (msg.method) events.push(msg.method)
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

await send('Page.enable')
await send('Runtime.enable')
await send('Emulation.setDeviceMetricsOverride', {
  width: 1440,
  height: 900,
  deviceScaleFactor: 1,
  mobile: false
})
events.length = 0
await send('Page.navigate', { url: BASE + path })
for (let i = 0; i < 60; i++) {
  if (events.includes('Page.loadEventFired')) break
  await sleep(100)
}
await sleep(1500)
const r = await send('Runtime.evaluate', {
  expression: `(() => { ${expr} })()`,
  awaitPromise: true,
  returnByValue: true
})
console.log(JSON.stringify(r.result?.value ?? r, null, 2))
ws.close()
