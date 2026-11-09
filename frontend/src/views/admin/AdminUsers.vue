<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { adminApi } from '../../api'
import { fmtDate, thousand } from '../../utils'
import { err, ok } from '../../toast'
import AppIcon from '../../components/AppIcon.vue'
import PageHead from '../../components/PageHead.vue'
import UserAvatar from '../../components/UserAvatar.vue'
import ConfirmDialog from '../../components/ConfirmDialog.vue'

const users = ref([])
const counts = reactive({ all: 0, active: 0, disabled: 0 })
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const status = ref('')
const loading = ref(true)
const busy = ref(false)

const dialog = ref({ show: false, action: '', user: null })
const editing = ref(null)
const editName = ref('')
const savingName = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const FILTERS = [
  { value: '', label: '全部用户' },
  { value: 'active', label: '正常' },
  { value: 'disabled', label: '已禁用' }
]

async function load() {
  loading.value = true
  try {
    const qs = new URLSearchParams()
    if (keyword.value.trim()) qs.set('q', keyword.value.trim())
    if (status.value) qs.set('status', status.value)
    qs.set('page', page.value)
    qs.set('page_size', pageSize.value)
    const data = await adminApi('/admin/users?' + qs.toString())
    users.value = data.items
    total.value = data.total
    Object.assign(counts, data.counts || {})
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

function setStatus(v) {
  status.value = v
  page.value = 1
  load()
}

function search() {
  page.value = 1
  load()
}

function go(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  load()
}

function askDeactivate(u) {
  dialog.value = { show: true, action: 'deactivate', user: u }
}

async function activate(u) {
  busy.value = true
  try {
    await adminApi(`/admin/users/${u.id}/activate`, { method: 'POST' })
    ok('已恢复该用户')
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

async function confirmDialog() {
  const u = dialog.value.user
  if (!u) return
  busy.value = true
  try {
    await adminApi(`/admin/users/${u.id}/deactivate`, { method: 'POST' })
    ok('已禁用该用户')
    dialog.value = { show: false, action: '', user: null }
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}

function startEdit(u) {
  editing.value = u
  editName.value = u.name
}

async function saveName() {
  const name = editName.value.trim()
  if (name.length < 2) {
    err('姓名至少 2 个字')
    return
  }
  savingName.value = true
  try {
    await adminApi(`/admin/users/${editing.value.id}`, { method: 'PATCH', body: { name } })
    ok('用户信息已更新')
    editing.value = null
    await load()
  } catch (e) {
    err(e.message)
  } finally {
    savingName.value = false
  }
}

watch(pageSize, () => {
  page.value = 1
  load()
})

onMounted(load)
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '管理后台', to: '/admin' }, { label: '用户管理' }]"
      title="用户管理"
      desc="管理平台注册用户账号，可编辑姓名或禁用违规账号"
    >
      <template #actions>
        <div class="head-search">
          <AppIcon name="search" :size="15" />
          <input v-model="keyword" placeholder="搜索用户名 / 学号…" @keyup.enter="search" />
        </div>
        <select v-model="status" class="select filter-select" @change="setStatus(status)">
          <option v-for="f in FILTERS" :key="f.value" :value="f.value">{{ f.label }}</option>
        </select>
      </template>
    </PageHead>

    <div class="stat-grid mini">
      <div class="mini-card">
        <span class="mini-label">全部用户</span>
        <span class="mini-value">{{ thousand(counts.all) }}</span>
      </div>
      <div class="mini-card">
        <span class="mini-label">正常</span>
        <span class="mini-value green">{{ thousand(counts.active) }}</span>
      </div>
      <div class="mini-card">
        <span class="mini-label">已禁用</span>
        <span class="mini-value red">{{ thousand(counts.disabled) }}</span>
      </div>
    </div>

    <div class="card table-card">
      <div class="table-scroll">
        <table class="table">
          <thead>
            <tr>
              <th style="width: 46%">用户</th>
              <th>学号</th>
              <th>角色</th>
              <th>发布数</th>
              <th>注册时间</th>
              <th>状态</th>
              <th style="text-align: right">操作</th>
            </tr>
          </thead>
          <tbody v-if="loading">
            <tr v-for="i in 5" :key="i">
              <td colspan="7"><div class="skeleton" style="height: 18px; width: 100%" /></td>
            </tr>
          </tbody>
          <tbody v-else-if="users.length">
            <tr v-for="u in users" :key="u.id">
              <td>
                <div class="cell-user">
                  <UserAvatar :name="u.name" :size="36" />
                  <div>
                    <div class="cell-name">{{ u.name }}</div>
                    <div class="cell-sub">ID {{ u.id }}</div>
                  </div>
                </div>
              </td>
              <td class="mono">{{ u.student_id }}</td>
              <td><span class="pill pill-neutral">{{ u.role }}</span></td>
              <td class="mono">{{ u.post_count }}</td>
              <td class="muted">{{ fmtDate(u.created_at) }}</td>
              <td>
                <span class="status-text" :class="u.active ? 'on' : 'off'">
                  <i class="dot" />{{ u.active ? '正常' : '已禁用' }}
                </span>
              </td>
              <td>
                <div class="row-ops">
                  <button class="link-op" @click="startEdit(u)">编辑</button>
                  <button v-if="u.active" class="link-op danger" @click="askDeactivate(u)">禁用</button>
                  <button v-else class="link-op" @click="activate(u)">启用</button>
                </div>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="7">
                <div class="empty" style="padding: 40px 0">
                  <div class="empty-art"><AppIcon name="users" :size="30" /></div>
                  <div class="empty-title">没有符合条件的用户</div>
                  <p class="empty-desc">换个关键词或筛选条件试试</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-foot">
        <span class="foot-info">共 {{ total }} 条</span>
        <div class="pager">
          <button class="pager-btn" :disabled="page <= 1" @click="go(page - 1)">
            <AppIcon name="chevronLeft" :size="14" />
          </button>
          <span class="pager-now">{{ page }} / {{ totalPages }}</span>
          <button class="pager-btn" :disabled="page >= totalPages" @click="go(page + 1)">
            <AppIcon name="chevronRight" :size="14" />
          </button>
        </div>
        <select v-model.number="pageSize" class="select size-select">
          <option :value="10">10 / 页</option>
          <option :value="20">20 / 页</option>
          <option :value="50">50 / 页</option>
        </select>
      </div>
    </div>

    <ConfirmDialog
      :show="dialog.show"
      title="禁用该用户？"
      :desc="`禁用后 ${dialog.user?.name || ''} 将无法登录和发布招募，已有内容会保留。`"
      confirm-text="禁用账号"
      danger
      :loading="busy"
      @cancel="dialog = { show: false, action: '', user: null }"
      @confirm="confirmDialog"
    />

    <transition name="overlay">
      <div v-if="editing" class="overlay" @click.self="editing = null">
        <div class="modal">
          <h3 class="modal-title">编辑用户姓名</h3>
          <p class="modal-desc">仅修改展示名称，学号与账号状态不受影响。</p>
          <div style="margin-top: 4px">
            <input v-model="editName" class="input" maxlength="20" placeholder="请输入姓名" @keyup.enter="saveName" />
          </div>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="editing = null">取消</button>
            <button class="btn btn-primary" :disabled="savingName" @click="saveName">
              {{ savingName ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.head-search {
  position: relative;
  display: flex;
  align-items: center;
  width: 230px;
}

.head-search svg {
  position: absolute;
  left: 12px;
  color: #a3aaba;
  pointer-events: none;
}

.head-search input {
  width: 100%;
  height: 42px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: #fff;
  padding: 0 12px 0 36px;
  font-size: 13px;
  font-family: inherit;
  outline: none;
}

.head-search input:focus {
  border-color: #b9c0da;
  box-shadow: 0 0 0 4px rgba(78, 85, 121, 0.07);
}

.filter-select {
  width: 128px;
  height: 42px;
}

.stat-grid.mini {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.mini-card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  padding: 12px 18px;
  display: flex;
  align-items: center;
  gap: 18px;
  min-width: 156px;
  box-shadow: var(--shadow-sm);
}

.mini-label {
  font-size: 12.5px;
  color: var(--text-3);
}

.mini-value {
  margin-left: auto;
  font-size: 20px;
  font-weight: 750;
  letter-spacing: -0.03em;
  color: #22283a;
  font-variant-numeric: tabular-nums;
}

.mini-value.green {
  color: var(--green);
}

.mini-value.red {
  color: var(--red);
}

.table-card {
  overflow: hidden;
}

.table-scroll {
  overflow-x: auto;
}

.cell-name {
  font-size: 13px;
  font-weight: 650;
  color: #262b3c;
}

.cell-sub {
  font-size: 11px;
  color: #b0b7c6;
  margin-top: 1px;
}

.mono {
  font-variant-numeric: tabular-nums;
  font-size: 12.5px;
  color: #4d5468;
}

.muted {
  font-size: 12.5px;
  color: #8b92a5;
}

.status-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
}

.status-text.on {
  color: var(--green);
}

.status-text.off {
  color: #9aa1b2;
}

.row-ops {
  display: flex;
  gap: 14px;
  justify-content: flex-end;
}

.link-op {
  border: 0;
  background: transparent;
  font-size: 12.5px;
  font-family: inherit;
  color: #5b6486;
  cursor: pointer;
  padding: 2px 0;
}

.link-op:hover {
  color: var(--accent);
}

.link-op.danger:hover {
  color: var(--red);
}

.table-foot {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  border-top: 1px solid #f4f5f9;
}

.foot-info {
  font-size: 12px;
  color: #9aa1b2;
}

.pager {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pager-now {
  font-size: 12px;
  color: #5b6486;
  min-width: 42px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.size-select {
  width: 96px;
  height: 34px;
  font-size: 12px;
}
</style>
