<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppTopbar from './components/AppTopbar.vue'
import MobileTabbar from './components/MobileTabbar.vue'
import ToastHost from './components/ToastHost.vue'
import { admin, auth, refreshUnread } from './store'

const route = useRoute()

const adminTabs = [
  { to: '/admin', label: '数据概览' },
  { to: '/admin/users', label: '用户管理' },
  { to: '/admin/posts', label: '招募管理' }
]

onMounted(refreshUnread)
watch(
  () => route.fullPath,
  () => {
    if (auth.user) refreshUnread()
  }
)
</script>

<template>
  <div v-if="route.meta.bare" class="bare-shell">
    <router-view />
  </div>

  <div v-else class="shell">
    <AppSidebar class="only-desktop-side" />
    <div class="shell-main">
      <AppTopbar />
      <nav v-if="admin.logged && route.meta.admin" class="admin-mnav only-mobile">
        <router-link
          v-for="t in adminTabs"
          :key="t.to"
          :to="t.to"
          class="admin-mtab"
          :class="{ active: route.path === t.to }"
        >
          {{ t.label }}
        </router-link>
      </nav>
      <main class="page">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <MobileTabbar v-if="!route.meta.admin" />
  </div>

  <ToastHost />
</template>

<style>
.bare-shell {
  min-height: 100vh;
  background: var(--bg);
}

.admin-mnav {
  display: flex;
  gap: 6px;
  padding: 10px 14px 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.admin-mnav::-webkit-scrollbar {
  display: none;
}

.admin-mtab {
  flex: none;
  padding: 7px 13px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--line);
  font-size: 12.5px;
  font-weight: 500;
  color: #5b6276;
  white-space: nowrap;
}

.admin-mtab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  font-weight: 600;
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-leave-to {
  opacity: 0;
}
</style>
