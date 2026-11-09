<script setup>
import AppIcon from './AppIcon.vue'
import { toastState } from '../toast'
</script>

<template>
  <div class="toast-host">
    <transition name="toast">
      <div v-if="toastState.show" :key="toastState.key" class="toast" :class="toastState.type">
        <AppIcon :name="toastState.type === 'err' ? 'alert' : 'check'" :size="16" />
        <span>{{ toastState.text }}</span>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.toast-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>
