<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'
import { toast } from '../toast'
import { STATUS_TEXT, TYPE_TEXT, isNew, relTime } from '../utils'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const loading = ref(true)
const typeFilter = ref('all')
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (typeFilter.value !== 'all') params.set('type', typeFilter.value)
    if (keyword.value.trim()) params.set('q', keyword.value.trim())
    posts.value = await api('/posts?' + params.toString())
  } catch (e) {
    toast(e.message, 'err')
  } finally {
    loading.value = false
  }
}

async function toggleFav(p) {
  if (!auth.user) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  try {
    if (p.is_favorite) {
      await api('/posts/' + p.id + '/favorite', { method: 'DELETE' })
      p.is_favorite = false
      toast('已取消收藏')
    } else {
      await api('/posts/' + p.id + '/favorite', { method: 'POST' })
      p.is_favorite = true
      toast('已收藏')
    }
  } catch (e) {
    toast(e.message, 'err')
  }
}

watch(typeFilter, load)
onMounted(load)
</script>

<template>
  <div class="container">
    <div class="hero">
      <div class="hero-copy">
        <div class="hero-kicker">校内比赛组队</div>
        <h1>找到能一起上场的人</h1>
        <p>发布赛事、缺什么角色和联系方式。30 天内有效，登录后即可查看联系方式。</p>
        <div class="hero-actions">
          <router-link to="/publish" class="btn">发布招募</router-link>
          <a class="btn ghost" href="#list">浏览正在招募</a>
        </div>
        <div class="hero-notes">
          <span>学号 + 姓名注册</span>
          <span>联系方式登录可见</span>
        </div>
      </div>
      <div class="hero-board" aria-hidden="true">
        <div class="board-head">
          <b><span class="board-dot"></span>招募板</b>
          <span>3 条招募中</span>
        </div>
        <div class="board-item">
          <span class="board-id">#104</span>
          <div>
            <div class="board-title">全国大学生数学建模竞赛</div>
            <div class="board-meta">
              <span class="board-role">找队友 · 缺 1 人</span>
              <span>数据处理</span>
              <span class="board-status">招募中</span>
            </div>
          </div>
        </div>
        <div class="board-item">
          <span class="board-id">#098</span>
          <div>
            <div class="board-title">互联网+创新创业大赛</div>
            <div class="board-meta">
              <span class="board-role">找队伍</span>
              <span>前端方向</span>
              <span class="board-status">招募中</span>
            </div>
          </div>
        </div>
        <div class="board-item">
          <span class="board-id">#091</span>
          <div>
            <div class="board-title">电子设计竞赛</div>
            <div class="board-meta">
              <span class="board-role">找队友 · 缺 2 人</span>
              <span>嵌入式</span>
              <span class="board-status">招募中</span>
            </div>
          </div>
        </div>
        <div class="board-foot">
          <span>联系方式仅登录用户可见</span>
          <span>30 天有效</span>
        </div>
      </div>
    </div>

    <div id="list" class="section-head">
      <h2>正在招募</h2>
      <span class="count" v-if="!loading">共 {{ posts.length }} 条</span>
    </div>

    <div class="toolbar">
      <div class="tabs">
        <button :class="{ active: typeFilter === 'all' }" @click="typeFilter = 'all'">全部</button>
        <button :class="{ active: typeFilter === 'team' }" @click="typeFilter = 'team'">找队友</button>
        <button :class="{ active: typeFilter === 'join' }" @click="typeFilter = 'join'">找队伍</button>
      </div>
      <div class="search-box">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
        </svg>
        <input v-model="keyword" placeholder="搜索赛事名称 / 描述" @keyup.enter="load" />
        <button class="search-submit" @click="load">搜索</button>
      </div>
    </div>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!posts.length" class="empty">
      <svg viewBox="0 0 64 64" width="72" height="72" fill="none" stroke="#c9ccd4" stroke-width="2">
        <rect x="10" y="14" width="44" height="34" rx="4" />
        <path d="M10 24h44" /><circle cx="17" cy="19" r="1.5" /><circle cx="23" cy="19" r="1.5" />
        <path d="M22 34h20M22 40h12" />
      </svg>
      <div style="margin-top: 10px">暂无招募信息，来发布第一条吧</div>
      <div style="margin-top: 12px">
        <router-link to="/publish" class="btn sm">去发布</router-link>
      </div>
    </div>

    <div v-else class="post-list">
      <div v-for="p in posts" :key="p.id" class="post-card">
        <button
          class="star-btn"
          :class="{ active: p.is_favorite }"
          :title="p.is_favorite ? '取消收藏' : '收藏'"
          @click.stop="toggleFav(p)"
        >
          <svg viewBox="0 0 24 24" width="17" height="17" :fill="p.is_favorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </button>
        <router-link :to="'/post/' + p.id" class="post-body">
          <div class="title-row">
            <span class="row-id">#{{ String(p.id).padStart(3, '0') }}</span>
            <span class="tag" :class="p.type">{{ TYPE_TEXT[p.type] }}</span>
            <h3>{{ p.title }}</h3>
            <span v-if="isNew(p.created_at)" class="tag new">新</span>
            <span class="tag" :class="p.status">{{ STATUS_TEXT[p.status] }}</span>
          </div>
          <div class="desc">{{ p.description.slice(0, 40) }}{{ p.description.length > 40 ? '…' : '' }}</div>
          <div class="meta">
            <span>{{ p.author_name }}</span>
            <span class="dot">·</span>
            <span>{{ relTime(p.created_at) }}</span>
            <span class="dot">·</span>
            <span class="views">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
              </svg>
              {{ p.views }}
            </span>
            <template v-if="p.need_num">
              <span class="dot">·</span>
              <span>需 {{ p.need_num }} 人</span>
            </template>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>
