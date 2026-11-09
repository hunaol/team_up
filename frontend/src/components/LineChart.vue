<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{date, posts, participants}]
  height: { type: Number, default: 250 }
})

const COLOR_POSTS = '#14b8a6'
const COLOR_PEOPLE = '#a78bfa'

const H = props.height
const PAD = { l: 36, r: 14, t: 18, b: 30 }

const hover = ref(-1)
const wrap = ref(null)
const width = ref(760)

let observer = null

function measure() {
  if (wrap.value) width.value = Math.max(320, Math.round(wrap.value.clientWidth))
}

onMounted(() => {
  measure()
  observer = new ResizeObserver(measure)
  if (wrap.value) observer.observe(wrap.value)
})
onBeforeUnmount(() => observer && observer.disconnect())

/** 整数刻度，最多 4 段 */
function makeScale(maxValue) {
  const step = Math.max(1, Math.ceil(maxValue / 4))
  return {
    top: step * 4,
    ticks: [0, step, step * 2, step * 3, step * 4]
  }
}

/** 单调三次插值（Fritsch–Carlson）：曲线不过冲、不会掉到 0 以下 */
function monotone(pts) {
  const n = pts.length
  if (!n) return ''
  if (n === 1) return `M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`

  const dx = []
  const m = []
  for (let i = 0; i < n - 1; i++) {
    dx[i] = pts[i + 1].x - pts[i].x
    m[i] = dx[i] === 0 ? 0 : (pts[i + 1].y - pts[i].y) / dx[i]
  }

  const t = new Array(n)
  t[0] = m[0]
  t[n - 1] = m[n - 2]
  for (let i = 1; i < n - 1; i++) {
    if (m[i - 1] * m[i] <= 0) {
      t[i] = 0
    } else {
      const w1 = 2 * dx[i] + dx[i - 1]
      const w2 = dx[i] + 2 * dx[i - 1]
      t[i] = (w1 + w2) / (w1 / m[i - 1] + w2 / m[i])
    }
  }

  let d = `M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`
  for (let i = 0; i < n - 1; i++) {
    const c1x = pts[i].x + dx[i] / 3
    const c1y = pts[i].y + (t[i] * dx[i]) / 3
    const c2x = pts[i + 1].x - dx[i] / 3
    const c2y = pts[i + 1].y - (t[i + 1] * dx[i]) / 3
    d += ` C${c1x.toFixed(1)},${c1y.toFixed(1)} ${c2x.toFixed(1)},${c2y.toFixed(1)} ${pts[
      i + 1
    ].x.toFixed(1)},${pts[i + 1].y.toFixed(1)}`
  }
  return d
}

/** 圆角柱（顶部圆角，高度不足时自动收敛半径） */
function barPath(x, y, w, h, r) {
  if (h <= 0.4) return ''
  const rr = Math.min(r, w / 2, h)
  return [
    `M${x.toFixed(1)},${(y + h).toFixed(1)}`,
    `L${x.toFixed(1)},${(y + rr).toFixed(1)}`,
    `Q${x.toFixed(1)},${y.toFixed(1)} ${(x + rr).toFixed(1)},${y.toFixed(1)}`,
    `L${(x + w - rr).toFixed(1)},${y.toFixed(1)}`,
    `Q${(x + w).toFixed(1)},${y.toFixed(1)} ${(x + w).toFixed(1)},${(y + rr).toFixed(1)}`,
    `L${(x + w).toFixed(1)},${(y + h).toFixed(1)}`,
    'Z'
  ].join(' ')
}

const geom = computed(() => {
  const w = width.value
  const iw = Math.max(40, w - PAD.l - PAD.r)
  const ih = H - PAD.t - PAD.b
  const rows = props.data.length

  const maxV = rows
    ? Math.max(
        ...props.data.map((d) => Math.max(Number(d.posts) || 0, Number(d.participants) || 0))
      )
    : 0
  const scale = makeScale(maxV)
  const base = PAD.t + ih

  const band = rows ? iw / rows : iw
  const center = (i) => PAD.l + band * i + band / 2
  const barW = Math.max(2.5, Math.min(16, band * 0.44))
  const y = (v) => base - (Math.max(0, Number(v) || 0) / scale.top) * ih

  const bars = props.data.map((d, i) => {
    const h = Math.max(0, base - y(d.posts))
    return {
      d: barPath(center(i) - barW / 2, base - h, barW, h, 5),
      i
    }
  })

  const points = props.data.map((d, i) => ({ x: center(i), y: y(d.participants) }))
  const line = monotone(points)
  const area = line
    ? `${line} L${points[points.length - 1].x.toFixed(1)},${base.toFixed(1)} L${points[0].x.toFixed(
        1
      )},${base.toFixed(1)} Z`
    : ''

  const ticks = scale.ticks.map((v) => ({ v, y: y(v) }))

  // x 轴标签：最多 8 个，两两不重叠
  const labels = []
  if (rows) {
    const every = Math.max(1, Math.ceil(rows / 7))
    for (let i = 0; i < rows; i += every) labels.push(i)
    const last = rows - 1
    if (!labels.includes(last)) {
      if (last - labels[labels.length - 1] >= Math.ceil(every * 0.6)) labels.push(last)
      else labels[labels.length - 1] = last
    }
  }

  return { w, iw, ih, band, center, barW, y, base, bars, line, area, ticks, rows, labels }
})

function onMove(e) {
  const g = geom.value
  if (!g.rows) return
  const rect = e.currentTarget.getBoundingClientRect()
  const px = ((e.clientX - rect.left) / rect.width) * width.value
  const idx = Math.floor((px - PAD.l) / (g.band || 1))
  hover.value = Math.min(g.rows - 1, Math.max(0, idx))
}

const active = computed(() => (hover.value >= 0 ? props.data[hover.value] : null))

const tipStyle = computed(() => {
  if (hover.value < 0) return {}
  const g = geom.value
  return { left: `${Math.min(84, Math.max(16, (g.center(hover.value) / g.w) * 100))}%` }
})
</script>

<template>
  <div ref="wrap" class="chart">
    <div v-if="!data.length" class="chart-empty">暂无数据</div>

    <svg
      v-else
      class="chart-svg"
      :viewBox="`0 0 ${width} ${H}`"
      :height="H"
      width="100%"
      @mousemove="onMove"
      @mouseleave="hover = -1"
    >
      <defs>
        <linearGradient id="lcBarPosts" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#2dd4bf" />
          <stop offset="100%" stop-color="#0d9488" />
        </linearGradient>
        <linearGradient id="lcAreaPeople" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="COLOR_PEOPLE" stop-opacity=".18" />
          <stop offset="100%" :stop-color="COLOR_PEOPLE" stop-opacity="0" />
        </linearGradient>
      </defs>

      <!-- 网格 + 刻度 -->
      <g>
        <line
          v-for="t in geom.ticks"
          :key="'g' + t.v"
          :x1="PAD.l"
          :x2="width - PAD.r"
          :y1="t.y"
          :y2="t.y"
          :stroke="t.v === 0 ? '#e5e8f2' : '#f2f4fa'"
          stroke-width="1"
        />
        <text
          v-for="t in geom.ticks"
          :key="'t' + t.v"
          :x="PAD.l - 10"
          :y="t.y + 4"
          text-anchor="end"
          font-size="10.5"
          fill="#a8afc2"
        >
          {{ t.v }}
        </text>
      </g>

      <!-- hover 高亮列 -->
      <rect
        v-if="hover >= 0"
        :x="PAD.l + geom.band * hover"
        :y="PAD.t - 6"
        :width="geom.band"
        :height="geom.ih + 6"
        fill="#0d9488"
        fill-opacity=".05"
        rx="6"
      />

      <!-- 参与人数：面积 + 折线 -->
      <path class="lc-area" :d="geom.area" fill="url(#lcAreaPeople)" />
      <path
        class="lc-line"
        :d="geom.line"
        fill="none"
        :stroke="COLOR_PEOPLE"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        pathLength="1"
      />

      <!-- 发布数：圆角柱 -->
      <path
        v-for="b in geom.bars"
        :key="'b' + b.i"
        class="lc-bar"
        :d="b.d"
        fill="url(#lcBarPosts)"
        :style="{ animationDelay: Math.min(b.i * 18, 420) + 'ms' }"
      />

      <!-- 参与人数的非零点 -->
      <circle
        v-for="(d, i) in data"
        :key="'d' + i"
        v-show="d.participants > 0"
        :cx="geom.center(i)"
        :cy="geom.y(d.participants)"
        r="2.8"
        fill="#fff"
        :stroke="COLOR_PEOPLE"
        stroke-width="1.8"
      />

      <!-- hover 标记 -->
      <g v-if="active">
        <circle
          :cx="geom.center(hover)"
          :cy="geom.y(active.participants)"
          r="5"
          fill="#fff"
          :stroke="COLOR_PEOPLE"
          stroke-width="2.4"
        />
      </g>

      <!-- x 轴 -->
      <text
        v-for="i in geom.labels"
        :key="'x' + i"
        :x="geom.center(i)"
        :y="H - 8"
        text-anchor="middle"
        font-size="10.5"
        fill="#a8afc2"
      >
        {{ data[i].date }}
      </text>
    </svg>

    <div v-if="active" class="tip" :style="tipStyle">
      <div class="tip-date">{{ active.date }}</div>
      <div class="tip-row">
        <i :style="{ background: COLOR_POSTS }" />
        <span>发布数</span>
        <b>{{ active.posts }}</b>
      </div>
      <div class="tip-row">
        <i :style="{ background: COLOR_PEOPLE }" />
        <span>参与数</span>
        <b>{{ active.participants }}</b>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart {
  position: relative;
  width: 100%;
}

.chart-svg {
  display: block;
  width: 100%;
  overflow: visible;
}

.chart-empty {
  height: 220px;
  display: grid;
  place-items: center;
  color: var(--text-3);
  font-size: 12.5px;
}

.lc-bar {
  transform-box: fill-box;
  transform-origin: 50% 100%;
  transform: scaleY(0);
  animation: lc-grow 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

.lc-line {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: lc-draw 1s cubic-bezier(0.4, 0, 0.2, 1) 0.25s forwards;
}

.lc-area {
  opacity: 0;
  animation: lc-fade 0.8s ease 0.7s forwards;
}

@keyframes lc-grow {
  to {
    transform: scaleY(1);
  }
}

@keyframes lc-draw {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes lc-fade {
  to {
    opacity: 1;
  }
}

.tip {
  position: absolute;
  top: 8px;
  transform: translateX(-50%);
  min-width: 108px;
  padding: 9px 12px;
  border-radius: 12px;
  background: rgba(28, 32, 50, 0.95);
  backdrop-filter: blur(6px);
  color: #fff;
  font-size: 11.5px;
  box-shadow: 0 16px 34px -16px rgba(20, 24, 38, 0.75);
  pointer-events: none;
  z-index: 3;
}

.tip-date {
  color: rgba(255, 255, 255, 0.58);
  margin-bottom: 5px;
  letter-spacing: 0.04em;
}

.tip-row {
  display: flex;
  align-items: center;
  gap: 7px;
  line-height: 1.8;
}

.tip-row i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex: none;
}

.tip-row b {
  margin-left: auto;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}
</style>
