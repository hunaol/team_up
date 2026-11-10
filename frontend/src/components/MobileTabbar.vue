<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { auth, badge } from '../store'

const route = useRoute()
const router = useRouter()

const tabs = [
  { key: 'home', to: '/', icon: 'home', label: '首页' },
  { key: 'posts', to: '/posts', icon: 'compass', label: '广场' }
]
const rightTabs = [
  { key: 'messages', to: '/messages', icon: 'chat', label: '消息', badge: true },
  { key: 'me', to: '/profile', icon: 'user', label: '我的' }
]

const active = computed(() => {
  const p = route.path
  if (p === '/') return 'home'
  if (p.startsWith('/posts') || p.startsWith('/post/')) return 'posts'
  if (p.startsWith('/publish')) return 'publish'
  if (p.startsWith('/messages')) return 'messages'
  if (p.startsWith('/profile') || p.startsWith('/my') || p.startsWith('/favorites')) return 'me'
  return ''
})

function go(to) {
  if (to === '/publish' && !auth.user) {
    router.push({ path: '/login', query: { redirect: '/publish' } })
    return
  }
  router.push(to)
}
</script>

<template>
  <nav v-if="!route.meta.bare" class="m-tabbar">
    <button
      v-for="t in tabs"
      :key="t.key"
      class="m-tab"
      :class="{ active: active === t.key }"
      @click="go(t.to)"
    >
      <AppIcon :name="t.icon" />
      <span>{{ t.label }}</span>
    </button>

    <button class="m-tab m-tab-publish" :class="{ active: active === 'publish' }" @click="go('/publish')">
      <span><AppIcon name="plus" :size="24" :stroke="2" /></span>
    </button>

    <button
      v-for="t in rightTabs"
      :key="t.key"
      class="m-tab"
      :class="{ active: active === t.key }"
      @click="go(t.to)"
    >
      <span style="position: relative; display: grid; place-items: center">
        <AppIcon :name="t.icon" />
        <i v-if="t.badge && badge.unread" class="m-tab-badge">{{ badge.unread > 99 ? '99+' : badge.unread }}</i>
      </span>
      <span>{{ t.label }}</span>
    </button>
  </nav>
</template>
