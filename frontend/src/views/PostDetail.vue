<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'
import { toast } from '../toast'
import { STATUS_TEXT, TYPE_TEXT, CONTACT_TEXT, copyText, relTime } from '../utils'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(true)
const notFound = ref(false)

async function load() {
  try {
    post.value = await api('/posts/' + route.params.id)
  } catch (e) {
    if (e.status === 404) notFound.value = true
    else toast(e.message, 'err')
  } finally {
    loading.value = false
  }
}

async function onCopy() {
  const ok = await copyText(post.value.contact)
  toast(ok ? '已复制到剪贴板' : '复制失败，请手动复制', ok ? 'ok' : 'err')
}

function goLogin() {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

async function toggleFav() {
  if (!auth.user) {
    goLogin()
    return
  }
  try {
    if (post.value.is_favorite) {
      await api('/posts/' + post.value.id + '/favorite', { method: 'DELETE' })
      post.value.is_favorite = false
      toast('已取消收藏')
    } else {
      await api('/posts/' + post.value.id + '/favorite', { method: 'POST' })
      post.value.is_favorite = true
      toast('已收藏')
    }
  } catch (e) {
    toast(e.message, 'err')
  }
}

onMounted(load)
</script>

<template>
  <div class="container" style="padding-top: 40px">
    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="notFound" class="empty">
      <svg viewBox="0 0 64 64" width="72" height="72" fill="none" stroke="#c9ccd4" stroke-width="2">
        <circle cx="32" cy="32" r="22" />
        <path d="M24 26l16 12M40 26L24 38" />
      </svg>
      <div style="margin-top: 10px">帖子不存在或已被下架</div>
    </div>

    <div v-else class="card detail-card">
      <div class="banner warn" v-if="post.status === 'full'">该招募已完成，仅供参考</div>
      <div class="title-row" style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap">
        <span class="row-id">#{{ String(post.id).padStart(3, '0') }}</span>
        <span class="tag" :class="post.type">{{ TYPE_TEXT[post.type] }}</span>
        <h2 style="margin: 0; font-size: 28px; font-weight: 500; line-height: 1.35">{{ post.title }}</h2>
        <span class="tag" :class="post.status">{{ STATUS_TEXT[post.status] }}</span>
        <button class="star-btn inline" :class="{ active: post.is_favorite }" @click="toggleFav">
          <svg viewBox="0 0 24 24" width="17" height="17" :fill="post.is_favorite ? 'currentColor' : 'none'"
            stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          {{ post.is_favorite ? '已收藏' : '收藏' }}
        </button>
      </div>

      <div class="meta" style="color: var(--sub); font-size: 13px; margin-top: 8px">
        {{ post.author_name }} · {{ relTime(post.created_at) }} ·
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
          style="vertical-align: -2px">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
        {{ post.views }} 次浏览
      </div>

      <div class="detail-grid">
        <div class="row"><span class="k">描述</span><span style="white-space: pre-wrap">{{ post.description }}</span>
        </div>
        <div class="row" v-if="post.need_num"><span class="k">需求人数</span><span>{{ post.need_num }} 人</span></div>
      </div>

      <div class="contact-box" v-if="post.contact">
        <div>
          <div class="contact-label">联系方式（{{ CONTACT_TEXT[post.contact_type] || '联系方式' }}）</div>
          <div class="num">{{ post.contact }}</div>
        </div>
        <button class="btn sm" style="margin-left: auto" @click="onCopy">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          一键复制
        </button>
      </div>
      <div class="contact-box masked" v-else>
        <div>
          <div class="contact-label">联系方式</div>
          <div class="num" style="color: var(--sub); font-size: 15px">
            {{ CONTACT_TEXT[post.contact_type] || '微信 / QQ / 手机号' }}：登录后可见
          </div>
        </div>
        <button class="btn sm ghost" style="margin-left: auto" @click="goLogin">登录后可查看联系方式</button>
      </div>
    </div>

    <div style="margin-top: 16px">
      <router-link to="/" class="btn plain sm">返回列表</router-link>
    </div>
  </div>
</template>
