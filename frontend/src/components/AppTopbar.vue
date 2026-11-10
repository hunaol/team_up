<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from './AppIcon.vue'
import UserAvatar from './UserAvatar.vue'
import { auth, admin, badge } from '../store'
import { ok } from '../toast'

const router = useRouter()
const keyword = ref('')

function onSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/posts', query: q ? { q } : {} })
}

function onBell() {
  router.push('/messages')
}

function onAvatar() {
  if (admin.logged) router.push('/admin')
  else if (auth.user) router.push('/profile')
  else router.push('/login')
}

const displayName = () => (admin.logged ? '平台管理员' : auth.user ? auth.user.name : '游客')
</script>

<template>
  <header class="topbar">
    <form class="topbar-search" @submit.prevent="onSearch">
      <AppIcon name="search" />
      <input v-model="keyword" type="search" placeholder="搜索招募、队伍或关键词…" aria-label="搜索" />
    </form>

    <div class="topbar-actions">
      <button class="icon-btn" title="消息" @click="onBell">
        <AppIcon name="bell" />
        <i v-if="badge.unread" class="dot" />
      </button>
      <button class="icon-btn" title="我的账号" style="padding: 0" @click="onAvatar">
        <UserAvatar :name="displayName()" :size="34" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar-actions .icon-btn:last-child {
  background: transparent;
  box-shadow: none;
  width: 36px;
  height: 36px;
}
</style>
