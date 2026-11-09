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
    posts.value = await api('/my/favorites')
  } catch (e) {
    toast(e.message, 'err')
  } finally {
    loading.value = false
  }
}

async function unfav(p) {
  try {
    await api('/posts/' + p.id + '/favorite', { method: 'DELETE' })
    toast('已取消收藏')
    load()
  } catch (e) {
    toast(e.message, 'err')
  }
}

onMounted(load)
</script>

<template>
  <div class="container" style="padding-top: 40px">
    <h2 style="margin: 0 0 20px; font-size: 24px; font-weight: 500">我的收藏</h2>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!posts.length" class="empty">
      <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="#c9ccd4" stroke-width="1.5">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
      <div style="margin-top: 10px">还没有收藏任何帖子</div>
      <div style="margin-top: 12px">
        <router-link to="/" class="btn sm">去逛逛</router-link>
      </div>
    </div>

    <div v-else class="post-list">
      <div v-for="p in posts" :key="p.id" class="post-card">
        <button class="star-btn active" title="取消收藏" @click.stop="unfav(p)">
          <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </button>
        <router-link :to="'/post/' + p.id" class="post-body">
          <div class="title-row">
            <span class="row-id">#{{ String(p.id).padStart(3, '0') }}</span>
            <span class="tag" :class="p.type">{{ TYPE_TEXT[p.type] }}</span>
            <h3>{{ p.title }}</h3>
            <span class="tag" :class="p.status">{{ STATUS_TEXT[p.status] }}</span>
          </div>
          <div class="desc">{{ p.description.slice(0, 40) }}{{ p.description.length > 40 ? '…' : '' }}</div>
          <div class="meta">
            <span>{{ p.author_name }}</span>
            <span class="dot">·</span>
            <span>{{ relTime(p.created_at) }}</span>
            <span class="dot">·</span>
            <span>{{ p.views }} 次浏览</span>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>
