import { reactive } from 'vue'

export const toastState = reactive({ show: false, text: '', type: 'ok', key: 0 })

let timer = null
export function toast(text, type = 'ok') {
  toastState.show = true
  toastState.text = text
  toastState.type = type
  toastState.key++
  clearTimeout(timer)
  timer = setTimeout(() => {
    toastState.show = false
  }, 2600)
}

export const ok = (t) => toast(t, 'ok')
export const err = (t) => toast(t, 'err')
