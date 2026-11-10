<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth, refreshUnread } from '../store'
import { relTime } from '../utils'
import { err } from '../toast'
import PageHead from '../components/PageHead.vue'
import AppIcon from '../components/AppIcon.vue'
import UserAvatar from '../components/UserAvatar.vue'

const route = useRoute()
const router = useRouter()

const threads = ref([])
const loading = ref(true)
const messages = ref([])
const peer = ref(null)
const draft = ref('')
const sending = ref(false)
const scroller = ref(null)

const activeId = computed(() => (route.params.peerId ? Number(route.params.peerId) : null))
const isMobileChat = computed(() => !!activeId.value)

function scrollBottom() {
  nextTick(() => {
    const el = scroller.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function loadThreads() {
  loading.value = true
  try {
    threads.value = await api('/messages/threads')
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

async function loadConversation() {
  if (!activeId.value) {
    messages.value = []
    peer.value = null
    return
  }
  try {
    const r = await api('/messages/with/' + activeId.value)
    peer.value = r.peer
    messages.value = r.messages
    scrollBottom()
    refreshUnread()
    // 会话里的未读数已清零，同步刷新列表角标
    const t = threads.value.find((x) => x.peer.id === activeId.value)
    if (t) t.unread = 0
  } catch (e) {
    err(e.message)
  }
}

async function send() {
  const text = draft.value.trim()
  if (!text || sending.value) return
  sending.value = true
  try {
    const m = await api('/messages', {
      method: 'POST',
      body: { to_id: activeId.value, body: text }
    })
    messages.value.push(m)
    draft.value = ''
    scrollBottom()
    loadThreads()
  } catch (e) {
    err(e.message)
  } finally {
    sending.value = false
  }
}

function openThread(t) {
  router.push({ path: `/messages/${t.peer.id}`, query: t.last.post_id ? { post: t.last.post_id } : {} })
}

onMounted(async () => {
  await loadThreads()
  await loadConversation()
})

watch(
  () => route.params.peerId,
  async () => {
    await loadConversation()
  }
)
</script>

<template>
  <div>
    <div class="msg-pagehead" :class="{ 'hide-on-chat': isMobileChat }">
      <PageHead
        :crumbs="[{ label: '首页', to: '/' }, { label: '消息' }]"
        title="消息"
        desc="和队长、队友的沟通都在这里，申请结果也会通过私信通知你"
      />
    </div>

    <div class="msg-wrap" :class="{ 'mobile-chat': isMobileChat }">
      <aside class="card thread-list">
        <div class="thread-head">
          <span>会话</span>
          <button class="icon-btn" title="刷新" @click="loadThreads"><AppIcon name="refresh" :size="15" /></button>
        </div>

        <div v-if="loading" class="thread-body">
          <div v-for="i in 4" :key="i" class="skeleton" style="height: 58px; border-radius: 12px; margin-bottom: 8px" />
        </div>

        <div v-else-if="threads.length" class="thread-body">
          <button
            v-for="t in threads"
            :key="t.peer.id"
            class="thread-item"
            :class="{ active: activeId === t.peer.id }"
            @click="openThread(t)"
          >
            <UserAvatar :name="t.peer.name" :size="38" />
            <div class="thread-main">
              <div class="thread-top">
                <span class="thread-name">{{ t.peer.name }}</span>
                <span class="thread-time">{{ relTime(t.last.created_at) }}</span>
              </div>
              <div class="thread-last">{{ t.last.from_id === auth.user?.id ? '我：' : '' }}{{ t.last.body }}</div>
              <div v-if="t.post_title" class="thread-post">
                <AppIcon name="flag" :size="11" />{{ t.post_title }}
              </div>
            </div>
            <span v-if="t.unread" class="thread-badge">{{ t.unread }}</span>
          </button>
        </div>

        <div v-else class="empty" style="padding: 40px 18px">
          <div class="empty-art"><AppIcon name="chat" :size="32" /></div>
          <div class="empty-title">还没有消息</div>
          <p class="empty-desc">在招募详情页点「私信发布者」就能开始聊天</p>
        </div>
      </aside>

      <section class="card chat">
        <template v-if="activeId">
          <header class="chat-head">
            <button class="icon-btn chat-back" @click="router.push('/messages')">
              <AppIcon name="chevronLeft" :size="18" />
            </button>
            <UserAvatar :name="peer?.name || ''" :size="34" />
            <div class="chat-who">
              <div class="chat-name">{{ peer?.name || '对话' }}</div>
              <div class="chat-sub">站内私信 · 请文明沟通</div>
            </div>
            <router-link v-if="peer" :to="`/post/${$route.query.post}`" class="only-desktop link-btn" style="margin-left: auto">
              相关招募
            </router-link>
          </header>

          <div ref="scroller" class="chat-body">
            <div v-if="!messages.length" class="chat-empty">还没有聊天记录，打个招呼吧</div>
            <div
              v-for="m in messages"
              :key="m.id"
              class="bubble-row"
              :class="{ mine: m.from_id === auth.user?.id }"
            >
              <div class="bubble">
                {{ m.body }}
                <span class="bubble-time">{{ relTime(m.created_at) }}</span>
              </div>
            </div>
          </div>

          <form class="chat-foot" @submit.prevent="send">
            <input v-model="draft" class="input" placeholder="说点什么…" maxlength="1000" />
            <button class="btn btn-primary" type="submit" :disabled="sending || !draft.trim()">
              <AppIcon name="send" :size="15" />
              发送
            </button>
          </form>
        </template>

        <div v-else class="chat-placeholder">
          <div class="empty-art"><AppIcon name="chat" :size="34" /></div>
          <div class="empty-title">选择一个会话</div>
          <p class="empty-desc">左侧列表里点开一条消息，就能继续聊天</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.msg-wrap {
  display: grid;
  grid-template-columns: 330px minmax(0, 1fr);
  gap: 16px;
  height: calc(100vh - var(--topbar-h) - 150px);
  min-height: 420px;
}

.thread-list {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.thread-head {
  display: flex;
  align-items: center;
  padding: 14px 16px 10px;
  font-size: 13px;
  font-weight: 700;
  color: #2b3143;
  border-bottom: 1px solid var(--line);
}

.thread-head .icon-btn {
  margin-left: auto;
}

.thread-body {
  overflow-y: auto;
  padding: 8px;
  flex: 1;
}

.thread-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 10px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  position: relative;
}

.thread-item:hover {
  background: #f7f8fd;
}

.thread-item.active {
  background: var(--accent-soft);
}

.thread-main {
  min-width: 0;
  flex: 1;
}

.thread-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.thread-name {
  font-size: 13px;
  font-weight: 650;
  color: #232838;
}

.thread-time {
  margin-left: auto;
  font-size: 10.5px;
  color: var(--text-4);
  flex: none;
}

.thread-last {
  font-size: 11.5px;
  color: var(--text-3);
  margin-top: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thread-post {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  color: #7a83a0;
  background: rgba(0, 0, 0, 0.035);
  border-radius: 6px;
  padding: 2px 6px;
  margin-top: 5px;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thread-badge {
  position: absolute;
  right: 10px;
  bottom: 10px;
  min-width: 17px;
  height: 17px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--red);
  color: #fff;
  font-size: 10px;
  line-height: 17px;
  text-align: center;
  font-weight: 700;
}

.chat {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.chat-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
}

.chat-back {
  display: none;
}

.chat-who {
  min-width: 0;
}

.chat-name {
  font-size: 13.5px;
  font-weight: 650;
  color: #232838;
}

.chat-sub {
  font-size: 11px;
  color: var(--text-3);
  margin-top: 1px;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #fbfcfe;
}

.chat-empty,
.chat-placeholder {
  margin: auto;
  text-align: center;
  font-size: 12.5px;
  color: var(--text-3);
}

.chat-placeholder .empty-art {
  margin: 0 auto 10px;
}

.bubble-row {
  display: flex;
}

.bubble-row.mine {
  justify-content: flex-end;
}

.bubble {
  max-width: 74%;
  padding: 9px 13px;
  border-radius: 14px 14px 14px 4px;
  background: #fff;
  border: 1px solid var(--line);
  font-size: 13px;
  line-height: 1.65;
  color: #2b3143;
  word-break: break-word;
  white-space: pre-wrap;
}

.bubble-row.mine .bubble {
  background: linear-gradient(140deg, #57608c, #414a6d);
  border-color: transparent;
  color: #fff;
  border-radius: 14px 14px 4px 14px;
}

.bubble-time {
  display: block;
  font-size: 10px;
  opacity: 0.6;
  margin-top: 4px;
  text-align: right;
}

.chat-foot {
  display: flex;
  gap: 10px;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid var(--line);
  background: #fff;
}

.chat-foot .btn {
  flex: none;
}

@media (max-width: 860px) {
  .msg-wrap {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 0;
  }

  .thread-list {
    max-height: calc(100dvh - var(--topbar-h) - 210px);
  }

  .msg-wrap.mobile-chat {
    height: calc(100dvh - var(--topbar-h) - 96px);
  }

  .msg-pagehead.hide-on-chat {
    display: none;
  }

  .msg-wrap.mobile-chat .thread-list {
    display: none;
  }

  .msg-wrap:not(.mobile-chat) .chat {
    display: none;
  }

  .chat-back {
    display: grid;
  }

  .bubble {
    max-width: 80%;
  }
}
</style>
