<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }, // [{label, value, color}]
  size: { type: Number, default: 168 },
  thickness: { type: Number, default: 20 }
})

const total = computed(() => props.items.reduce((s, i) => s + (i.value || 0), 0))

const R = computed(() => (props.size - props.thickness) / 2)
const C = computed(() => 2 * Math.PI * R.value)
const center = computed(() => props.size / 2)

const segments = computed(() => {
  if (!total.value) return []
  let offset = 0
  return props.items.map((it) => {
    const frac = it.value / total.value
    const len = frac * C.value
    const seg = {
      ...it,
      dash: `${Math.max(0, len - 2.5)} ${C.value - Math.max(0, len - 2.5)}`,
      offset: -offset,
      pct: Math.round(frac * 100)
    }
    offset += len
    return seg
  })
})

const mainPct = computed(() => {
  if (!total.value) return 0
  const top = [...props.items].sort((a, b) => b.value - a.value)[0]
  return top ? Math.round((top.value / total.value) * 100) : 0
})
</script>

<template>
  <div class="donut-wrap">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" class="donut">
      <circle
        :cx="center"
        :cy="center"
        :r="R"
        fill="none"
        stroke="#f2f4f9"
        :stroke-width="thickness"
      />
      <circle
        v-for="(s, i) in segments"
        :key="i"
        :cx="center"
        :cy="center"
        :r="R"
        fill="none"
        :stroke="s.color"
        :stroke-width="thickness"
        :stroke-dasharray="s.dash"
        :stroke-dashoffset="s.offset"
        stroke-linecap="round"
        :transform="`rotate(-90 ${center} ${center})`"
        class="seg"
      />
    </svg>

    <div class="donut-center">
      <strong>{{ total ? mainPct : 0 }}<small>%</small></strong>
      <span>{{ total ? '最高占比' : '暂无数据' }}</span>
    </div>
  </div>

  <ul class="legend">
    <li v-for="s in segments" :key="s.label">
      <i :style="{ background: s.color }" />
      <span>{{ s.label }}</span>
      <b>{{ s.pct }}%</b>
      <em>{{ s.value }}</em>
    </li>
    <li v-if="!segments.length" class="legend-empty">暂无招募数据</li>
  </ul>
</template>

<style scoped>
.donut-wrap {
  position: relative;
  display: grid;
  place-items: center;
  width: 100%;
}

.seg {
  transition: stroke-dasharray 0.5s ease;
}

.donut-center {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.donut-center strong {
  font-size: 26px;
  font-weight: 750;
  letter-spacing: -0.04em;
  color: #1e2333;
  line-height: 1.1;
}

.donut-center small {
  font-size: 13px;
  font-weight: 600;
  margin-left: 1px;
  color: #7b8399;
}

.donut-center span {
  font-size: 11px;
  color: var(--text-3);
}

.legend {
  list-style: none;
  padding: 0;
  margin: 14px 0 0;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.legend li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: #4d5468;
}

.legend i {
  width: 8px;
  height: 8px;
  border-radius: 3px;
  flex: none;
}

.legend b {
  margin-left: auto;
  font-weight: 650;
  font-variant-numeric: tabular-nums;
  color: #2b3143;
}

.legend em {
  font-style: normal;
  font-size: 11px;
  color: #aab1c0;
  min-width: 26px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.legend-empty {
  color: #aab1c0;
  font-size: 12px;
}
</style>
