<script setup>
import { computed } from 'vue'
import { gradientOf, initialsOne } from '../utils'

const props = defineProps({
  name: { type: String, default: '' },
  src: { type: String, default: '' },
  size: { type: [Number, String], default: 38 },
  radius: { type: [Number, String], default: 0 }
})

const style = computed(() => {
  const g = gradientOf(props.name)
  const px = typeof props.size === 'number' ? props.size + 'px' : props.size
  return {
    width: px,
    height: px,
    fontSize: Math.max(11, Math.round(Number.parseInt(props.size) * 0.38)) + 'px',
    background: `linear-gradient(140deg, ${g[0]}, ${g[1]})`,
    color: '#5b6a92',
    borderRadius: props.radius ? props.radius + 'px' : '50%'
  }
})

const letter = computed(() => initialsOne(props.name))
</script>

<template>
  <span class="avatar" :style="style">
    <img v-if="src" :src="src" :alt="name" />
    <template v-else>{{ letter }}</template>
  </span>
</template>
