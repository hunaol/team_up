<script setup>
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '../../api'
import { TYPE_TEXT, fmtDate, gradientOf, relTime } from '../../utils'
import { err, ok } from '../../toast'
import AppIcon from '../../components/AppIcon.vue'
import PageHead from '../../components/PageHead.vue'
import StatusPill from '../../components/StatusPill.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'

const posts = ref([])
const loading = ref(true)
const keyword = ref('')
const type = ref('')
const status = ref('')
const busy = ref(false)
const dialog = ref({ show: false, post: null })

const TYPES = [
  { value: '', label: '全部类型' },
  { value: 'team', label: '找队友' },
  { value: 'join', label: '找队伍' }
]

const STATUSES = [
  { value: '', label: '全部状态' },
  { value: 'open', label: '招募中' },
  { value: 'full', label: '已招满' },
  { value: 'down', label: '已下架' },
  { value: 'expired', label: '已过期' }
]

const shown = computed(() => {
  const k = keyword.value.trim()
  if (!k) return posts.value
  return posts.value.filter(
    (p) => p.title.includes(k) || p.author_name.includes(k) || (p.description_text || '').includes(k)
  )
})

async function load() {
  loading.value = true
  try {
    const qs = new URLSearchParams()
    if (type.value) qs.set('type', type.value)
    if (status.value) qs.set('status', status.value)
    const q = qs.toString()
    posts.value = await adminApi('/admin/posts' + (q ? '?' + q : ''))
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

async function takedown() {
  const p = dialog.value.post
  if (!p) return
  busy.value = true
  try {
    await adminApi(`/admin/posts/${p.id}/takedown`, { method: 'POST' })
    ok('已下架该招募')
    dialog.value = { show: false, post: null }
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '管理后台', to: '/admin' }, { label: '帖子管理' }]"
      title="帖子管理"
      desc="查看平台全部招募内容，发现违规信息可直接下架"
    >
      <template #actions>
        <div class="head-search">
          <AppIcon name="search" :size="15" />
          <input v-model="keyword" placeholder="搜索标题 / 发布者…" />
        </div>
        <select v-model="type" class="select filter-select" @change="load">
          <option v-for="t in TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
        <select v-model="status" class="select filter-select" @change="load">
          <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </template>
    </PageHead>

    <div class="card list-card">
      <div class="list-head">
        <span class="list-count">共 {{ shown.length }} 条招募</span>
      </div>

      <div v-if="loading" class="list-body">
        <div v-for="i in 4" :key="i" class="post-row">
          <div class="skeleton" style="width: 92px; height: 68px; border-radius: 12px" />
          <div style="flex: 1">
            <div class="skeleton" style="height: 15px; width: 38%" />
            <div class="skeleton" style="height: 12px; width: 62%; margin-top: 12px" />
          </div>
        </div>
      </div>

      <div v-else-if="shown.length" class="list-body">
        <div v-for="p in shown" :key="p.id" class="post-row">
          <router-link :to="`/post/${p.id}`" class="thumb">
            <img v-if="p.image" :src="p.image" :alt="p.title" />
            <span
              v-else
              class="thumb-fallback"
              :style="{ background: `linear-gradient(140deg, ${gradientOf(p.id + p.title)[0]}, ${gradientOf(p.id + p.title)[1]})` }"
            >
              <AppIcon name="building" />
            </span>
          </router-link>

          <div class="row-body">
            <router-link :to="`/post/${p.id}`" class="row-title">
              {{ p.title }}
              <StatusPill :status="p.status" />
              <span class="pill pill-accent">{{ TYPE_TEXT[p.type] }}</span>
            </router-link>
            <p class="row-desc">{{ p.description_text || p.description }}</p>
            <div class="row-meta">
              <span><AppIcon name="user" :size="13" />{{ p.author_name }}</span>
              <span><AppIcon name="users" :size="13" />需求 {{ p.need_num ? p.need_num + ' 人' : '不限' }}</span>
              <span><AppIcon name="eye" :size="13" />{{ p.views }} 次浏览</span>
              <span><AppIcon name="clock" :size="13" />{{ relTime(p.created_at) }}</span>
            </div>
          </div>

          <div class="row-actions">
            <router-link :to="`/post/${p.id}`" class="btn btn-ghost btn-xs">查看</router-link>
            <button
              v-if="p.status === 'open' || p.status === 'full'"
              class="btn btn-danger-soft btn-xs"
              @click="dialog = { show: true, post: p }"
            >
              下架
            </button>
            <span v-else class="row-note">{{ p.status === 'expired' ? '已自动过期' : '已下架' }}</span>
          </div>
        </div>
      </div>

      <div v-else class="list-body">
        <div class="empty">
          <div class="empty-art"><AppIcon name="list" :size="32" /></div>
          <div class="empty-title">没有符合条件的招募</div>
          <p class="empty-desc">调整筛选条件或搜索关键词后再试</p>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="dialog.show"
      title="下架这条招募？"
      :desc="`「${dialog.post?.title || ''}」下架后将不再展示在广场，发布者可重新发布。`"
      confirm-text="确认下架"
      danger
      :loading="busy"
      @cancel="dialog = { show: false, post: null }"
      @confirm="takedown"
    />
  </div>
</template>

<style scoped>
.head-search {
  position: relative;
  display: flex;
  align-items: center;
  width: 220px;
}

.head-search svg {
  position: absolute;
  left: 12px;
  color: #a3aaba;
  pointer-events: none;
}

.head-search input {
  width: 100%;
  height: 42px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: #fff;
  padding: 0 12px 0 36px;
  font-size: 13px;
  font-family: inherit;
  outline: none;
}

.filter-select {
  width: 122px;
  height: 42px;
}

.list-head {
  padding: 14px 20px;
  border-bottom: 1px solid #f4f5f9;
}

.list-count {
  font-size: 12px;
  color: #9aa1b2;
}

.list-body {
  padding: 4px 20px 8px;
}

.row-note {
  font-size: 11.5px;
  color: #b0b7c6;
}

@media (max-width: 720px) {
  .head-search {
    width: 100%;
  }
}
</style>
