<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'
import { GRADE_TEXT, ROLE_TEXT, STAGE_TEXT, roleLabel, stageLabel, gradeLabel } from '../utils'
import PageHead from '../components/PageHead.vue'
import PostCard from '../components/PostCard.vue'
import AppIcon from '../components/AppIcon.vue'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const total = ref([])
const loading = ref(true)
const failed = ref(false)
const meta = ref({ competitions: [], roles: [], grades: [], stages: [] })
const sheetOpen = ref(false)
const compQuery = ref('')

const TYPES = [
  { value: '', label: '全部' },
  { value: 'team', label: '找队友' },
  { value: 'join', label: '找队伍' }
]

const filters = reactive({
  type: '',
  q: '',
  competition: '',
  role: '',
  grade: '',
  stage: '',
  sort: 'recent'
})

const ROLES = Object.entries(ROLE_TEXT).map(([code, label]) => ({ code, label }))
const GRADES = Object.entries(GRADE_TEXT).map(([code, label]) => ({ code, label }))
const STAGES = Object.entries(STAGE_TEXT).map(([code, label]) => ({ code, label }))

const activeCount = computed(
  () => [filters.competition, filters.role, filters.grade, filters.stage].filter(Boolean).length
)

const compSuggestions = computed(() => {
  const q = compQuery.value.trim().toLowerCase()
  const all = meta.value.competitions || []
  if (!q) return []
  return all
    .filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.aliases || []).some((a) => a.toLowerCase().includes(q))
    )
    .slice(0, 10)
})

const hotComps = computed(() =>
  (meta.value.competitions || [])
    .filter((c) => (c.level || '').includes('国家级'))
    .slice(0, 6)
)

const chips = computed(() => {
  const out = []
  if (filters.competition) out.push({ key: 'competition', label: filters.competition })
  if (filters.role) out.push({ key: 'role', label: '缺 ' + roleLabel(filters.role) })
  if (filters.grade) out.push({ key: 'grade', label: gradeLabel(filters.grade) })
  if (filters.stage) out.push({ key: 'stage', label: stageLabel(filters.stage) })
  return out
})

function buildQuery() {
  const q = {}
  if (filters.type) q.type = filters.type
  if (filters.q) q.q = filters.q
  if (filters.competition) q.competition = filters.competition
  if (filters.role) q.role = filters.role
  if (filters.grade) q.grade = filters.grade
  if (filters.stage) q.stage = filters.stage
  if (filters.sort === 'match') q.sort = 'match'
  return q
}

function syncFromRoute() {
  const q = route.query
  filters.type = String(q.type || '')
  filters.q = String(q.q || '')
  filters.competition = String(q.competition || '')
  filters.role = String(q.role || '')
  filters.grade = String(q.grade || '')
  filters.stage = String(q.stage || '')
  filters.sort = q.sort === 'match' ? 'match' : 'recent'
}

function push() {
  router.replace({ path: '/posts', query: buildQuery() })
}

function setType(v) {
  filters.type = v
  push()
}

function setSort(v) {
  filters.sort = v
  push()
}

function pickCompetition(name) {
  filters.competition = filters.competition === name ? '' : name
  compQuery.value = ''
}

function clearChip(key) {
  filters[key] = ''
  push()
}

function resetAll() {
  filters.competition = ''
  filters.role = ''
  filters.grade = ''
  filters.stage = ''
  filters.type = ''
  filters.sort = 'recent'
  push()
  sheetOpen.value = false
}

async function load() {
  loading.value = true
  failed.value = false
  try {
    const qs = new URLSearchParams()
    Object.entries(buildQuery()).forEach(([k, v]) => v && qs.set(k, v))
    const suffix = qs.toString() ? '?' + qs.toString() : ''
    posts.value = await api('/posts' + suffix)
  } catch (e) {
    failed.value = true
  } finally {
    loading.value = false
  }
}

const counts = computed(() => {
  const c = { '': total.value.length, team: 0, join: 0 }
  total.value.forEach((p) => {
    c[p.type] = (c[p.type] || 0) + 1
  })
  return c
})

async function loadTotals() {
  try {
    total.value = await api('/posts')
  } catch (e) {
    /* 计数失败不影响列表 */
  }
}

onMounted(async () => {
  syncFromRoute()
  try {
    meta.value = await api('/meta')
  } catch (e) {
    /* 选项拉不到也不影响浏览 */
  }
  await load()
  loadTotals()
})

watch(
  () => route.query,
  () => {
    syncFromRoute()
    load()
  }
)
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '首页', to: '/' }, { label: '招募广场' }]"
      title="招募广场"
      desc="按比赛、位置、年级筛选，一眼看到最适合你的队伍"
    >
      <template #actions>
        <router-link v-if="auth.user" to="/publish" class="btn btn-primary only-desktop">
          <AppIcon name="plus" :size="16" />
          发布招募
        </router-link>
      </template>
    </PageHead>

    <div class="board">
      <div class="board-bar">
        <div class="chip-row">
          <button
            v-for="t in TYPES"
            :key="t.value"
            class="chip"
            :class="{ active: filters.type === t.value }"
            @click="setType(t.value)"
          >
            {{ t.label }}
            <span class="chip-count">{{ counts[t.value] || 0 }}</span>
          </button>
        </div>

        <div class="bar-right">
          <button
            v-if="auth.user"
            class="sort-btn"
            :class="{ active: filters.sort === 'match' }"
            @click="setSort(filters.sort === 'match' ? 'recent' : 'match')"
          >
            <AppIcon name="sparkles" :size="14" />
            {{ filters.sort === 'match' ? '匹配优先' : '最新发布' }}
          </button>
          <button class="filter-btn" :class="{ active: activeCount }" @click="sheetOpen = true">
            <AppIcon name="filter" :size="15" />
            筛选
            <span v-if="activeCount" class="filter-count">{{ activeCount }}</span>
          </button>
        </div>
      </div>

      <div v-if="chips.length" class="chip-row active-chips">
        <button v-for="c in chips" :key="c.key" class="chip chip-on" @click="clearChip(c.key)">
          {{ c.label }}
          <AppIcon name="close" :size="12" />
        </button>
        <button class="link-btn" @click="resetAll">清空</button>
      </div>

      <div v-if="loading" class="post-grid">
        <div v-for="i in 6" :key="i" class="card skeleton-card">
          <div class="skeleton" style="width: 58px; height: 58px; border-radius: 13px" />
          <div style="flex: 1">
            <div class="skeleton" style="height: 14px; width: 72%" />
            <div class="skeleton" style="height: 12px; width: 44%; margin-top: 10px" />
          </div>
        </div>
      </div>

      <div v-else-if="failed" class="card">
        <div class="empty">
          <div class="empty-art"><AppIcon name="alert" :size="34" /></div>
          <div class="empty-title">加载失败</div>
          <p class="empty-desc">请确认后端服务已启动，然后重试</p>
          <button class="btn btn-ghost btn-sm" style="margin-top: 6px" @click="load">重新加载</button>
        </div>
      </div>

      <div v-else-if="posts.length" class="post-grid">
        <PostCard v-for="p in posts" :key="p.id" :post="p" />
      </div>

      <div v-else class="card">
        <div class="empty">
          <div class="empty-art"><AppIcon name="search" :size="34" /></div>
          <div class="empty-title">没有符合条件的招募</div>
          <p class="empty-desc">放宽一点筛选条件，或者成为第一个发布的人</p>
          <button v-if="activeCount || filters.type" class="btn btn-ghost btn-sm" style="margin-top: 6px" @click="resetAll">
            清空筛选
          </button>
          <router-link v-if="auth.user" to="/publish" class="btn btn-primary btn-sm" style="margin-top: 6px">
            发布招募
          </router-link>
        </div>
      </div>
    </div>

    <!-- 筛选面板 -->
    <transition name="sheet">
      <div v-if="sheetOpen" class="sheet-mask" @click.self="sheetOpen = false">
        <div class="sheet">
          <div class="sheet-head">
            <div class="sheet-title">高级筛选</div>
            <button class="icon-btn" @click="sheetOpen = false"><AppIcon name="close" /></button>
          </div>

          <div class="sheet-body">
            <div class="sheet-group">
              <div class="sheet-label">比赛</div>
              <div v-if="filters.competition" class="picked">
                <AppIcon name="flag" :size="13" />
                {{ filters.competition }}
                <button class="link-btn" @click="filters.competition = ''">重选</button>
              </div>
              <template v-else>
                <input v-model="compQuery" class="input" placeholder="搜比赛名或别名，如「正大杯」「美赛」" />
                <div v-if="compQuery.trim()" class="sug-list">
                  <button
                    v-for="c in compSuggestions"
                    :key="c.name"
                    class="sug"
                    @click="pickCompetition(c.name)"
                  >
                    <span class="sug-name">{{ c.name }}</span>
                    <span class="sug-meta">{{ c.level }} · {{ c.category }}</span>
                  </button>
                  <div v-if="!compSuggestions.length" class="sug-empty">没找到这场比赛的记录，可先随便选或直接在发布时自填</div>
                </div>
                <template v-else>
                  <div class="hot-comps">
                    <button v-for="c in hotComps" :key="c.name" class="hot-chip" @click="pickCompetition(c.name)">
                      {{ c.name }}
                    </button>
                  </div>
                  <div class="sheet-hint">
                    点一下常用比赛直接筛选，或输入关键词找其他比赛
                    <router-link to="/competitions" class="hint-link" @click="sheetOpen = false">
                      浏览全部名录 →
                    </router-link>
                  </div>
                </template>
              </template>
            </div>

            <div class="sheet-group">
              <div class="sheet-label">缺什么位置</div>
              <div class="chip-row">
                <button
                  v-for="r in ROLES"
                  :key="r.code"
                  class="chip chip-sm"
                  :class="{ active: filters.role === r.code }"
                  @click="filters.role = filters.role === r.code ? '' : r.code"
                >
                  {{ r.label }}
                </button>
              </div>
            </div>

            <div class="sheet-group">
              <div class="sheet-label">年级要求</div>
              <div class="chip-row">
                <button
                  v-for="g in GRADES"
                  :key="g.code"
                  class="chip chip-sm"
                  :class="{ active: filters.grade === g.code }"
                  @click="filters.grade = filters.grade === g.code ? '' : g.code"
                >
                  {{ g.label }}
                </button>
              </div>
              <div class="sheet-hint">选了年级后，没写年级要求的招募仍会显示</div>
            </div>

            <div class="sheet-group">
              <div class="sheet-label">比赛阶段</div>
              <div class="chip-row">
                <button
                  v-for="s in STAGES"
                  :key="s.code"
                  class="chip chip-sm"
                  :class="{ active: filters.stage === s.code }"
                  @click="filters.stage = filters.stage === s.code ? '' : s.code"
                >
                  {{ s.label }}
                </button>
              </div>
            </div>
          </div>

          <div class="sheet-foot">
            <button class="btn btn-ghost" @click="resetAll">重置</button>
            <button class="btn btn-primary" @click="sheetOpen = false; push()">
              查看结果
              <span v-if="activeCount" class="foot-count">{{ activeCount }} 个条件</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.board {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.board-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.bar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chip-count {
  font-size: 11px;
  font-weight: 600;
  padding: 0 6px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.05);
  margin-left: 2px;
}

.chip.active .chip-count {
  background: rgba(255, 255, 255, 0.2);
}

.chip-on {
  background: #fff;
  border: 1px solid #dfe3f0;
  color: #4a5270;
  gap: 4px;
}

.chip-sm {
  height: 30px;
  font-size: 12.5px;
  padding: 0 12px;
}

.sort-btn,
.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid var(--line-strong);
  background: #fff;
  color: #5d6580;
  font-size: 12.5px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
}

.sort-btn.active,
.filter-btn.active {
  border-color: transparent;
  background: var(--accent-soft);
  color: var(--accent);
}

.filter-count {
  min-width: 16px;
  height: 16px;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  font-size: 10px;
  line-height: 16px;
  text-align: center;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.skeleton-card {
  display: flex;
  gap: 13px;
  padding: 18px;
  align-items: flex-start;
}

/* 筛选面板 */
.sheet-mask {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(22, 27, 40, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.sheet {
  width: 100%;
  max-width: 520px;
  max-height: 84vh;
  background: #fff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.sheet-head {
  display: flex;
  align-items: center;
  padding: 16px 18px 8px;
}

.sheet-title {
  font-size: 15.5px;
  font-weight: 700;
  color: #1e2333;
}

.sheet-head .icon-btn {
  margin-left: auto;
}

.sheet-body {
  padding: 6px 18px 18px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sheet-label {
  font-size: 12.5px;
  font-weight: 700;
  color: #3a4157;
  margin-bottom: 9px;
}

.sheet-hint {
  margin-top: 7px;
  font-size: 11.5px;
  color: var(--text-3);
}

.sug-list {
  margin-top: 8px;
  max-height: 190px;
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: 12px;
}

.hot-comps {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}

.hot-chip {
  min-width: 0;
  height: 32px;
  padding: 0 11px;
  border: 1px solid var(--line-strong);
  border-radius: 9px;
  background: #fff;
  color: #4a5169;
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: left;
  transition: all 0.16s ease;
}

.hot-chip:hover {
  border-color: var(--accent);
  color: var(--accent-strong);
  background: var(--accent-soft);
}

.hint-link {
  margin-left: 6px;
  color: var(--accent-strong);
  font-weight: 600;
  text-decoration: none;
}

.hint-link:hover {
  text-decoration: underline;
}

.sug {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  width: 100%;
  padding: 10px 12px;
  border: 0;
  border-bottom: 1px solid #f4f5f9;
  background: #fff;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
}

.sug:last-child {
  border-bottom: 0;
}

.sug:hover {
  background: #f7f9fd;
}

.sug-name {
  font-size: 13px;
  font-weight: 600;
  color: #262b3c;
}

.sug-meta {
  font-size: 11px;
  color: var(--text-3);
}

.sug-empty {
  padding: 12px;
  font-size: 12px;
  color: var(--text-3);
}

.picked {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #2b3247;
  background: #f5f7fd;
  border-radius: 10px;
  padding: 10px 12px;
}

.picked .link-btn {
  margin-left: auto;
  font-size: 12px;
}

.sheet-foot {
  display: flex;
  gap: 10px;
  padding: 12px 18px calc(14px + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid var(--line);
}

.sheet-foot .btn {
  flex: 1;
}

.foot-count {
  opacity: 0.85;
  font-weight: 500;
}

.sheet-enter-active,
.sheet-leave-active {
  transition: opacity 0.2s ease;
}

.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
}

@media (max-width: 1100px) {
  .post-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .post-grid {
    grid-template-columns: 1fr;
  }

  .sheet-mask {
    padding: 0;
    align-items: flex-end;
  }

  .sheet {
    max-width: none;
    border-radius: 20px 20px 0 0;
    max-height: 88vh;
  }

  .sheet-body {
    gap: 18px;
  }

  .sheet-enter-active .sheet,
  .sheet-leave-active .sheet {
    transition: transform 0.24s ease;
  }

  .sheet-enter-from .sheet,
  .sheet-leave-to .sheet {
    transform: translateY(24px);
  }
}
</style>
