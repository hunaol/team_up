<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { adminApi } from '../../api'
import { thousand } from '../../utils'
import { err } from '../../toast'
import AppIcon from '../../components/AppIcon.vue'
import PageHead from '../../components/PageHead.vue'
import LineChart from '../../components/LineChart.vue'
import DonutChart from '../../components/DonutChart.vue'

const range = ref(30)
const data = ref(null)
const loading = ref(true)

const RANGES = [
  { value: 7, label: '近 7 天' },
  { value: 30, label: '近 30 天' },
  { value: 90, label: '近 90 天' }
]

const cards = computed(() => {
  const d = data.value || {}
  const g = d.growth || {}
  return [
    {
      label: '注册用户',
      value: thousand(d.user_count ?? 0),
      delta: g.users,
      icon: 'users',
      tone: 'blue',
      sub: `本周期新增 ${d.users_new ?? 0}`
    },
    {
      label: '发布招募',
      value: thousand(d.post_total ?? 0),
      delta: g.posts,
      icon: 'megaphone',
      tone: 'green',
      sub: `本周期 ${d.posts_in_range ?? 0} 条`
    },
    {
      label: '参与人数',
      value: thousand(d.participants_total ?? 0),
      delta: g.participants,
      icon: 'user',
      tone: 'orange',
      sub: `本周期 ${d.participants_in_range ?? 0} 人`
    },
    {
      label: '招募成功率',
      value: (d.success_rate ?? 0) + '%',
      delta: g.success_rate,
      icon: 'trend',
      tone: 'purple',
      sub: '已招满 / 全部招募',
      raw: true
    }
  ]
})

const donutItems = computed(() => {
  const dist = data.value?.status_distribution || {}
  return [
    { label: '招募中', value: dist.open || 0, color: '#0d9488' },
    { label: '已招满', value: dist.full || 0, color: '#3b82f6' },
    { label: '已下架', value: dist.down || 0, color: '#f59e0b' },
    { label: '已过期', value: dist.expired || 0, color: '#94a3b8' }
  ].filter((i) => i.value > 0)
})

async function load() {
  loading.value = true
  try {
    data.value = await adminApi(`/admin/stats?range=${range.value}`)
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

function deltaText(v, raw) {
  if (v === undefined || v === null) return ''
  if (v === 0) return '持平'
  const sign = v > 0 ? '+' : ''
  return raw ? `${sign}${v} pt` : `${sign}${v}%`
}

watch(range, load)
onMounted(load)
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '管理后台', to: '/admin' }, { label: '数据概览' }]"
      title="数据概览"
      desc="平台整体运行数据，掌握招募活跃度与转化情况"
    >
      <template #actions>
        <div class="segmented">
          <button
            v-for="r in RANGES"
            :key="r.value"
            :class="{ active: range === r.value }"
            @click="range = r.value"
          >
            {{ r.label }}
          </button>
        </div>
      </template>
    </PageHead>

    <div class="stat-grid">
      <div v-for="c in cards" :key="c.label" class="stat-card">
        <span class="stat-icon" :class="c.tone"><AppIcon :name="c.icon" /></span>
        <div class="stat-main">
          <div class="stat-label">{{ c.label }}</div>
          <div class="stat-value">
            {{ loading ? '—' : c.value }}
            <span
              v-if="!loading && c.delta !== undefined && c.delta !== null"
              class="stat-delta"
              :class="{ down: c.delta < 0 }"
            >
              <AppIcon :name="c.delta < 0 ? 'chevronDown' : 'trend'" :size="11" />
              {{ deltaText(c.delta, c.raw) }}
            </span>
          </div>
          <div class="stat-sub">{{ c.sub }}</div>
        </div>
      </div>
    </div>

    <div class="charts">
      <section class="card chart-card">
        <div class="chart-head">
          <div>
            <h2 class="card-title">招募发布趋势</h2>
            <p class="card-sub">每日新增招募与参与人数变化</p>
          </div>
          <div class="legend-inline">
            <span><i class="dot1" />发布数</span>
            <span><i class="dot2" />参与数</span>
          </div>
        </div>
        <div class="chart-body">
          <div v-if="loading" class="skeleton" style="height: 240px; border-radius: 12px" />
          <LineChart v-else :data="data?.trend || []" :height="250" />
        </div>
      </section>

      <section class="card chart-card donut-card">
        <div class="chart-head">
          <div>
            <h2 class="card-title">招募状态分布</h2>
            <p class="card-sub">全部招募的当前状态占比</p>
          </div>
        </div>
        <div class="donut-body">
          <div v-if="loading" class="skeleton" style="height: 168px; width: 168px; border-radius: 50%; margin: 0 auto" />
          <DonutChart v-else :items="donutItems" :size="168" :thickness="20" />
        </div>
      </section>
    </div>

    <section class="card insight">
      <div class="insight-icon"><AppIcon name="sparkles" :size="18" /></div>
      <div>
        <div class="insight-title">运营小结</div>
        <p class="insight-text">
          当前共有 <b>{{ data?.open_count ?? 0 }}</b> 条招募正在进行中，
          平台累计发布 <b>{{ data?.post_total ?? 0 }}</b> 条，
          其中找队友 <b>{{ data?.team_count ?? 0 }}</b> 条、找队伍 <b>{{ data?.join_count ?? 0 }}</b> 条。
          平均每条招募需求 <b>{{ data?.post_total ? (data.participants_total / data.post_total).toFixed(1) : 0 }}</b> 人。
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.stat-sub {
  font-size: 11px;
  color: #aab1c0;
  margin-top: 1px;
}

.charts {
  display: grid;
  grid-template-columns: minmax(0, 1.62fr) minmax(0, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.chart-card {
  padding: 20px 22px 14px;
}

.chart-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 10px;
}

.legend-inline {
  margin-left: auto;
  display: flex;
  gap: 14px;
  font-size: 11.5px;
  color: #7b8296;
}

.legend-inline span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-inline i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.dot1 {
  background: #14b8a6;
}

.dot2 {
  background: #a78bfa;
}

.chart-body {
  padding-top: 6px;
}

.donut-card {
  display: flex;
  flex-direction: column;
}

.donut-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 6px 4px 10px;
}

.insight {
  display: flex;
  gap: 14px;
  padding: 18px 22px;
  margin-top: 16px;
  align-items: flex-start;
}

.insight-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--accent-soft);
  color: var(--accent);
  flex: none;
}

.insight-title {
  font-size: 13px;
  font-weight: 650;
  color: #262b3c;
  margin-bottom: 3px;
}

.insight-text {
  font-size: 12.5px;
  color: var(--text-2);
  line-height: 1.8;
}

.insight-text b {
  color: #333a52;
}

@media (max-width: 1100px) {
  .charts {
    grid-template-columns: 1fr;
  }
}
</style>
