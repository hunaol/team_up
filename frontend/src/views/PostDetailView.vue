<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { admin, auth } from '../store'
import {
  CONTACT_TEXT,
  GRADE_TEXT,
  ROLE_TEXT,
  STAGE_TEXT,
  STAGE_TONE,
  TYPE_TEXT,
  copyText,
  daysLeft,
  descToHtml,
  fmtDate,
  gradeLabel,
  relTime,
  roleLabel,
  stageLabel
} from '../utils'
import { err, ok } from '../toast'
import AppIcon from '../components/AppIcon.vue'
import StatusPill from '../components/StatusPill.vue'
import UserAvatar from '../components/UserAvatar.vue'
import MatchBadge from '../components/MatchBadge.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageHead from '../components/PageHead.vue'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(true)
const notFound = ref(false)
const reveal = ref(false)
const busy = ref(false)
const dialog = ref({ show: false, action: '' })

const applyOpen = ref(false)
const applyForm = ref({ message: '', resume: '' })
const applications = ref([])
const applicantsLoading = ref(false)
const candidates = ref([])
const candidatesLoading = ref(false)
const tab = ref('detail') // 详情 / 收到的申请（队长）/ 候选人

const isOwner = computed(() => !!post.value && !!auth.user && post.value.author_id === auth.user.id)
/** 只登录了管理员：可以看内容，但不能以学生身份申请/私信/收藏 */
const adminViewer = computed(() => !!admin.logged && !auth.user)
const isTeam = computed(() => post.value?.type === 'team')
const left = computed(() => daysLeft(post.value?.deadline))
const roles = computed(() => post.value?.roles || [])
const grades = computed(() => (post.value?.grade_req || []).map(gradeLabel))

const pendingCount = computed(() => applications.value.filter((a) => a.status === 'pending').length)

async function load() {
  loading.value = true
  notFound.value = false
  try {
    post.value = await api('/posts/' + route.params.id)
    if (isOwner.value) loadOwnerData()
  } catch (e) {
    if (e.status === 404) notFound.value = true
    else err(e.message)
  } finally {
    loading.value = false
  }
}

async function loadOwnerData() {
  applicantsLoading.value = true
  candidatesLoading.value = true
  try {
    applications.value = await api(`/posts/${post.value.id}/applications`)
  } catch (e) {
    /* ignore */
  } finally {
    applicantsLoading.value = false
  }
  try {
    candidates.value = isTeam.value ? await api(`/posts/${post.value.id}/candidates`) : []
  } catch (e) {
    candidates.value = []
  } finally {
    candidatesLoading.value = false
  }
}

async function toggleFavorite() {
  if (!auth.user) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  if (busy.value) return
  busy.value = true
  try {
    if (post.value.is_favorite) {
      await api(`/posts/${post.value.id}/favorite`, { method: 'DELETE' })
      post.value.is_favorite = false
      ok('已取消收藏')
    } else {
      await api(`/posts/${post.value.id}/favorite`, { method: 'POST' })
      post.value.is_favorite = true
      ok('已加入收藏')
    }
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

function toStudentLogin() {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

function openApply() {
  if (!auth.user) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  applyForm.value = {
    message: '',
    resume: ''
  }
  api('/auth/profile')
    .then((p) => {
      applyForm.value.resume = p.resume || ''
    })
    .catch(() => {})
  applyOpen.value = true
}

async function submitApply() {
  if (busy.value) return
  busy.value = true
  try {
    await api(`/posts/${post.value.id}/apply`, {
      method: 'POST',
      body: {
        message: applyForm.value.message.trim(),
        resume: applyForm.value.resume.trim()
      }
    })
    post.value.has_applied = true
    applyOpen.value = false
    ok('申请已发送，队长会在消息里回复你')
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

async function review(app, action) {
  busy.value = true
  try {
    await api(`/applications/${app.id}/${action}`, { method: 'POST' })
    ok(action === 'accept' ? '已通过申请' : '已婉拒')
    await loadOwnerData()
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

async function chat() {
  if (!auth.user) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  router.push({ path: `/messages/${post.value.author_id}`, query: { post: post.value.id } })
}

async function doAction(action) {
  busy.value = true
  try {
    if (action === 'down') {
      await api(`/posts/${post.value.id}/down`, { method: 'POST' })
      ok('已下架该招募')
    } else if (action === 'close') {
      await api(`/posts/${post.value.id}/close`, { method: 'POST' })
      ok('已标记为招满')
    } else if (action === 'delete') {
      await api(`/posts/${post.value.id}`, { method: 'DELETE' })
      ok('已删除')
      router.push('/my')
      return
    }
    dialog.value = { show: false, action: '' }
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

async function copyContact() {
  if (!post.value?.contact) return
  const done = await copyText(post.value.contact)
  done ? ok('联系方式已复制') : err('复制失败，请手动选择')
}

function ask(action) {
  dialog.value = { show: true, action }
}

const dialogMeta = computed(() => {
  switch (dialog.value.action) {
    case 'down':
      return { title: '下架这条招募？', desc: '下架后其他同学将无法在广场看到它，你可以随时重新发布。', text: '下架' }
    case 'close':
      return { title: '标记为已招满？', desc: '招募广场将显示“已招满”，不再接受新的申请。', text: '标记招满' }
    case 'delete':
      return { title: '删除这条招募？', desc: '删除后不可恢复，相关的收藏与申请也会一并移除。', text: '删除' }
    default:
      return { title: '', desc: '', text: '确认' }
  }
})

onMounted(load)
</script>

<template>
  <div>
    <PageHead :crumbs="[{ label: '首页', to: '/' }, { label: '招募广场', to: '/posts' }, { label: '招募详情' }]" title="招募详情" />

    <div v-if="loading" class="card card-pad">
      <div class="skeleton" style="height: 24px; width: 40%" />
      <div class="skeleton" style="height: 14px; width: 62%; margin-top: 16px" />
      <div class="skeleton" style="height: 14px; width: 52%; margin-top: 10px" />
      <div class="skeleton" style="height: 160px; width: 100%; margin-top: 22px" />
    </div>

    <div v-else-if="notFound" class="card">
      <div class="empty">
        <div class="empty-art"><AppIcon name="alert" :size="34" /></div>
        <div class="empty-title">这条招募不存在或已下架</div>
        <p class="empty-desc">它可能已被发布者删除，或超过了 30 天有效期</p>
        <router-link to="/posts" class="btn btn-primary btn-sm" style="margin-top: 6px">返回招募广场</router-link>
      </div>
    </div>

    <div v-else-if="post" class="detail">
      <div class="detail-left">
        <!-- 队长视角的标签页 -->
        <div v-if="isOwner" class="tabs owner-tabs">
          <button class="tab" :class="{ active: tab === 'detail' }" @click="tab = 'detail'">招募详情</button>
          <button class="tab" :class="{ active: tab === 'apps' }" @click="tab = 'apps'; loadOwnerData()">
            收到的申请
            <span v-if="pendingCount" class="tab-count">{{ pendingCount }}</span>
          </button>
          <button v-if="isTeam" class="tab" :class="{ active: tab === 'cand' }" @click="tab = 'cand'">
            匹配候选人
            <span v-if="candidates.length" class="tab-count">{{ candidates.length }}</span>
          </button>
        </div>

        <article v-if="tab === 'detail'" class="card detail-main">
          <div class="detail-head">
            <div class="detail-badges">
              <span class="pill pill-accent">{{ TYPE_TEXT[post.type] }}</span>
              <StatusPill :status="post.status" />
              <span v-if="post.stage" class="tag" :class="STAGE_TONE[post.stage]">{{ stageLabel(post.stage) }}</span>
              <MatchBadge v-if="post.match" :score="post.match.score" size="lg" />
            </div>
            <h1 class="detail-title">{{ post.title }}</h1>
            <div class="detail-meta">
              <span><AppIcon name="user" :size="13" />{{ post.author_name }}</span>
              <span><AppIcon name="clock" :size="13" />发布于 {{ fmtDate(post.created_at) }}</span>
              <span><AppIcon name="eye" :size="13" />{{ post.views }} 次浏览</span>
              <span v-if="post.deadline"><AppIcon name="calendar" :size="13" />截止 {{ post.deadline }}</span>
            </div>
          </div>

          <div v-if="post.competition || roles.length || grades.length || post.major_req || post.stage" class="facts">
            <div v-if="post.competition" class="fact fact-wide">
              <span class="fact-label"><AppIcon name="flag" :size="13" />比赛</span>
              <span class="fact-value">{{ post.competition }}</span>
            </div>
            <div v-if="roles.length" class="fact fact-wide">
              <span class="fact-label"><AppIcon name="users" :size="13" />{{ isTeam ? '缺什么位置' : '擅长方向' }}</span>
              <span class="tag-row">
                <span v-for="r in roles" :key="r" class="tag tag-accent">{{ roleLabel(r) }}</span>
              </span>
            </div>
            <div v-if="grades.length" class="fact">
              <span class="fact-label"><AppIcon name="user" :size="13" />年级</span>
              <span class="fact-value">{{ grades.join(' / ') }}</span>
            </div>
            <div v-if="post.major_req" class="fact">
              <span class="fact-label"><AppIcon name="building" :size="13" />专业</span>
              <span class="fact-value">{{ post.major_req }}</span>
            </div>
            <div v-if="post.stage" class="fact">
              <span class="fact-label"><AppIcon name="trend" :size="13" />阶段</span>
              <span class="fact-value">{{ stageLabel(post.stage) }}</span>
            </div>
            <div class="fact">
              <span class="fact-label"><AppIcon name="users" :size="13" />需求人数</span>
              <span class="fact-value">{{ post.need_num ? post.need_num + ' 人' : '不限' }}</span>
            </div>
          </div>

          <div v-if="post.match && post.match.reasons?.length" class="match-hint">
            <AppIcon name="sparkles" :size="14" />
            <span>{{ post.match.reasons.join(' · ') }}</span>
            <span v-if="post.match.missing?.length" class="miss">还差：{{ post.match.missing.join('、') }}</span>
          </div>

          <div v-if="post.deadline" class="countdown" :class="{ warn: left !== null && left <= 3 }">
            <AppIcon name="clock" :size="15" />
            <template v-if="left === null || left > 0">距离截止还有 <b>{{ left }}</b> 天，感兴趣就尽快联系吧</template>
            <template v-else>该招募的截止日期已过</template>
          </div>

          <div v-if="post.image" class="detail-cover">
            <img :src="post.image" :alt="post.title" />
          </div>

          <div class="detail-body">
            <h2 class="detail-subtitle">招募说明</h2>
            <div class="rich" v-html="descToHtml(post.description)"></div>
          </div>
        </article>

        <!-- 收到的申请 -->
        <div v-else-if="tab === 'apps'" class="card detail-main">
          <div class="panel-head">
            <div>
              <h2 class="detail-subtitle" style="margin: 0">收到的申请</h2>
              <p class="panel-sub">通过后会通过站内私信通知对方，并展示完整简历</p>
            </div>
            <button class="btn btn-ghost btn-sm" @click="loadOwnerData">刷新</button>
          </div>

          <div v-if="applicantsLoading" class="panel-body">
            <div v-for="i in 3" :key="i" class="skeleton" style="height: 72px; margin-bottom: 10px; border-radius: 12px" />
          </div>

          <div v-else-if="applications.length" class="app-list">
            <div v-for="a in applications" :key="a.id" class="app-card">
              <div class="app-top">
                <UserAvatar :name="a.applicant.name" :size="38" />
                <div class="app-who">
                  <div class="app-name">
                    {{ a.applicant.name }}
                    <span v-if="a.match_score != null" class="match-chip" :class="a.match_score >= 75 ? 'high' : a.match_score >= 50 ? 'mid' : 'low'">
                      匹配 {{ a.match_score }}%
                    </span>
                  </div>
                  <div class="app-sub">
                    {{ a.applicant.grade ? gradeLabel(a.applicant.grade) : '年级未填' }}
                    · {{ a.applicant.major || '专业未填' }}
                    · {{ relTime(a.created_at) }}
                  </div>
                </div>
                <span class="app-status" :class="a.status">
                  {{ a.status === 'pending' ? '待处理' : a.status === 'accepted' ? '已通过' : '已婉拒' }}
                </span>
              </div>

              <div v-if="a.applicant.skills?.length" class="tag-row" style="margin-top: 10px">
                <span v-for="s in a.applicant.skills" :key="s" class="tag">{{ roleLabel(s) }}</span>
              </div>

              <p v-if="a.message" class="app-msg">{{ a.message }}</p>
              <p v-if="a.resume" class="app-resume">{{ a.resume }}</p>

              <div v-if="a.status === 'pending'" class="app-actions">
                <button class="btn btn-danger-soft btn-sm" :disabled="busy" @click="review(a, 'reject')">婉拒</button>
                <button class="btn btn-primary btn-sm" :disabled="busy" @click="review(a, 'accept')">通过</button>
              </div>
            </div>
          </div>

          <div v-else class="empty" style="padding: 40px 0">
            <div class="empty-art"><AppIcon name="users" :size="32" /></div>
            <div class="empty-title">还没有人申请</div>
            <p class="empty-desc">完善招募里的位置与年级要求，会更容易被匹配到</p>
          </div>
        </div>

        <!-- 匹配候选人 -->
        <div v-else class="card detail-main">
          <div class="panel-head">
            <div>
              <h2 class="detail-subtitle" style="margin: 0">系统匹配的候选人</h2>
              <p class="panel-sub">按「找队伍」帖的技能与你缺的位置自动排序</p>
            </div>
            <button class="btn btn-ghost btn-sm" @click="loadOwnerData">刷新</button>
          </div>

          <div v-if="candidatesLoading" class="panel-body">
            <div v-for="i in 3" :key="i" class="skeleton" style="height: 68px; margin-bottom: 10px; border-radius: 12px" />
          </div>

          <div v-else-if="candidates.length" class="cand-list">
            <router-link v-for="c in candidates" :key="c.id" :to="`/post/${c.id}`" class="cand-row">
              <UserAvatar :name="c.author_name" :size="36" />
              <div class="cand-body">
                <div class="cand-title">{{ c.author_name }} · {{ c.title }}</div>
                <div class="cand-tags">
                  <span v-for="r in c.roles" :key="r" class="tag">{{ roleLabel(r) }}</span>
                </div>
              </div>
              <span class="match-chip" :class="c.match.score >= 75 ? 'high' : c.match.score >= 50 ? 'mid' : 'low'">
                {{ c.match.score }}%
              </span>
            </router-link>
          </div>

          <div v-else class="empty" style="padding: 40px 0">
            <div class="empty-art"><AppIcon name="search" :size="32" /></div>
            <div class="empty-title">暂时没有匹配的候选人</div>
            <p class="empty-desc">等更多同学发布「找队伍」后，这里会自动出现合适的人</p>
          </div>
        </div>
      </div>

      <aside class="detail-aside">
        <section class="card aside-card">
          <div class="aside-head">
            <UserAvatar :name="post.author_name" :size="42" />
            <div>
              <div class="aside-title">{{ post.author_name }}</div>
              <div class="aside-sub">
                {{ post.author?.grade ? gradeLabel(post.author.grade) : '校园认证用户' }}
                <template v-if="post.author?.major"> · {{ post.author.major }}</template>
              </div>
            </div>
          </div>
          <p v-if="post.author?.bio" class="author-bio">{{ post.author.bio }}</p>
          <div v-if="post.author?.skills?.length" class="tag-row" style="margin-bottom: 12px">
            <span v-for="s in post.author.skills.slice(0, 4)" :key="s" class="tag">{{ roleLabel(s) }}</span>
          </div>
          <div class="aside-meta">
            <span>发布于 {{ fmtDate(post.created_at) }}</span>
            <span>{{ post.views }} 次浏览</span>
          </div>
          <p class="aside-note">
            {{ adminViewer ? '管理员审核可见，请勿外传学生联系方式。' : '联系方式仅登录用户可见，请文明沟通。' }}
          </p>
        </section>

        <section v-if="!isOwner && !adminViewer" class="card aside-card">
          <template v-if="post.status === 'open'">
            <button v-if="!post.has_applied" class="btn btn-primary btn-block" @click="openApply">
              <AppIcon name="send" :size="15" />
              申请加入并附上简历
            </button>
            <div v-else class="applied-tip">
              <AppIcon name="check" :size="15" />
              已提交申请，等待队长回复
            </div>
            <button class="btn btn-ghost btn-block" style="margin-top: 8px" @click="chat">
              <AppIcon name="chat" :size="15" />
              私信发布者
            </button>
          </template>
          <button class="btn btn-ghost btn-block" style="margin-top: 8px" :disabled="busy" @click="toggleFavorite">
            <AppIcon name="heart" :size="15" />
            {{ post.is_favorite ? '取消收藏' : '收藏这条招募' }}
          </button>
        </section>

        <section v-if="!isOwner && adminViewer" class="card aside-card admin-view-tip">
          <div class="aside-label">管理员浏览模式</div>
          <p>你可以查看全部内容与联系方式用于审核；申请、私信、收藏需要学生账号。</p>
          <div class="admin-view-actions">
            <router-link v-if="post.status === 'down' || post.status === 'expired'" to="/admin/posts" class="btn btn-ghost btn-sm">
              <AppIcon name="list" :size="14" />
              去招募管理
            </router-link>
            <router-link to="/login?redirect=" class="btn btn-ghost btn-sm" @click.prevent="toStudentLogin">
              <AppIcon name="user" :size="14" />
              用学生账号登录
            </router-link>
          </div>
        </section>

        <section class="card aside-card contact-card">
          <div class="aside-label">{{ CONTACT_TEXT[post.contact_type] }}</div>
          <div v-if="post.contact" class="contact-value">
            <span class="contact-text">{{ reveal ? post.contact : '•'.repeat(Math.min(post.contact.length, 11)) }}</span>
            <button class="btn btn-ghost btn-xs" @click="reveal = !reveal">
              <AppIcon :name="reveal ? 'eye' : 'lock'" :size="13" />
              {{ reveal ? '隐藏' : '显示' }}
            </button>
          </div>
          <div v-else class="contact-locked">
            <AppIcon name="lock" :size="15" />
            <span>登录后可查看联系方式</span>
          </div>

          <button class="btn btn-primary btn-block" style="margin-top: 14px" :disabled="!post.contact" @click="copyContact">
            <AppIcon name="link" :size="15" />
            复制联系方式
          </button>
        </section>

        <section v-if="isOwner" class="card aside-card">
          <div class="aside-label">管理这条招募</div>
          <router-link
            v-if="post.status === 'open'"
            :to="`/post/${post.id}/edit`"
            class="btn btn-ghost btn-block"
            style="margin-top: 10px"
          >
            <AppIcon name="edit" :size="15" />编辑内容
          </router-link>
          <button
            v-if="post.status === 'open'"
            class="btn btn-ghost btn-block"
            style="margin-top: 8px"
            @click="ask('close')"
          >
            <AppIcon name="check" :size="15" />标记为已招满
          </button>
          <button
            v-if="post.status === 'open'"
            class="btn btn-danger-soft btn-block"
            style="margin-top: 8px"
            @click="ask('down')"
          >
            <AppIcon name="download" :size="15" />下架招募
          </button>
          <button
            v-if="post.status === 'open' || post.status === 'full'"
            class="btn btn-danger-soft btn-block"
            style="margin-top: 8px"
            @click="ask('delete')"
          >
            <AppIcon name="trash" :size="15" />删除
          </button>
        </section>
      </aside>
    </div>

    <!-- 申请弹窗 -->
    <div v-if="applyOpen" class="apply-mask" @click.self="applyOpen = false">
      <div class="apply-box">
        <div class="apply-head">
          <div class="apply-title">申请加入「{{ post.title }}」</div>
          <button class="icon-btn" @click="applyOpen = false"><AppIcon name="close" /></button>
        </div>
        <div class="apply-body">
          <label class="apply-label">自荐语</label>
          <textarea
            v-model="applyForm.message"
            class="textarea"
            rows="3"
            maxlength="500"
            placeholder="简单介绍你的相关经验、能投入的时间，让队长更快了解你"
          />
          <label class="apply-label" style="margin-top: 14px">简历 / 经历</label>
          <textarea
            v-model="applyForm.resume"
            class="textarea"
            rows="5"
            maxlength="2000"
            placeholder="获奖、项目、技能证书等，会自动带上你个人资料里的简历"
          />
          <p class="apply-hint">申请会以站内私信同时通知队长，通过后会再次提醒你。</p>
        </div>
        <div class="apply-foot">
          <button class="btn btn-ghost" @click="applyOpen = false">取消</button>
          <button class="btn btn-primary" :disabled="busy" @click="submitApply">
            {{ busy ? '提交中…' : '发送申请' }}
          </button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="dialog.show"
      :title="dialogMeta.title"
      :desc="dialogMeta.desc"
      :confirm-text="dialogMeta.text"
      :danger="dialog.action !== 'close'"
      :loading="busy"
      @cancel="dialog = { show: false, action: '' }"
      @confirm="doAction(dialog.action)"
    />
  </div>
</template>

<style scoped>
.detail {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 318px;
  gap: 18px;
  align-items: start;
}

.detail-left {
  min-width: 0;
}

.owner-tabs {
  margin-bottom: 12px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0 6px;
}

.detail-main {
  padding: 28px 30px 32px;
}

.detail-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.detail-title {
  font-size: 24px;
  font-weight: 750;
  letter-spacing: -0.03em;
  line-height: 1.35;
  color: #1a1f2e;
}

.detail-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  font-size: 12px;
  color: #98a0b3;
}

.detail-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.facts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
  padding: 14px;
  background: #f8f9fd;
  border: 1px solid #eef0f7;
  border-radius: 14px;
}

.fact {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.fact-wide {
  grid-column: span 3;
}

.fact-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: #98a0b3;
}

.fact-value {
  font-size: 13px;
  font-weight: 650;
  color: #2b3247;
  word-break: break-word;
}

.match-hint {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-wrap: wrap;
  margin-top: 14px;
  padding: 10px 13px;
  border-radius: 11px;
  background: var(--accent-soft);
  color: #0b7f75;
  font-size: 12.5px;
  font-weight: 600;
}

.match-hint .miss {
  color: #a06a2c;
  font-weight: 500;
}

.countdown {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 18px;
  padding: 11px 15px;
  border-radius: 11px;
  background: #f4f6fc;
  border: 1px solid #e8ecf7;
  font-size: 12.5px;
  color: #5d6584;
}

.countdown b {
  color: #3b4668;
  font-size: 14px;
}

.countdown.warn {
  background: #fef6ee;
  border-color: #f8e6cf;
  color: #a9702c;
}

.detail-cover {
  margin-top: 20px;
  border-radius: 14px;
  overflow: hidden;
  height: 240px;
  background: #f4f6fb;
}

.detail-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-body {
  margin-top: 26px;
}

.detail-subtitle {
  font-size: 14px;
  font-weight: 700;
  color: #262b3c;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-subtitle::before {
  content: "";
  width: 3px;
  height: 14px;
  border-radius: 3px;
  background: var(--primary);
}

.panel-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-head .btn {
  margin-left: auto;
}

.panel-sub {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 5px;
}

.rich {
  font-size: 13.5px;
  line-height: 1.95;
  color: #454c62;
  word-break: break-word;
}

.rich :deep(b) {
  color: #262b3c;
}

.rich :deep(img) {
  display: block;
  max-width: 100%;
  margin: 10px 0;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.detail-aside {
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: sticky;
  top: calc(var(--topbar-h) + 8px);
}

.aside-card {
  padding: 20px;
}

.aside-head {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 12px;
}

.aside-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0 12px;
  border-top: 1px solid var(--line);
  font-size: 12px;
  color: var(--text-3);
}

.aside-meta span + span::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #ccd2de;
  margin-right: 12px;
  vertical-align: middle;
}

.aside-title {
  font-size: 13.5px;
  font-weight: 650;
  color: #262b3c;
}

.aside-sub {
  font-size: 11.5px;
  color: var(--text-3);
}

.author-bio {
  font-size: 12.5px;
  color: var(--text-2);
  line-height: 1.7;
  margin-bottom: 10px;
}

.aside-note {
  font-size: 12px;
  color: var(--text-3);
  line-height: 1.7;
}

.admin-view-tip p {
  font-size: 12.5px;
  color: var(--text-3);
  line-height: 1.7;
  margin-top: 8px;
}

.admin-view-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.aside-label {
  font-size: 11.5px;
  letter-spacing: 0.08em;
  color: var(--text-3);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 10px;
}

.contact-value {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
}

.contact-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #2b3247;
  font-variant-numeric: tabular-nums;
  word-break: break-all;
}

.contact-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text-3);
  background: #f8f9fd;
  border-radius: 10px;
  padding: 12px;
}

.applied-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  height: 40px;
  border-radius: 10px;
  background: var(--green-soft);
  color: #0a8f63;
  font-size: 12.5px;
  font-weight: 600;
}

/* 申请列表 */
.app-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.app-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px;
  background: #fff;
}

.app-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-who {
  min-width: 0;
  flex: 1;
}

.app-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  font-weight: 650;
  color: #232838;
  flex-wrap: wrap;
}

.app-sub {
  font-size: 11.5px;
  color: var(--text-3);
  margin-top: 3px;
}

.app-status {
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--surface-2);
  color: var(--text-3);
  flex: none;
}

.app-status.accepted {
  background: var(--green-soft);
  color: #0a8f63;
}

.app-status.rejected {
  background: var(--red-soft);
  color: #c92845;
}

.app-status.pending {
  background: var(--orange-soft);
  color: #a86a00;
}

.app-msg {
  margin-top: 10px;
  font-size: 12.5px;
  color: #454c62;
  line-height: 1.7;
  background: #f8f9fd;
  border-radius: 10px;
  padding: 10px 12px;
}

.app-resume {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-2);
  line-height: 1.75;
  white-space: pre-wrap;
  max-height: 150px;
  overflow: auto;
}

.app-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

/* 候选人 */
.cand-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cand-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 11px 12px;
  border: 1px solid var(--line);
  border-radius: 12px;
  transition: all 0.16s ease;
}

.cand-row:hover {
  background: #f9fafd;
  border-color: #e2e7f3;
}

.cand-body {
  flex: 1;
  min-width: 0;
}

.cand-title {
  font-size: 13px;
  font-weight: 600;
  color: #262b3c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cand-tags {
  display: flex;
  gap: 5px;
  margin-top: 5px;
  flex-wrap: wrap;
}

/* 申请弹窗 */
.apply-mask {
  position: fixed;
  inset: 0;
  z-index: 85;
  background: rgba(22, 27, 40, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.apply-box {
  width: 100%;
  max-width: 520px;
  max-height: 86vh;
  background: #fff;
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.apply-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 18px 10px;
}

.apply-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #1e2333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apply-head .icon-btn {
  margin-left: auto;
  flex: none;
}

.apply-body {
  padding: 4px 18px 14px;
  overflow-y: auto;
}

.apply-label {
  display: block;
  font-size: 12.5px;
  font-weight: 650;
  color: #3a4157;
  margin-bottom: 7px;
}

.apply-hint {
  margin-top: 12px;
  font-size: 11.5px;
  color: var(--text-3);
  line-height: 1.7;
}

.apply-foot {
  display: flex;
  gap: 10px;
  padding: 12px 18px calc(14px + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid var(--line);
}

.apply-foot .btn {
  flex: 1;
}

@media (max-width: 1000px) {
  .detail {
    grid-template-columns: 1fr;
  }
  .detail-aside {
    position: static;
  }
}

@media (max-width: 860px) {
  .facts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .fact-wide {
    grid-column: span 2;
  }
  .apply-mask {
    padding: 0;
    align-items: flex-end;
  }
  .apply-box {
    max-width: none;
    border-radius: 18px 18px 0 0;
    max-height: 88vh;
  }
}
</style>
