<script setup>
import { useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppTopbar from './components/AppTopbar.vue'
import ToastHost from './components/ToastHost.vue'

const route = useRoute()
</script>

<template>
  <div v-if="route.meta.bare" class="bare-shell">
    <router-view />
  </div>

  <div v-else class="shell">
    <AppSidebar />
    <div class="shell-main">
      <AppTopbar />
      <main class="page">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>

  <ToastHost />
</template>

<style>
.bare-shell {
  min-height: 100vh;
  background: var(--bg);
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
