<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import AppIcon from './AppIcon.vue'
import { uploadImage } from '../api'
import { err, ok } from '../toast'
import { htmlToText } from '../utils'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '请输入详细描述…' },
  maxText: { type: Number, default: 500 }
})
const emit = defineEmits(['update:modelValue'])

const el = ref(null)
const fileInput = ref(null)
const focused = ref(false)
const uploading = ref(false)
const textLen = ref(0)
const active = ref({ bold: false, italic: false, underline: false })

const empty = computed(() => textLen.value === 0)
const over = computed(() => textLen.value > props.maxText)

function sync() {
  const html = el.value ? el.value.innerHTML : ''
  emit('update:modelValue', html)
  textLen.value = htmlToText(html).replace(/\s/g, '').length
  refreshActive()
}

function refreshActive() {
  if (!el.value || !focused.value) return
  try {
    active.value = {
      bold: document.queryCommandState('bold'),
      italic: document.queryCommandState('italic'),
      underline: document.queryCommandState('underline')
    }
  } catch (e) {
    /* 部分浏览器不支持 queryCommandState */
  }
}

function exec(cmd) {
  el.value?.focus()
  document.execCommand(cmd)
  sync()
  refreshActive()
}

function clearFormat() {
  el.value?.focus()
  document.execCommand('removeFormat')
  sync()
}

function onPaste(e) {
  e.preventDefault()
  const text = (e.clipboardData || window.clipboardData).getData('text/plain')
  document.execCommand('insertText', false, text)
  nextTick(sync)
}

async function pickImage() {
  fileInput.value?.click()
}

async function onFile(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    err('图片不能超过 2MB')
    return
  }
  uploading.value = true
  try {
    const url = await uploadImage(file)
    el.value?.focus()
    document.execCommand(
      'insertHTML',
      false,
      `<img src="${url}" alt="" style="max-width:100%;border-radius:10px;margin:6px 0">`
    )
    sync()
  } catch (e2) {
    err(e2.message || '图片上传失败')
  } finally {
    uploading.value = false
  }
}

function countText(html) {
  textLen.value = htmlToText(html).replace(/\s/g, '').length
}

onMounted(() => {
  if (el.value) el.value.innerHTML = props.modelValue || ''
  countText(props.modelValue || '')
})

watch(
  () => props.modelValue,
  (v) => {
    if (el.value && el.value.innerHTML !== (v || '')) {
      el.value.innerHTML = v || ''
      countText(v || '')
    }
  }
)

defineExpose({ focus: () => el.value?.focus() })
</script>

<template>
  <div class="editor" :class="{ focused }">
    <div class="editor-toolbar">
      <button
        type="button"
        class="tool"
        :class="{ on: active.bold }"
        title="加粗"
        @mousedown.prevent="exec('bold')"
      >
        <AppIcon name="bold" :size="15" />
      </button>
      <button
        type="button"
        class="tool"
        :class="{ on: active.italic }"
        title="斜体"
        @mousedown.prevent="exec('italic')"
      >
        <AppIcon name="italic" :size="15" />
      </button>
      <button
        type="button"
        class="tool"
        :class="{ on: active.underline }"
        title="下划线"
        @mousedown.prevent="exec('underline')"
      >
        <AppIcon name="underline" :size="15" />
      </button>
      <span class="tool-sep" />
      <button type="button" class="tool" title="插入图片" :disabled="uploading" @mousedown.prevent="pickImage">
        <AppIcon :name="uploading ? 'refresh' : 'image'" :size="15" />
      </button>
      <button type="button" class="tool" title="清除格式" @mousedown.prevent="clearFormat">
        <AppIcon name="close" :size="14" />
      </button>
      <input ref="fileInput" type="file" accept="image/*" hidden @change="onFile" />
      <span class="tool-hint">支持加粗 / 斜体 / 下划线 / 图片</span>
    </div>

    <div class="editor-shell">
      <div
        ref="el"
        class="editor-input"
        :class="{ 'is-empty': empty }"
        contenteditable="true"
        spellcheck="false"
        :data-placeholder="placeholder"
        @input="sync"
        @focus="focused = true; refreshActive()"
        @blur="focused = false"
        @keyup="refreshActive"
        @mouseup="refreshActive"
        @paste="onPaste"
      />
    </div>

    <div class="editor-foot">
      <span class="editor-tip">描述将展示在招募详情页</span>
      <span class="counter" :class="{ over }">{{ textLen }} / {{ maxText }}</span>
    </div>
  </div>
</template>

<style scoped>
.editor {
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.editor.focused {
  border-color: #b9c0da;
  box-shadow: 0 0 0 4px rgba(78, 85, 121, 0.08);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 7px 10px;
  border-bottom: 1px solid #f2f4f9;
  background: #fcfcfe;
}

.tool {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: #6d7488;
  cursor: pointer;
  transition: all 0.16s ease;
}

.tool:hover {
  background: #eef0f7;
  color: #3f465c;
}

.tool.on {
  background: var(--primary-soft);
  color: var(--primary);
}

.tool[disabled] {
  opacity: 0.5;
  cursor: wait;
}

.tool-sep {
  width: 1px;
  height: 18px;
  background: #e8eaf2;
  margin: 0 5px;
}

.tool-hint {
  margin-left: auto;
  font-size: 11px;
  color: #b0b7c6;
}

.editor-shell {
  padding: 12px 14px;
  max-height: 320px;
  overflow-y: auto;
}

.editor-input {
  display: block;
  min-height: 116px;
  height: auto;
  outline: none;
  font-size: 13.5px;
  line-height: 1.85;
  color: #333a4e;
  word-break: break-word;
}

.editor-input :deep(img) {
  max-width: 100%;
  border-radius: 10px;
  margin: 6px 0;
  display: block;
}

.editor-input.is-empty::before {
  content: attr(data-placeholder);
  color: #aab1c0;
  pointer-events: none;
}

.editor-foot {
  display: flex;
  align-items: center;
  padding: 8px 14px 10px;
  font-size: 11px;
  color: #aab1c0;
}

.counter {
  margin-left: auto;
  font-variant-numeric: tabular-nums;
}

.counter.over {
  color: var(--red);
  font-weight: 600;
}
</style>
