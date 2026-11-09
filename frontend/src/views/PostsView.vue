<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'
import { TYPE_TEXT } from '../utils'
import PageHead from '../components/PageHead.vue'
import PostCard from '../components/PostCard.vue'
import AppIcon from '../components/AppIcon.vue'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const loading = ref(true)
const type = ref('')
const keyword = ref('')
const failed = ref(false)

const TYPES = [
  { value: '', label: '全部招募' },
  { value: 'team', label: '找队友' },
  { value: 'join', label: '找队伍' }
]

const counts = computed(() => {
  const c = { '': posts.value.length, team: 0, join: 0 }
  posts.value.forEach((p) => {
    c[p.type] = (c[p.type] || 0) + 1
  })
  return c
})

const shown = computed(() => (type.value ? posts.value.filter((p) => p.type === type.value) : posts.value))

async function load() {
  loading.value = true
  failed.value = false
  try {
    const q = route.query.q || ''
    keyword.value = String(q)
    const data = await api('/posts' + (q ? '?q=' + encodeURIComponent(q) : ''))
    posts.value = data
  } catch (e) {
    failed.value = true
  } finally {
    loading.value = false
  }
}

function setType(v) {
  type.value = v
}

onMounted(load)
watch(() => route.query.q, load)
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '首页', to: '/' }, { label: '招募广场' }]"
      title="招募广场"
      desc="浏览全校正在寻找队友的招募信息，找到你的下一个比赛搭档"
    >
      <template #actions>
        <router-link v-if="auth.user" to="/publish" class="btn btn-primary">
          <AppIcon name="plus" :size="16" />
          发布招募
        </router-link>
      </template>
    </PageHead>

    <div class="board">
      <div class="board-bar">
        <div class="chip-row">
          <button
            v-for="t in TYPES"
            :key="t.value"
            class="chip"
            :class="{ active: type === t.value }"
            @click="setType(t.value)"
          >
            {{ t.label }}
            <span class="chip-count">{{ counts[t.value] || 0 }}</span>
          </button>
        </div>

        <div v-if="keyword" class="search-tip">
          搜索 “{{ keyword }}”
          <button class="link-btn" @click="router.push('/posts')">清除</button>
        </div>
      </div>

      <div v-if="loading" class="post-grid">
        <div v-for="i in 6" :key="i" class="card skeleton-card">
          <div class="skeleton" style="width: 66px; height: 66px; border-radius: 14px" />
          <div style="flex: 1">
            <div class="skeleton" style="height: 14px; width: 72%" />
            <div class="skeleton" style="height: 12px; width: 44%; margin-top: 10px" />
          </div>
        </div>
      </div>

      <div v-else-if="failed" class="card">
        <div class="empty">
          <div class="empty-art"><AppIcon name="alert" :size="34" /></div>
          <div class="empty-title">加载失败</div>
          <p class="empty-desc">请确认后端服务已启动，然后重试</p>
          <button class="btn btn-ghost btn-sm" style="margin-top: 6px" @click="load">重新加载</button>
        </div>
      </div>

      <div v-else-if="shown.length" class="post-grid">
        <PostCard v-for="p in shown" :key="p.id" :post="p" />
      </div>

      <div v-else class="card">
        <div class="empty">
          <div class="empty-art"><AppIcon name="search" :size="34" /></div>
          <div class="empty-title">没有找到相关招募</div>
          <p class="empty-desc">换个关键词试试，或者成为第一个发布的人</p>
          <router-link v-if="auth.user" to="/publish" class="btn btn-primary btn-sm" style="margin-top: 6px">
            发布招募
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.board {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.board-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.chip-count {
  font-size: 11px;
  font-weight: 600;
  padding: 0 6px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.05);
  margin-left: 2px;
}

.chip.active .chip-count {
  background: rgba(255, 255, 255, 0.2);
}

.search-tip {
  margin-left: auto;
  font-size: 12.5px;
  color: var(--text-3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.skeleton-card {
  display: flex;
  gap: 13px;
  padding: 18px;
  align-items: flex-start;
}

@media (max-width: 1100px) {
  .post-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .post-grid {
    grid-template-columns: 1fr;
  }
}
</style>
