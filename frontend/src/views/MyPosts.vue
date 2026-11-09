<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { toast } from '../toast'
import { STATUS_TEXT, TYPE_TEXT, relTime } from '../utils'

const posts = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    posts.value = await api('/my/posts')
  } catch (e) {
    toast(e.message, 'err')
  } finally {
    loading.value = false
  }
}

async function onClose(p) {
  if (!confirm('确认关闭该招募？关闭后状态将变为“已招满”。')) return
  try {
    await api('/posts/' + p.id + '/close', { method: 'POST' })
    toast('已关闭招募')
    load()
  } catch (e) {
    toast(e.message, 'err')
  }
}

async function onDelete(p) {
  if (!confirm('删除后不可恢复，确认删除？')) return
  try {
    await api('/posts/' + p.id, { method: 'DELETE' })
    toast('已删除')
    load()
  } catch (e) {
    toast(e.message, 'err')
  }
}

onMounted(load)
</script>

<template>
  <div class="container" style="padding-top: 40px">
    <h2 style="margin: 0 0 20px; font-size: 24px; font-weight: 500">我的发布</h2>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!posts.length" class="empty">
      你还没有发布过招募信息
      <div style="margin-top: 12px">
        <router-link to="/publish" class="btn sm">去发布</router-link>
      </div>
    </div>

    <div v-for="p in posts" :key="p.id" class="card post-item">
      <div class="title-row" style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap">
        <span class="tag" :class="p.type">{{ TYPE_TEXT[p.type] }}</span>
        <router-link :to="'/post/' + p.id" style="font-weight: 500">
          {{ p.title }}
        </router-link>
        <span class="tag" :class="p.status">{{ STATUS_TEXT[p.status] }}</span>
      </div>
      <div style="color: var(--sub); font-size: 13px; margin: 8px 0">
        {{ p.description.slice(0, 60) }}{{ p.description.length > 60 ? '…' : '' }}
      </div>
      <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap">
        <span class="meta" style="color: var(--sub); font-size: 12px; margin-right: auto">
          {{ relTime(p.created_at) }}
          <template v-if="p.status === 'down'"> · 如对下架有疑问，请联系管理员</template>
        </span>
        <button v-if="p.status === 'open'" class="btn sm plain" @click="onClose(p)">
          关闭招募（已招满）
        </button>
        <button
          v-if="p.status === 'open' || p.status === 'full'"
          class="btn sm danger"
          @click="onDelete(p)"
        >
          删除
        </button>
      </div>
    </div>
  </div>
</template>
