<script setup>
import { computed } from 'vue'
import { matchTone } from '../utils'

const props = defineProps({
  score: { type: Number, default: null },
  size: { type: String, default: 'sm' }, // sm | lg
  showLabel: { type: Boolean, default: true }
})

const tone = computed(() => matchTone(props.score))
const label = computed(() => {
  if (props.score == null) return '待完善'
  if (props.score >= 75) return '高匹配'
  if (props.score >= 50) return '较匹配'
  return '一般'
})
</script>

<template>
  <span v-if="score != null" class="match-chip" :class="[tone, size === 'lg' ? 'lg' : '']">
    <svg v-if="size === 'lg'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
      <circle cx="12" cy="12" r="8.5" stroke-dasharray="54" :stroke-dashoffset="54 - (54 * score) / 100" transform="rotate(-90 12 12)" />
    </svg>
    匹配 {{ score }}%
    <template v-if="showLabel && size === 'lg'"> · {{ label }}</template>
  </span>
</template>

<style scoped>
.match-chip.lg {
  height: 28px;
  padding: 0 12px;
  font-size: 12.5px;
  gap: 6px;
}
</style>
