<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  desc: { type: String, default: '' },
  confirmText: { type: String, default: '确认' },
  cancelText: { type: String, default: '取消' },
  danger: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <transition name="overlay">
    <div v-if="show" class="overlay" @click.self="emit('cancel')">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-icon" :class="{ danger }">
          <AppIcon :name="danger ? 'alert' : 'shield'" :size="20" />
        </div>
        <h3 class="modal-title">{{ title }}</h3>
        <p v-if="desc" class="modal-desc">{{ desc }}</p>
        <div class="modal-actions">
          <button class="btn btn-ghost" :disabled="loading" @click="emit('cancel')">
            {{ cancelText }}
          </button>
          <button
            class="btn"
            :class="danger ? 'btn-danger-soft' : 'btn-primary'"
            :disabled="loading"
            @click="emit('confirm')"
          >
            {{ loading ? '处理中…' : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-icon {
  width: 42px;
  height: 42px;
  border-radius: 13px;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
  margin-bottom: 14px;
}
.modal-icon.danger {
  background: var(--red-soft);
  color: var(--red);
}
.overlay-leave-active {
  transition: opacity 0.16s ease;
}
.overlay-leave-to {
  opacity: 0;
}
</style>
