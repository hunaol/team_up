<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth, badge, logout, setUser } from '../store'
import { CONTACT_PLACEHOLDER, CONTACT_TEXT, GRADE_TEXT, ROLE_TEXT, TYPE_TEXT, gradeLabel, relTime, roleLabel } from '../utils'
import { err, ok } from '../toast'
import PageHead from '../components/PageHead.vue'
import AppIcon from '../components/AppIcon.vue'
import UserAvatar from '../components/UserAvatar.vue'

const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const meta = ref({ competitions: [], majors: [] })
const profile = ref({
  name: '',
  student_id: '',
  grade: '',
  major: '',
  skills: [],
  interests: [],
  bio: '',
  resume: '',
  contact_type: 'wechat',
  contact: '',
  open_to_match: true
})
const myApplications = ref([])
const compQuery = ref('')

const ROLES = Object.entries(ROLE_TEXT).map(([code, label]) => ({ code, label }))
const GRADES = Object.entries(GRADE_TEXT).map(([code, label]) => ({ code, label }))

const completeness = computed(() => {
  const p = profile.value
  const checks = [
    !!p.grade,
    !!p.major,
    p.skills.length > 0,
    p.interests.length > 0,
    !!p.bio,
    !!p.resume,
    !!p.contact
  ]
  return Math.round((checks.filter(Boolean).length / checks.length) * 100)
})

const compSuggestions = computed(() => {
  const q = compQuery.value.trim().toLowerCase()
  const all = meta.value.competitions || []
  const pool = q
    ? all.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          (c.aliases || []).some((a) => a.toLowerCase().includes(q))
      )
    : all
  return pool.filter((c) => !profile.value.interests.includes(c.name)).slice(0, 8)
})

function toggleSkill(code) {
  const i = profile.value.skills.indexOf(code)
  if (i >= 0) profile.value.skills.splice(i, 1)
  else profile.value.skills.push(code)
}

function addInterest(name) {
  if (!profile.value.interests.includes(name)) profile.value.interests.push(name)
  compQuery.value = ''
}

function removeInterest(name) {
  profile.value.interests = profile.value.interests.filter((n) => n !== name)
}

async function load() {
  loading.value = true
  try {
    const [p, apps] = await Promise.all([
      api('/auth/profile'),
      api('/my/applications').catch(() => [])
    ])
    profile.value = { ...profile.value, ...p }
    myApplications.value = apps
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

async function save() {
  if (saving.value) return
  saving.value = true
  try {
    const p = await api('/auth/profile', {
      method: 'PUT',
      body: {
        grade: profile.value.grade,
        major: profile.value.major,
        skills: profile.value.skills,
        interests: profile.value.interests,
        bio: profile.value.bio,
        resume: profile.value.resume,
        contact_type: profile.value.contact_type,
        contact: profile.value.contact,
        open_to_match: profile.value.open_to_match
      }
    })
    profile.value = { ...profile.value, ...p }
    setUser({ ...auth.user, name: p.name, id: p.id })
    ok('资料已保存，匹配度会更准')
  } catch (e) {
    err(e.message)
  } finally {
    saving.value = false
  }
}

async function onLogout() {
  await logout()
  ok('已退出登录')
  router.push('/')
}

onMounted(async () => {
  try {
    meta.value = await api('/meta')
  } catch (e) {
    /* ignore */
  }
  await load()
})
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '首页', to: '/' }, { label: '我的资料' }]"
      title="我的资料"
      desc="资料越完整，系统给你的匹配度越准，也越容易被队长搜到"
    >
      <template #actions>
        <router-link to="/my" class="btn btn-ghost btn-sm">
          <AppIcon name="file" :size="14" />我的发布
        </router-link>
      </template>
    </PageHead>

    <div v-if="loading" class="card card-pad">
      <div class="skeleton" style="height: 76px; width: 100%" />
      <div class="skeleton" style="height: 44px; width: 70%; margin-top: 16px" />
    </div>

    <div v-else class="profile-grid">
      <div class="profile-main">
        <section class="card who-card">
          <UserAvatar :name="profile.name" :size="56" />
          <div class="who-meta">
            <div class="who-name">{{ profile.name }}</div>
            <div class="who-sub">
              {{ profile.student_id }}
              <template v-if="profile.grade"> · {{ gradeLabel(profile.grade) }}</template>
              <template v-if="profile.major"> · {{ profile.major }}</template>
            </div>
          </div>
          <div class="who-meter">
            <div class="meter-bar"><i :style="{ width: completeness + '%' }" /></div>
            <span>资料完整度 {{ completeness }}%</span>
          </div>
        </section>

        <section class="card card-pad">
          <h2 class="block-title">基本信息</h2>

          <div class="field">
            <div class="field-label">年级</div>
            <div class="field-body">
              <div class="chip-row">
                <button
                  v-for="g in GRADES"
                  :key="g.code"
                  class="chip chip-sm"
                  :class="{ active: profile.grade === g.code }"
                  @click="profile.grade = profile.grade === g.code ? '' : g.code"
                >
                  {{ g.label }}
                </button>
              </div>
            </div>
          </div>

          <div class="field">
            <div class="field-label">专业</div>
            <div class="field-body">
              <input v-model="profile.major" class="input" maxlength="40" placeholder="如：工商管理 / 计算机科学与技术" />
              <div class="chip-row" style="margin-top: 8px">
                <button
                  v-for="m in meta.majors"
                  :key="m"
                  class="tag"
                  style="cursor: pointer; border: 0"
                  @click="profile.major = m"
                >
                  {{ m }}
                </button>
              </div>
            </div>
          </div>

          <div class="field">
            <div class="field-label">擅长 / 兴趣位置</div>
            <div class="field-body">
              <div class="chip-row">
                <button
                  v-for="r in ROLES"
                  :key="r.code"
                  class="chip chip-sm"
                  :class="{ active: profile.skills.includes(r.code) }"
                  @click="toggleSkill(r.code)"
                >
                  <AppIcon v-if="profile.skills.includes(r.code)" name="check" :size="12" />
                  {{ r.label }}
                </button>
              </div>
              <div class="field-hint">勾选你能承担的位置，系统据此给你的匹配度打分</div>
            </div>
          </div>
        </section>

        <section class="card card-pad">
          <h2 class="block-title">意向比赛</h2>
          <div class="field">
            <div class="field-label">比赛</div>
            <div class="field-body">
              <div v-if="profile.interests.length" class="chip-row" style="margin-bottom: 10px">
                <button
                  v-for="name in profile.interests"
                  :key="name"
                  class="chip chip-sm active"
                  @click="removeInterest(name)"
                >
                  {{ name }}
                  <AppIcon name="close" :size="12" />
                </button>
              </div>
              <input v-model="compQuery" class="input" placeholder="搜比赛名或别名，如「正大杯」「美赛」「市调」" />
              <div class="sug-list">
                <button v-for="c in compSuggestions" :key="c.name" class="sug" @click="addInterest(c.name)">
                  <span class="sug-name">{{ c.name }}</span>
                  <span class="sug-meta">{{ c.level }}</span>
                </button>
                <div v-if="!compSuggestions.length" class="sug-empty">没有更多可添加的比赛了</div>
              </div>
            </div>
          </div>
        </section>

        <section class="card card-pad">
          <h2 class="block-title">介绍与简历</h2>
          <div class="field">
            <div class="field-label">一句话介绍</div>
            <div class="field-body">
              <textarea v-model="profile.bio" class="textarea" rows="2" maxlength="300" placeholder="如：擅长问卷设计与数据分析，带队拿过市调省一" />
            </div>
          </div>
          <div class="field">
            <div class="field-label">简历 / 经历</div>
            <div class="field-body">
              <textarea
                v-model="profile.resume"
                class="textarea"
                rows="6"
                maxlength="2000"
                placeholder="竞赛获奖、项目经历、技能证书…申请加入队伍时会自动带上这份简历"
              />
            </div>
          </div>
        </section>

        <section class="card card-pad">
          <h2 class="block-title">联系方式</h2>
          <div class="field">
            <div class="field-label">联系方式</div>
            <div class="field-body">
              <div class="contact-row">
                <select v-model="profile.contact_type" class="select contact-type">
                  <option v-for="(label, key) in CONTACT_TEXT" :key="key" :value="key">{{ label }}</option>
                </select>
                <input v-model="profile.contact" class="input" :placeholder="CONTACT_PLACEHOLDER[profile.contact_type]" />
              </div>
              <div class="field-hint">通过申请后，队长可以直接看到你的联系方式</div>
            </div>
          </div>
          <div class="switch-row">
            <div>
              <div class="switch-title">开放匹配</div>
              <div class="switch-desc">允许系统把你推荐给正在招人的队伍</div>
            </div>
            <button class="switch" :class="{ on: profile.open_to_match }" @click="profile.open_to_match = !profile.open_to_match">
              <i />
            </button>
          </div>
        </section>

        <div class="save-bar">
          <button class="btn btn-primary btn-lg" :disabled="saving" @click="save">
            {{ saving ? '保存中…' : '保存资料' }}
          </button>
        </div>
      </div>

      <aside class="profile-aside">
        <section class="card aside-card">
          <div class="aside-label">我发出的申请</div>
          <div v-if="myApplications.length" class="mini-list">
            <router-link v-for="a in myApplications" :key="a.id" :to="`/post/${a.post.id}`" class="mini-row">
              <div class="mini-body">
                <div class="mini-title">{{ a.post.title }}</div>
                <div class="mini-sub">{{ TYPE_TEXT[a.post.type] }} · {{ relTime(a.created_at) }}</div>
              </div>
              <span class="mini-status" :class="a.status">
                {{ a.status === 'pending' ? '待回复' : a.status === 'accepted' ? '已通过' : '已婉拒' }}
              </span>
            </router-link>
          </div>
          <p v-else class="aside-empty">还没有申请过队伍，去广场看看吧</p>
          <router-link to="/posts" class="btn btn-ghost btn-block btn-sm" style="margin-top: 10px">
            去招募广场
          </router-link>
        </section>

        <section class="card aside-card">
          <div class="aside-label">快捷入口</div>
          <router-link to="/my" class="side-link"><AppIcon name="file" :size="15" />我的发布</router-link>
          <router-link to="/favorites" class="side-link"><AppIcon name="bookmark" :size="15" />我的收藏</router-link>
          <router-link to="/messages" class="side-link">
            <AppIcon name="chat" :size="15" />我的消息
            <span v-if="badge.unread" class="mini-badge">{{ badge.unread }}</span>
          </router-link>
          <button class="side-link danger" @click="onLogout"><AppIcon name="logout" :size="15" />退出登录</button>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 18px;
  align-items: start;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.who-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  flex-wrap: wrap;
}

.who-meta {
  min-width: 0;
  flex: 1;
}

.who-name {
  font-size: 17px;
  font-weight: 750;
  color: #1e2333;
}

.who-sub {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 3px;
}

.who-meter {
  min-width: 160px;
  text-align: right;
}

.meter-bar {
  height: 6px;
  border-radius: 99px;
  background: #eef0f7;
  overflow: hidden;
}

.meter-bar i {
  display: block;
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--teal), var(--cyan));
  transition: width 0.3s ease;
}

.who-meter span {
  font-size: 11.5px;
  color: var(--text-3);
  display: block;
  margin-top: 6px;
}

.block-title {
  font-size: 14px;
  font-weight: 700;
  color: #262b3c;
  margin-bottom: 14px;
  padding-left: 10px;
  position: relative;
}

.block-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 3px;
  bottom: 3px;
  width: 3px;
  border-radius: 3px;
  background: var(--primary);
}

.chip-sm {
  height: 30px;
  font-size: 12.5px;
  padding: 0 12px;
}

.contact-row {
  display: flex;
  gap: 10px;
}

.contact-type {
  width: 112px;
  flex: none;
}

.sug-list {
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: 12px;
}

.sug {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 12px;
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
  flex: 1;
  font-size: 12.5px;
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

.switch-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
  margin-top: 6px;
}

.switch-title {
  font-size: 13px;
  font-weight: 650;
  color: #2b3143;
}

.switch-desc {
  font-size: 11.5px;
  color: var(--text-3);
  margin-top: 2px;
}

.switch {
  margin-left: auto;
  width: 44px;
  height: 26px;
  border-radius: 999px;
  border: 0;
  background: #dfe3ee;
  position: relative;
  cursor: pointer;
  transition: background 0.2s ease;
  flex: none;
}

.switch i {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s ease;
  box-shadow: 0 1px 3px rgba(20, 26, 46, 0.2);
}

.switch.on {
  background: var(--accent);
}

.switch.on i {
  transform: translateX(18px);
}

.save-bar {
  display: flex;
  justify-content: flex-end;
}

.save-bar .btn {
  min-width: 180px;
}

.profile-aside {
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: sticky;
  top: calc(var(--topbar-h) + 8px);
}

.aside-card {
  padding: 18px;
}

.aside-label {
  font-size: 11.5px;
  letter-spacing: 0.08em;
  color: var(--text-3);
  font-weight: 600;
  margin-bottom: 12px;
  text-transform: uppercase;
}

.mini-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border: 1px solid var(--line);
  border-radius: 10px;
}

.mini-row:hover {
  background: #f9fafd;
}

.mini-body {
  min-width: 0;
  flex: 1;
}

.mini-title {
  font-size: 12.5px;
  font-weight: 600;
  color: #2b3143;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-sub {
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
}

.mini-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--surface-2);
  color: var(--text-3);
  flex: none;
}

.mini-status.accepted {
  background: var(--green-soft);
  color: #0a8f63;
}

.mini-status.rejected {
  background: var(--red-soft);
  color: #c92845;
}

.mini-status.pending {
  background: var(--orange-soft);
  color: #a86a00;
}

.aside-empty {
  font-size: 12px;
  color: var(--text-3);
  line-height: 1.7;
}

.side-link {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 9px 10px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #5b6276;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
}

.side-link:hover {
  background: #f3f4fa;
  color: #333a52;
}

.side-link.danger:hover {
  background: #fdf0f3;
  color: var(--red);
}

.mini-badge {
  margin-left: auto;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--red);
  color: #fff;
  font-size: 10.5px;
  line-height: 18px;
  text-align: center;
}

@media (max-width: 1000px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  .profile-aside {
    position: static;
  }
}

@media (max-width: 860px) {
  .who-meter {
    min-width: 100%;
    text-align: left;
  }
  .save-bar .btn {
    width: 100%;
  }
}
</style>
