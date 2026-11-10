<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { TYPE_TEXT, fmtDate, gradientOf, relTime, roleLabel } from '../utils'
import { err, ok } from '../toast'
import AppIcon from '../components/AppIcon.vue'
import StatusPill from '../components/StatusPill.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageHead from '../components/PageHead.vue'

const router = useRouter()

const posts = ref([])
const loading = ref(true)
const keyword = ref('')
const tab = ref('all')
const menuFor = ref(null)
const busy = ref(false)
const dialog = ref({ show: false, action: '', post: null })

const TABS = [
  { value: 'all', label: '全部' },
  { value: 'open', label: '招募中' },
  { value: 'down', label: '已下架' },
  { value: 'full', label: '已招满' }
]

const filtered = computed(() => {
  let list = posts.value
  if (tab.value !== 'all') list = list.filter((p) => p.status === tab.value)
  const k = keyword.value.trim()
  if (k) list = list.filter((p) => p.title.includes(k) || (p.description_text || '').includes(k))
  return list
})

function countOf(status) {
  return posts.value.filter((p) => p.status === status).length
}

async function load() {
  loading.value = true
  try {
    posts.value = await api('/my/posts')
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

function ask(action, post) {
  menuFor.value = null
  dialog.value = { show: true, action, post }
}

const dialogMeta = computed(() => {
  switch (dialog.value.action) {
    case 'down':
      return { title: '下架这条招募？', text: '下架', desc: '下架后广场不再展示，你可以在“已下架”中找到它并重新发布。' }
    case 'delete':
      return { title: '删除这条招募？', text: '删除', desc: '删除后不可恢复，相关收藏也会一起移除。' }
    case 'reopen':
      return { title: '重新发布？', text: '重新发布', desc: '重新发布后，这条招募会再次出现在招募广场。' }
    default:
      return { title: '', text: '确认', desc: '' }
  }
})

async function doAction() {
  const { action, post } = dialog.value
  if (!post) return
  busy.value = true
  try {
    if (action === 'down') {
      await api(`/posts/${post.id}/down`, { method: 'POST' })
      ok('已下架')
    } else if (action === 'delete') {
      await api(`/posts/${post.id}`, { method: 'DELETE' })
      ok('已删除')
    } else if (action === 'reopen') {
      await api(`/posts/${post.id}/reopen`, { method: 'POST' })
      ok('已重新发布')
    }
    dialog.value = { show: false, action: '', post: null }
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
      :crumbs="[{ label: '首页', to: '/' }, { label: '我的发布' }]"
      title="我的发布"
      desc="管理你发布的招募信息，随时编辑、下架或重新发布"
    >
      <template #actions>
        <div class="head-search">
          <AppIcon name="search" :size="15" />
          <input v-model="keyword" placeholder="搜索我的招募…" />
        </div>
        <router-link to="/publish" class="btn btn-dark">
          <AppIcon name="plus" :size="16" />
          发布招募
        </router-link>
      </template>
    </PageHead>

    <div class="card list-card">
      <div class="list-tabs">
        <div class="tabs">
          <button
            v-for="t in TABS"
            :key="t.value"
            class="tab"
            :class="{ active: tab === t.value }"
            @click="tab = t.value"
          >
            {{ t.label }}
            <span class="tab-count">{{ t.value === 'all' ? posts.length : countOf(t.value) }}</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="list-body">
        <div v-for="i in 3" :key="i" class="post-row">
          <div class="skeleton" style="width: 104px; height: 76px; border-radius: 12px" />
          <div style="flex: 1">
            <div class="skeleton" style="height: 15px; width: 42%" />
            <div class="skeleton" style="height: 12px; width: 64%; margin-top: 12px" />
          </div>
        </div>
      </div>

      <div v-else-if="filtered.length" class="list-body">
        <div v-for="p in filtered" :key="p.id" class="post-row">
          <router-link :to="`/post/${p.id}`" class="thumb">
            <img v-if="p.image" :src="p.image" :alt="p.title" />
            <span
              v-else
              class="thumb-fallback"
              :style="{ background: `linear-gradient(140deg, ${gradientOf(p.id)[0]}, ${gradientOf(p.id)[1]})` }"
            >
              <AppIcon :name="p.type === 'team' ? 'users' : 'user'" />
            </span>
          </router-link>

          <div class="row-body">
            <router-link :to="`/post/${p.id}`" class="row-title">
              {{ p.title }}
              <StatusPill :status="p.status" />
              <span class="pill pill-accent">{{ TYPE_TEXT[p.type] }}</span>
            </router-link>
            <div v-if="p.competition || (p.roles && p.roles.length)" class="row-comp">
              <span v-if="p.competition" class="row-comp-name">
                <AppIcon name="flag" :size="11" />{{ p.competition }}
              </span>
              <span v-for="r in (p.roles || []).slice(0, 3)" :key="r" class="tag">{{ roleLabel(r) }}</span>
            </div>
            <p class="row-desc">{{ p.description_text || p.description }}</p>
            <div class="row-meta">
              <span><AppIcon name="users" :size="13" />需求 {{ p.need_num ? p.need_num + ' 人' : '不限' }}</span>
              <span><AppIcon name="calendar" :size="13" />截止 {{ p.deadline || '未设置' }}</span>
              <span><AppIcon name="clock" :size="13" />发布于 {{ fmtDate(p.created_at) }}</span>
              <span><AppIcon name="eye" :size="13" />{{ p.views }} 次浏览</span>
            </div>
          </div>

          <div class="row-actions">
            <router-link v-if="p.status === 'open'" :to="`/post/${p.id}/edit`" class="btn btn-ghost btn-xs">
              <AppIcon name="edit" :size="13" />编辑
            </router-link>
            <button
              v-if="p.status === 'open'"
              class="btn btn-danger-soft btn-xs"
              @click="ask('down', p)"
            >
              下架
            </button>
            <button
              v-if="p.status === 'down'"
              class="btn btn-ghost btn-xs"
              @click="ask('reopen', p)"
            >
              <AppIcon name="refresh" :size="13" />重新发布
            </button>
            <router-link v-if="p.status === 'full'" :to="`/post/${p.id}`" class="btn btn-ghost btn-xs">
              查看详情
            </router-link>

            <div class="menu-wrap">
              <button class="icon-mini" @click="menuFor = menuFor === p.id ? null : p.id">
                <AppIcon name="more" :size="16" />
              </button>
              <div v-if="menuFor === p.id" class="menu">
                <button @click="router.push(`/post/${p.id}`); menuFor = null">
                  <AppIcon name="eye" />查看详情
                </button>
                <button v-if="p.status === 'open'" @click="router.push(`/post/${p.id}/edit`); menuFor = null">
                  <AppIcon name="edit" />编辑内容
                </button>
                <button v-if="p.status !== 'down'" class="danger" @click="ask('delete', p)">
                  <AppIcon name="trash" />删除招募
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="list-body">
        <div class="empty">
          <div class="empty-art"><AppIcon name="megaphone" :size="34" /></div>
          <div class="empty-title">{{ posts.length ? '这个分类下还没有招募' : '你还没有发布过招募' }}</div>
          <p class="empty-desc">发布一条招募，让正在找队友的同学看到你</p>
          <router-link to="/publish" class="btn btn-primary btn-sm" style="margin-top: 6px">发布招募</router-link>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="dialog.show"
      :title="dialogMeta.title"
      :desc="dialogMeta.desc"
      :confirm-text="dialogMeta.text"
      :danger="dialog.action !== 'reopen'"
      :loading="busy"
      @cancel="dialog = { show: false, action: '', post: null }"
      @confirm="doAction"
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
  transition: all 0.18s ease;
}

.head-search input:focus {
  border-color: #b9c0da;
  box-shadow: 0 0 0 4px rgba(78, 85, 121, 0.07);
}

.list-card {
  overflow: visible;
}

.list-tabs {
  padding: 0 20px;
}

.list-body {
  padding: 4px 20px 8px;
}

.icon-mini {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #9aa1b2;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.icon-mini:hover {
  background: #f2f3f9;
  color: #4d5468;
}

@media (max-width: 720px) {
  .head-search {
    width: 100%;
  }
}
</style>
