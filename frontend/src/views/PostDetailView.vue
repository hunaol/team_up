<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'
import { CONTACT_TEXT, TYPE_TEXT, copyText, daysLeft, descToHtml, fmtDate, gradientOf } from '../utils'
import { err, ok } from '../toast'
import AppIcon from '../components/AppIcon.vue'
import StatusPill from '../components/StatusPill.vue'
import UserAvatar from '../components/UserAvatar.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageHead from '../components/PageHead.vue'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(true)
const notFound = ref(false)
const reveal = ref(false)
const busy = ref(false)
const dialog = ref({ show: false, action: '' })

const isOwner = computed(
  () => !!post.value && !!auth.user && post.value.author_name === auth.user.name
)
const grad = computed(() => gradientOf((post.value?.id || 0) + (post.value?.title || '')))
const left = computed(() => daysLeft(post.value?.deadline))

async function load() {
  loading.value = true
  notFound.value = false
  try {
    post.value = await api('/posts/' + route.params.id)
  } catch (e) {
    if (e.status === 404) notFound.value = true
    else err(e.message)
  } finally {
    loading.value = false
  }
}

async function toggleFavorite() {
  if (!auth.user) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  if (busy.value) return
  busy.value = true
  try {
    if (post.value.is_favorite) {
      await api(`/posts/${post.value.id}/favorite`, { method: 'DELETE' })
      post.value.is_favorite = false
      ok('已取消收藏')
    } else {
      await api(`/posts/${post.value.id}/favorite`, { method: 'POST' })
      post.value.is_favorite = true
      ok('已加入收藏')
    }
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

async function doAction(action) {
  busy.value = true
  try {
    if (action === 'down') {
      await api(`/posts/${post.value.id}/down`, { method: 'POST' })
      ok('已下架该招募')
    } else if (action === 'close') {
      await api(`/posts/${post.value.id}/close`, { method: 'POST' })
      ok('已标记为招满')
    } else if (action === 'delete') {
      await api(`/posts/${post.value.id}`, { method: 'DELETE' })
      ok('已删除')
      router.push('/my')
      return
    }
    dialog.value = { show: false, action: '' }
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

async function copyContact() {
  if (!post.value?.contact) return
  const done = await copyText(post.value.contact)
  done ? ok('联系方式已复制') : err('复制失败，请手动选择')
}

function ask(action) {
  dialog.value = { show: true, action }
}

const dialogMeta = computed(() => {
  switch (dialog.value.action) {
    case 'down':
      return { title: '下架这条招募？', desc: '下架后其他同学将无法在广场看到它，你可以随时重新发布。', text: '下架' }
    case 'close':
      return { title: '标记为已招满？', desc: '招募广场将显示“已招满”，不再接受新的联系。', text: '标记招满' }
    case 'delete':
      return { title: '删除这条招募？', desc: '删除后不可恢复，相关的收藏也会一并移除。', text: '删除' }
    default:
      return { title: '', desc: '', text: '确认' }
  }
})

onMounted(load)
</script>

<template>
  <div>
    <PageHead :crumbs="[{ label: '首页', to: '/' }, { label: '招募广场', to: '/posts' }, { label: '招募详情' }]" title="招募详情" />

    <div v-if="loading" class="card card-pad">
      <div class="skeleton" style="height: 24px; width: 40%" />
      <div class="skeleton" style="height: 14px; width: 62%; margin-top: 16px" />
      <div class="skeleton" style="height: 14px; width: 52%; margin-top: 10px" />
      <div class="skeleton" style="height: 160px; width: 100%; margin-top: 22px" />
    </div>

    <div v-else-if="notFound" class="card">
      <div class="empty">
        <div class="empty-art"><AppIcon name="alert" :size="34" /></div>
        <div class="empty-title">这条招募不存在或已下架</div>
        <p class="empty-desc">它可能已被发布者删除，或超过了 30 天有效期</p>
        <router-link to="/posts" class="btn btn-primary btn-sm" style="margin-top: 6px">返回招募广场</router-link>
      </div>
    </div>

    <div v-else-if="post" class="detail">
      <article class="card detail-main">
        <div class="detail-head">
          <div class="detail-badges">
            <span class="pill pill-accent">{{ TYPE_TEXT[post.type] }}</span>
            <StatusPill :status="post.status" />
            <span v-if="post.need_num" class="pill pill-neutral">
              <AppIcon name="users" :size="12" />需要 {{ post.need_num }} 人
            </span>
          </div>
          <h1 class="detail-title">{{ post.title }}</h1>
          <div class="detail-meta">
            <span><AppIcon name="user" :size="13" />{{ post.author_name }}</span>
            <span><AppIcon name="clock" :size="13" />发布于 {{ fmtDate(post.created_at) }}</span>
            <span><AppIcon name="eye" :size="13" />{{ post.views }} 次浏览</span>
            <span v-if="post.deadline"><AppIcon name="calendar" :size="13" />截止 {{ post.deadline }}</span>
          </div>
        </div>

        <div v-if="post.deadline" class="countdown" :class="{ warn: left !== null && left <= 3 }">
          <AppIcon name="clock" :size="15" />
          <template v-if="left === null || left > 0">距离截止还有 <b>{{ left }}</b> 天，感兴趣就尽快联系吧</template>
          <template v-else>该招募的截止日期已过</template>
        </div>

        <div v-if="post.image" class="detail-cover">
          <img :src="post.image" :alt="post.title" />
        </div>
        <div
          v-else
          class="detail-cover detail-cover-fallback"
          :style="{ background: `linear-gradient(140deg, ${grad[0]}, ${grad[1]})` }"
        >
          <AppIcon name="building" :size="34" />
        </div>

        <div class="detail-body">
          <h2 class="detail-subtitle">招募说明</h2>
          <div class="rich" v-html="descToHtml(post.description)"></div>
        </div>
      </article>

      <aside class="detail-aside">
        <section class="card aside-card">
          <div class="aside-head">
            <UserAvatar :name="post.author_name" :size="42" />
            <div>
              <div class="aside-title">{{ post.author_name }}</div>
              <div class="aside-sub">发布者 · 校园认证用户</div>
            </div>
          </div>
          <div class="aside-meta">
            <span>发布于 {{ fmtDate(post.created_at) }}</span>
            <span>{{ post.views }} 次浏览</span>
          </div>
          <p class="aside-note">联系方式仅登录用户可见，请文明沟通。</p>
        </section>

        <section class="card aside-card contact-card">
          <div class="aside-label">{{ CONTACT_TEXT[post.contact_type] }}</div>
          <div v-if="post.contact" class="contact-value">
            <span class="contact-text">{{ reveal ? post.contact : '•'.repeat(Math.min(post.contact.length, 11)) }}</span>
            <button class="btn btn-ghost btn-xs" @click="reveal = !reveal">
              <AppIcon :name="reveal ? 'eye' : 'lock'" :size="13" />
              {{ reveal ? '隐藏' : '显示' }}
            </button>
          </div>
          <div v-else class="contact-locked">
            <AppIcon name="lock" :size="15" />
            <span>登录后可查看联系方式</span>
          </div>

          <button class="btn btn-primary btn-block" style="margin-top: 14px" :disabled="!post.contact" @click="copyContact">
            <AppIcon name="link" :size="15" />
            复制联系方式
          </button>
          <button class="btn btn-ghost btn-block" style="margin-top: 8px" :disabled="busy" @click="toggleFavorite">
            <AppIcon name="heart" :size="15" />
            {{ post.is_favorite ? '取消收藏' : '收藏这条招募' }}
          </button>
        </section>

        <section v-if="isOwner" class="card aside-card">
          <div class="aside-label">管理这条招募</div>
          <router-link
            v-if="post.status === 'open'"
            :to="`/post/${post.id}/edit`"
            class="btn btn-ghost btn-block"
            style="margin-top: 10px"
          >
            <AppIcon name="edit" :size="15" />编辑内容
          </router-link>
          <button
            v-if="post.status === 'open'"
            class="btn btn-ghost btn-block"
            style="margin-top: 8px"
            @click="ask('close')"
          >
            <AppIcon name="check" :size="15" />标记为已招满
          </button>
          <button
            v-if="post.status === 'open'"
            class="btn btn-danger-soft btn-block"
            style="margin-top: 8px"
            @click="ask('down')"
          >
            <AppIcon name="download" :size="15" />下架招募
          </button>
          <button
            v-if="post.status === 'open' || post.status === 'full'"
            class="btn btn-danger-soft btn-block"
            style="margin-top: 8px"
            @click="ask('delete')"
          >
            <AppIcon name="trash" :size="15" />删除
          </button>
        </section>
      </aside>
    </div>

    <ConfirmDialog
      :show="dialog.show"
      :title="dialogMeta.title"
      :desc="dialogMeta.desc"
      :confirm-text="dialogMeta.text"
      :danger="dialog.action !== 'close'"
      :loading="busy"
      @cancel="dialog = { show: false, action: '' }"
      @confirm="doAction(dialog.action)"
    />
  </div>
</template>

<style scoped>
.detail {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 318px;
  gap: 18px;
  align-items: start;
}

.detail-main {
  padding: 28px 30px 32px;
}

.detail-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.detail-title {
  font-size: 24px;
  font-weight: 750;
  letter-spacing: -0.03em;
  line-height: 1.35;
  color: #1a1f2e;
}

.detail-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  font-size: 12px;
  color: #98a0b3;
}

.detail-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.countdown {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 18px;
  padding: 11px 15px;
  border-radius: 11px;
  background: #f4f6fc;
  border: 1px solid #e8ecf7;
  font-size: 12.5px;
  color: #5d6584;
}

.countdown b {
  color: #3b4668;
  font-size: 14px;
}

.countdown.warn {
  background: #fef6ee;
  border-color: #f8e6cf;
  color: #a9702c;
}

.detail-cover {
  margin-top: 20px;
  border-radius: 14px;
  overflow: hidden;
  height: 240px;
  background: #f4f6fb;
}

.detail-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-cover-fallback {
  height: 116px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #98a3c4;
  opacity: 0.75;
}

.detail-body {
  margin-top: 26px;
}

.detail-subtitle {
  font-size: 14px;
  font-weight: 700;
  color: #262b3c;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-subtitle::before {
  content: "";
  width: 3px;
  height: 14px;
  border-radius: 3px;
  background: var(--primary);
}

.rich {
  font-size: 13.5px;
  line-height: 1.95;
  color: #454c62;
  word-break: break-word;
}

.rich :deep(b) {
  color: #262b3c;
}

.rich :deep(img) {
  display: block;
  max-width: 100%;
  margin: 10px 0;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.detail-aside {
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: sticky;
  top: calc(var(--topbar-h) + 8px);
}

.aside-card {
  padding: 20px;
}

.aside-head {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 14px;
}

.aside-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
  flex: none;
}

.aside-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0 12px;
  margin-bottom: 8px;
  border-top: 1px solid var(--line);
  font-size: 12px;
  color: var(--text-3);
}

.aside-meta span + span::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #ccd2de;
  margin-right: 12px;
  vertical-align: middle;
}

.aside-title {
  font-size: 13.5px;
  font-weight: 650;
  color: #262b3c;
}

.aside-sub {
  font-size: 11.5px;
  color: var(--text-3);
}

.aside-note {
  font-size: 12px;
  color: var(--text-3);
  line-height: 1.7;
}

.aside-label {
  font-size: 11.5px;
  letter-spacing: 0.08em;
  color: var(--text-3);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 10px;
}

.contact-value {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
}

.contact-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #2b3247;
  font-variant-numeric: tabular-nums;
  word-break: break-all;
}

.contact-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text-3);
  background: #f8f9fd;
  border-radius: 10px;
  padding: 12px;
}

@media (max-width: 1000px) {
  .detail {
    grid-template-columns: 1fr;
  }
  .detail-aside {
    position: static;
  }
}
</style>
