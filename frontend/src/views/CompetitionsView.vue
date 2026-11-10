<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { err } from '../toast'
import AppIcon from '../components/AppIcon.vue'
import PageHead from '../components/PageHead.vue'

const router = useRouter()

const all = ref([])
const counts = ref({})
const keyword = ref('')
const category = ref('')
const onlyActive = ref(false)
const loading = ref(true)

const CATS = [
  '计算机',
  '电子工程',
  '机械制造',
  '数理统计',
  '经管商科',
  '创新创业',
  '设计传媒',
  '能源环境',
  '土木建筑',
  '地球科学',
  '生命科学',
  '外语人文',
  '综合'
]

onMounted(async () => {
  try {
    const meta = await api('/meta')
    all.value = meta.competitions || []
  } catch (e) {
    err(e.message || '比赛名录加载失败')
  } finally {
    loading.value = false
  }
  try {
    counts.value = await api('/meta/competition-counts')
  } catch (e) {
    /* 计数失败不影响名录浏览 */
  }
})

const cats = computed(() => {
  const present = new Set(all.value.map((c) => c.category))
  return CATS.filter((c) => present.has(c))
})

const activeCount = computed(() =>
  Object.values(counts.value).reduce((sum, n) => sum + n, 0)
)

const filtered = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return all.value.filter((c) => {
    if (onlyActive.value && !counts.value[c.name]) return false
    if (category.value && c.category !== category.value) return false
    if (!q) return true
    return (
      c.name.toLowerCase().includes(q) ||
      (c.aliases || []).some((a) => a.toLowerCase().includes(q))
    )
  })
})

const grouped = computed(() => {
  const map = new Map()
  for (const c of filtered.value) {
    const k = c.category || '其他'
    if (!map.has(k)) map.set(k, [])
    map.get(k).push(c)
  }
  return [...map.entries()].sort(
    (a, b) => (CATS.indexOf(a[0]) + 1 || 99) - (CATS.indexOf(b[0]) + 1 || 99)
  )
})

function open(name) {
  router.push({ path: '/posts', query: { competition: name } })
}

function levelTone(level) {
  if (!level) return ''
  if (level.includes('A 类')) return 'lv-a'
  if (level.includes('国际')) return 'lv-intl'
  if (level.includes('企业')) return 'lv-corp'
  return ''
}

function pickCat(c) {
  category.value = category.value === c ? '' : c
}
</script>

<template>
  <div class="comp-page">
    <PageHead
      :crumbs="[{ label: '首页', to: '/' }, { label: '竞赛名录' }]"
      title="竞赛名录"
      desc="90 场高水平竞赛的标准名与常用叫法，选一场看看谁在组队"
    />

    <div class="comp-toolbar">
      <div class="head-search">
        <AppIcon name="search" :size="15" />
        <input v-model="keyword" placeholder="搜比赛名或别名，如「正大杯」「美赛」「蓝桥杯」" />
      </div>
    </div>

    <div class="cat-row">
      <button
        class="chip chip-live"
        :class="{ 'chip-on': onlyActive }"
        @click="onlyActive = !onlyActive"
      >
        有队伍在招
        <span v-if="activeCount" class="live-count">{{ activeCount }}</span>
      </button>
      <button class="chip" :class="{ 'chip-on': !category }" @click="category = ''">全部</button>
      <button
        v-for="c in cats"
        :key="c"
        class="chip"
        :class="{ 'chip-on': category === c }"
        @click="pickCat(c)"
      >
        {{ c }}
      </button>
    </div>

    <div v-if="loading" class="comp-list">
      <div v-for="i in 6" :key="i" class="comp-item skeleton" />
    </div>

    <div v-else-if="!filtered.length" class="empty">
      <AppIcon name="search" :size="26" />
      <p>没找到这场比赛。你可以在发布招募时直接填写名字，我们会保留你的写法。</p>
    </div>

    <div v-else class="comp-groups">
      <section v-for="[cat, items] in grouped" :key="cat" class="comp-group">
        <div class="group-head">
          <h3>{{ cat }}</h3>
          <span class="group-count">{{ items.length }}</span>
        </div>
        <div class="comp-list">
          <button v-for="c in items" :key="c.name" class="comp-item" @click="open(c.name)">
            <span class="comp-main">
              <span class="comp-name">{{ c.name }}</span>
              <span v-if="c.aliases && c.aliases.length" class="comp-alias">
                也叫 {{ c.aliases.slice(0, 3).join(' / ') }}
              </span>
            </span>
            <span class="comp-right">
              <span v-if="counts[c.name]" class="teams-live">{{ counts[c.name] }} 队在招</span>
              <span v-if="c.level" class="lv" :class="levelTone(c.level)">{{ c.level }}</span>
              <AppIcon name="chevronRight" :size="15" />
            </span>
          </button>
        </div>
      </section>
    </div>

    <div class="comp-tip">
      <AppIcon name="sparkles" :size="14" />
      名录里没有的比赛，发布时直接写名字就行，不用等我们收录。
    </div>
  </div>
</template>

<style scoped>
.comp-toolbar {
  margin-bottom: 12px;
}

.comp-toolbar .head-search {
  max-width: 460px;
}

.head-search {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.head-search svg {
  position: absolute;
  left: 12px;
  color: #a3aaba;
  pointer-events: none;
}

.head-search input {
  width: 100%;
  height: 44px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: #fff;
  padding: 0 12px 0 36px;
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: all 0.18s ease;
}

.head-search input:focus {
  border-color: #b9c0da;
  box-shadow: 0 0 0 4px rgba(78, 85, 121, 0.07);
}

.cat-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.comp-groups {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.group-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-left: 2px;
}

.group-head h3 {
  font-size: 13px;
  font-weight: 700;
  color: #414963;
  letter-spacing: 0.01em;
}

.group-count {
  font-size: 11px;
  color: #8f97ab;
  background: #eef1f8;
  border-radius: 6px;
  padding: 1px 6px;
}

.comp-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  text-align: left;
  padding: 12px 14px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.comp-item:hover {
  border-color: #c3cbe4;
  box-shadow: 0 6px 16px rgba(30, 41, 71, 0.06);
}

.comp-item:active {
  transform: scale(0.995);
}

.comp-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.comp-name {
  font-size: 13.5px;
  font-weight: 600;
  color: #1f2434;
  line-height: 1.35;
}

.comp-alias {
  font-size: 11.5px;
  color: #98a0b3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comp-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: none;
  color: #b6bccd;
}

.lv {
  font-size: 10.5px;
  font-weight: 600;
  border-radius: 6px;
  padding: 2px 6px;
  background: #f1f3f9;
  color: #6d7487;
  white-space: nowrap;
}

.teams-live {
  font-size: 10.5px;
  font-weight: 700;
  border-radius: 6px;
  padding: 2px 7px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  white-space: nowrap;
}

.live-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  margin-left: 4px;
  padding: 0 4px;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}

.lv-a {
  background: #e8f6f2;
  color: #0f766e;
}

.lv-intl {
  background: #eef0fe;
  color: #4f46b8;
}

.lv-corp {
  background: #fdf1e3;
  color: #b06a12;
}

.comp-tip {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin-top: 18px;
  padding: 11px 14px;
  font-size: 12px;
  line-height: 1.6;
  color: #6d7487;
  background: #f4f6fc;
  border-radius: 10px;
}

.comp-tip svg {
  flex: none;
  margin-top: 3px;
}

.skeleton {
  height: 54px;
  background: linear-gradient(90deg, #f2f4fa 25%, #e9edf7 37%, #f2f4fa 63%);
  background-size: 400% 100%;
  animation: sk 1.2s ease infinite;
}

@keyframes sk {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0 50%;
  }
}

@media (min-width: 1000px) {
  .comp-page {
    max-width: 1180px;
  }

  .comp-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 10px;
  }

  .comp-toolbar .head-search {
    max-width: 380px;
  }
}

@media (max-width: 860px) {
  .comp-toolbar .head-search {
    max-width: none;
  }

  .cat-row {
    overflow-x: auto;
    flex-wrap: nowrap;
    scrollbar-width: none;
    padding-bottom: 2px;
  }

  .cat-row::-webkit-scrollbar {
    display: none;
  }

  .cat-row .chip {
    flex: none;
  }

  .comp-item {
    padding: 11px 13px;
    gap: 8px;
  }

  .comp-right .lv {
    font-size: 10px;
    padding: 2px 5px;
  }

  /* 窄屏上「几队在招」更有用，级别徽章让位，避免比赛名被挤成两行 */
  .comp-right .teams-live ~ .lv {
    display: none;
  }
}
</style>
