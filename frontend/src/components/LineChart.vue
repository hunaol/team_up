<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{date, posts, participants}]
  height: { type: Number, default: 240 }
})

const W = 720
const H = props.height
const PAD = { l: 34, r: 12, t: 18, b: 30 }

const hover = ref(-1)
const wrap = ref(null)
const width = ref(W)

function resize() {
  if (wrap.value) width.value = Math.max(420, wrap.value.clientWidth)
}

const geom = computed(() => {
  const w = width.value
  const iw = w - PAD.l - PAD.r
  const ih = H - PAD.t - PAD.b
  const n = props.data.length || 1
  const maxV = Math.max(4, ...props.data.map((d) => Math.max(d.posts, d.participants)))
  const step = n > 1 ? iw / (n - 1) : 0

  const x = (i) => PAD.l + i * step
  const y = (v) => PAD.t + ih - (v / maxV) * ih

  const line = (key) =>
    props.data
      .map((d, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(d[key]).toFixed(1)}`)
      .join(' ')

  const area = (key) =>
    `${line(key)} L${x(n - 1).toFixed(1)},${(PAD.t + ih).toFixed(1)} L${PAD.l},${(
      PAD.t + ih
    ).toFixed(1)} Z`

  // 平滑曲线（Catmull-Rom → 三次贝塞尔）
  const smooth = (key) => {
    const pts = props.data.map((d, i) => ({ x: x(i), y: y(d[key]) }))
    if (pts.length < 2) return ''
    let d = `M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i]
      const p1 = pts[i]
      const p2 = pts[i + 1]
      const p3 = pts[i + 2] || p2
      const t = 0.18
      const c1x = p1.x + (p2.x - p0.x) * t
      const c1y = p1.y + (p2.y - p0.y) * t
      const c2x = p2.x - (p3.x - p1.x) * t
      const c2y = p2.y - (p3.y - p1.y) * t
      d += ` C${c1x.toFixed(1)},${c1y.toFixed(1)} ${c2x.toFixed(1)},${c2y.toFixed(1)} ${p2.x.toFixed(
        1
      )},${p2.y.toFixed(1)}`
    }
    return d
  }

  const smoothArea = (key) => {
    const s = smooth(key)
    if (!s) return ''
    return `${s} L${x(n - 1).toFixed(1)},${(PAD.t + ih).toFixed(1)} L${PAD.l},${(
      PAD.t + ih
    ).toFixed(1)} Z`
  }

  const ticks = [0, 0.5, 1].map((f) => ({
    y: PAD.t + ih - f * ih,
    v: Math.round(maxV * f)
  }))

  const lx = (i) => x(i)
  const ly = (key, i) => y(props.data[i][key])

  return { w, iw, ih, x, y, maxV, line, area, smooth, smoothArea, ticks, n, step, lx, ly }
})

const labelEvery = computed(() => {
  const n = props.data.length
  return n > 30 ? 6 : n > 14 ? 3 : 1
})

function onMove(e) {
  const svg = e.currentTarget
  const rect = svg.getBoundingClientRect()
  const px = ((e.clientX - rect.left) / rect.width) * width.value
  const g = geom.value
  const idx = Math.round((px - PAD.l) / (g.step || 1))
  hover.value = Math.min(props.data.length - 1, Math.max(0, idx))
}

onMounted(() => {
  resize()
  window.addEventListener('resize', resize)
})
onBeforeUnmount(() => window.removeEventListener('resize', resize))

defineExpose({ resize })
</script>

<template>
  <div ref="wrap" class="chart">
    <svg
      :viewBox="`0 0 ${width} ${H}`"
      :height="H"
      width="100%"
      preserveAspectRatio="none"
      @mousemove="onMove"
      @mouseleave="hover = -1"
    >
      <defs>
        <linearGradient id="areaPosts" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#4a5bd4" stop-opacity=".16" />
          <stop offset="1" stop-color="#4a5bd4" stop-opacity="0" />
        </linearGradient>
        <linearGradient id="areaPeople" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#b9c0d8" stop-opacity=".22" />
          <stop offset="1" stop-color="#b9c0d8" stop-opacity="0" />
        </linearGradient>
      </defs>

      <g>
        <line
          v-for="t in geom.ticks"
          :key="t.y"
          :x1="PAD.l"
          :x2="width - PAD.r"
          :y1="t.y"
          :y2="t.y"
          stroke="#f0f2f8"
          stroke-width="1"
        />
        <text
          v-for="t in geom.ticks"
          :key="'l' + t.y"
          :x="PAD.l - 8"
          :y="t.y + 3.5"
          text-anchor="end"
          font-size="10"
          fill="#b0b7c6"
        >
          {{ t.v }}
        </text>
      </g>

      <path v-if="data.length > 1" :d="geom.smoothArea('participants')" fill="url(#areaPeople)" />
      <path v-if="data.length > 1" :d="geom.smoothArea('posts')" fill="url(#areaPosts)" />

      <path
        v-if="data.length > 1"
        :d="geom.smooth('participants')"
        fill="none"
        stroke="#c3c9db"
        stroke-width="2"
        stroke-linecap="round"
      />
      <path
        v-if="data.length > 1"
        :d="geom.smooth('posts')"
        fill="none"
        stroke="#4a5bd4"
        stroke-width="2.4"
        stroke-linecap="round"
      />

      <g v-if="hover >= 0 && data[hover]">
        <line
          :x1="geom.x(hover)"
          :x2="geom.x(hover)"
          :y1="PAD.t"
          :y2="H - PAD.b"
          stroke="#d9dcec"
          stroke-width="1"
          stroke-dasharray="3 3"
        />
        <circle :cx="geom.x(hover)" :cy="geom.ly('participants', hover)" r="4" fill="#fff" stroke="#c3c9db" stroke-width="2" />
        <circle :cx="geom.x(hover)" :cy="geom.ly('posts', hover)" r="4.5" fill="#fff" stroke="#4a5bd4" stroke-width="2.4" />
      </g>

      <g>
        <text
          v-for="(d, i) in data"
          :key="d.date + i"
          v-show="i % labelEvery === 0 || i === data.length - 1"
          :x="geom.x(i)"
          :y="H - 8"
          text-anchor="middle"
          font-size="10"
          fill="#aab1c0"
        >
          {{ d.date }}
        </text>
      </g>
    </svg>

    <div
      v-if="hover >= 0 && data[hover]"
      class="tip"
      :style="{ left: Math.min(Math.max(geom.x(hover) / width.value * 100, 8), 86) + '%' }"
    >
      <div class="tip-date">{{ data[hover].date }}</div>
      <div class="tip-row"><i class="d1" />发布 <b>{{ data[hover].posts }}</b></div>
      <div class="tip-row"><i class="d2" />参与 <b>{{ data[hover].participants }}</b></div>
    </div>
  </div>
</template>

<style scoped>
.chart {
  position: relative;
  width: 100%;
}

.tip {
  position: absolute;
  top: 6px;
  transform: translateX(-50%);
  background: #232839;
  color: #fff;
  border-radius: 10px;
  padding: 8px 11px;
  font-size: 11px;
  box-shadow: 0 14px 30px -14px rgba(20, 24, 38, 0.7);
  pointer-events: none;
  min-width: 92px;
}

.tip-date {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
  letter-spacing: 0.04em;
}

.tip-row {
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.7;
}

.tip-row b {
  margin-left: auto;
  font-variant-numeric: tabular-nums;
}

.tip-row i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.d1 {
  background: #8f9dff;
}
.d2 {
  background: #cfd5e6;
}
</style>
