<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from './AppIcon.vue'
import UserAvatar from './UserAvatar.vue'
import { auth, admin, badge, logout, setAdminLogged } from '../store'
import { setAdminToken } from '../api'
import { ok } from '../toast'

const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)

const userNav = [
  { to: '/', icon: 'home', label: '首页' },
  { to: '/posts', icon: 'compass', label: '招募广场' },
  { to: '/competitions', icon: 'flag', label: '竞赛名录' },
  { to: '/publish', icon: 'megaphone', label: '发布招募' },
  { to: '/messages', icon: 'chat', label: '消息', badge: true },
  { to: '/my', icon: 'file', label: '我的发布' },
  { to: '/favorites', icon: 'bookmark', label: '我的收藏' },
  { to: '/profile', icon: 'user', label: '我的资料' }
]

const adminNav = [
  { to: '/admin', icon: 'chart', label: '数据概览' },
  { to: '/admin/users', icon: 'users', label: '用户管理' },
  { to: '/admin/posts', icon: 'list', label: '帖子管理' }
]

const isActive = (to) =>
  to === '/admin' ? route.path === '/admin' : route.path === to || route.path.startsWith(to + '/')

const roleText = computed(() => {
  if (auth.user) return admin.logged ? '学生 · 管理员' : '学生 · ' + auth.user.student_id
  if (admin.logged) return '管理员'
  return '未登录'
})

const displayName = computed(() => {
  if (auth.user) return auth.user.name
  if (admin.logged) return '平台管理员'
  return '游客'
})

async function onLogout() {
  menuOpen.value = false
  setAdminToken('')
  setAdminLogged(false)
  if (auth.user) {
    await logout()
    ok('已退出登录')
    router.push('/')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <span class="brand-mark">
        <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3.2 9.4 12 5.2l8.8 4.2L12 13.6 3.2 9.4Z" />
          <path d="M6.6 11.4v4.2c0 1.9 2.4 3.2 5.4 3.2s5.4-1.3 5.4-3.2v-4.2" />
          <path d="M20.8 9.6v4.6" />
        </svg>
      </span>
      <span class="brand-text">
        <span class="brand-title">比赛队招募</span>
        <span class="brand-sub">校园招募平台</span>
      </span>
    </div>

    <nav class="nav-group">
      <router-link
        v-for="item in userNav"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: isActive(item.to) }"
      >
        <AppIcon :name="item.icon" />
        <span>{{ item.label }}</span>
        <span v-if="item.badge && badge.unread" class="nav-count">{{ badge.unread > 99 ? '99+' : badge.unread }}</span>
      </router-link>
    </nav>

    <nav v-if="admin.logged" class="nav-group">
      <div class="nav-label">管理后台</div>
      <router-link
        v-for="item in adminNav"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: isActive(item.to) }"
      >
        <AppIcon :name="item.icon" />
        <span>{{ item.label }}</span>
      </router-link>
      <router-link to="/" class="nav-item nav-back">
        <AppIcon name="chevronLeft" />
        <span>返回前台</span>
      </router-link>
    </nav>

    <div class="sidebar-foot">
      <button v-if="!auth.user && !admin.logged" class="btn btn-primary btn-sm btn-block" @click="router.push('/login')">
        登录 / 注册
      </button>

      <template v-else>
        <button class="user-chip" @click="menuOpen = !menuOpen">
          <UserAvatar :name="displayName" :size="34" />
          <span class="user-chip-meta">
            <span class="user-chip-name">{{ displayName }}</span>
            <span class="user-chip-role">{{ roleText }}</span>
          </span>
          <AppIcon name="chevronDown" :size="15" style="color: #a3aaba" />
        </button>

        <div v-if="menuOpen" class="menu sidebar-menu">
          <button @click="router.push('/profile'); menuOpen = false">
            <AppIcon name="user" /> 我的资料
          </button>
          <button @click="router.push('/my'); menuOpen = false">
            <AppIcon name="file" /> 我的发布
          </button>
          <button v-if="admin.logged" @click="router.push('/admin'); menuOpen = false">
            <AppIcon name="chart" /> 管理后台
          </button>
          <button class="danger" @click="onLogout">
            <AppIcon name="logout" /> 退出登录
          </button>
        </div>

        <button class="logout-btn" @click="onLogout">
          <AppIcon name="logout" />
          <span>退出登录</span>
        </button>
      </template>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-foot {
  position: relative;
}
.sidebar-menu {
  position: absolute;
  left: 6px;
  right: 6px;
  bottom: calc(100% - 6px);
  top: auto;
}

/* 返回前台不参与「当前页高亮」，颜色和后台导航区分 */
.nav-back {
  color: var(--accent-strong);
}

.nav-back:hover {
  background: var(--accent-soft);
  color: var(--accent-strong);
}
</style>
