<script setup>
import { computed } from 'vue'
import { STATUS_CLASS, STATUS_TEXT } from '../utils'

const props = defineProps({
  status: { type: String, default: 'open' },
  dot: { type: Boolean, default: true }
})

const cls = computed(() => ['pill', STATUS_CLASS[props.status] || 'pill-neutral'])
const text = computed(() => STATUS_TEXT[props.status] || props.status)
</script>

<template>
  <span :class="cls">
    <i v-if="dot" class="dot" />
    {{ text }}
  </span>
</template>
