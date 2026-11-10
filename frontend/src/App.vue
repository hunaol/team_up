<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppIcon from './components/AppIcon.vue'
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
      <nav v-if="admin.logged && route.meta.admin" class="admin-mnav">
        <div class="admin-mnav-scroll">
          <router-link
            v-for="t in adminTabs"
            :key="t.to"
            :to="t.to"
            class="admin-mtab"
            :class="{ active: route.path === t.to }"
          >
            {{ t.label }}
          </router-link>
        </div>
        <router-link to="/" class="admin-mtab admin-mtab-back">
          <AppIcon name="chevronLeft" :size="13" />
          返回前台
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

/* 后台移动端导航：仅小屏显示（不用 .only-mobile，避免被它的 display:block 覆盖掉 flex） */
.admin-mnav {
  display: none;
}

@media (max-width: 860px) {
  .admin-mnav {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px 0;
  }
}

/* 后台三个 tab 可以横向滚动，返回前台固定贴在右侧，永远点得到 */
.admin-mnav-scroll {
  display: flex;
  gap: 6px;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.admin-mnav-scroll::-webkit-scrollbar {
  display: none;
}

.admin-mtab {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 34px;
  padding: 0 13px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--line);
  font-size: 12.5px;
  font-weight: 500;
  color: #5b6276;
  white-space: nowrap;
  line-height: 1;
}

.admin-mtab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  font-weight: 600;
}

/* 返回前台：和后台导航区分开，固定在右侧不参与滚动 */
.admin-mtab-back {
  flex: none;
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: var(--accent-strong);
  border-color: #b9e3dc;
  background: var(--accent-soft);
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
