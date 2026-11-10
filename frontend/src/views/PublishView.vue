<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, uploadImage } from '../api'
import {
  CONTACT_PLACEHOLDER,
  CONTACT_TEXT,
  GRADE_TEXT,
  ROLE_TEXT,
  STAGE_TEXT,
  htmlToText,
  textToHtml,
  descToHtml
} from '../utils'
import { err, ok } from '../toast'
import PageHead from '../components/PageHead.vue'
import AppIcon from '../components/AppIcon.vue'
import RichEditor from '../components/RichEditor.vue'

const route = useRoute()
const router = useRouter()

const editId = computed(() => route.params.id)
const isEdit = computed(() => !!editId.value)

const form = reactive({
  type: 'team',
  title: '',
  description: '',
  need_num: '',
  contact_type: 'wechat',
  contact: '',
  deadline: '',
  image: '',
  competition: '',
  roles: [],
  grade_req: [],
  major_req: '',
  stage: ''
})

const errors = reactive({})
const saving = ref(false)
const loading = ref(false)
const uploading = ref(false)
const coverInput = ref(null)
const meta = ref({ competitions: [], majors: [] })
const compFocused = ref(false)

const titleLen = computed(() => form.title.trim().length)
const descLen = computed(() => htmlToText(form.description).replace(/\s/g, '').length)

const TYPES = [
  { value: 'team', label: '找队友', desc: '我在组建队伍' },
  { value: 'join', label: '找队伍', desc: '我想加入队伍' }
]

const ROLES = Object.entries(ROLE_TEXT).map(([code, label]) => ({ code, label }))
const GRADES = Object.entries(GRADE_TEXT).map(([code, label]) => ({ code, label }))
const STAGES = Object.entries(STAGE_TEXT).map(([code, label]) => ({ code, label }))

const roleTitle = computed(() => (form.type === 'team' ? '缺什么位置' : '我能做什么'))
const roleHint = computed(() =>
  form.type === 'team'
    ? '勾选需要队友补的位置，系统会据此推荐候选人'
    : '勾选你擅长的能力，队长更容易通过匹配度找到你'
)

const compSuggestions = computed(() => {
  const q = form.competition.trim().toLowerCase()
  const all = meta.value.competitions || []
  if (!q) return all.slice(0, 6)
  const hit = all.filter(
    (c) =>
      c.name.toLowerCase().includes(q) ||
      (c.aliases || []).some((a) => a.toLowerCase().includes(q))
  )
  return hit.slice(0, 8)
})

const compExact = computed(() =>
  (meta.value.competitions || []).some((c) => c.name === form.competition)
)

function toggle(list, code) {
  const i = list.indexOf(code)
  if (i >= 0) list.splice(i, 1)
  else list.push(code)
}

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (titleLen.value < 2) errors.title = '招募名称至少 2 个字'
  if (titleLen.value > 50) errors.title = '招募名称不能超过 50 个字'
  if (descLen.value < 10) errors.description = '招募描述至少 10 个字'
  if (descLen.value > 500) errors.description = '招募描述不能超过 500 个字'
  if (form.need_num !== '' && form.need_num !== null) {
    const n = Number(form.need_num)
    if (!Number.isInteger(n) || n < 1 || n > 99) errors.need_num = '需求人数需为 1–99 的整数'
  }
  const contact = form.contact.trim()
  if (contact.length < 5) errors.contact = '联系方式至少 5 个字符'
  else if (form.contact_type === 'qq' && !/^\d{5,12}$/.test(contact)) errors.contact = 'QQ 号需为 5–12 位数字'
  else if (form.contact_type === 'phone' && !/^1[3-9]\d{9}$/.test(contact)) errors.contact = '手机号格式不正确'
  return Object.keys(errors).length === 0
}

function pickCover() {
  coverInput.value?.click()
}

async function onCover(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    err('封面图不能超过 2MB')
    return
  }
  uploading.value = true
  try {
    form.image = await uploadImage(file)
    ok('封面上传成功')
  } catch (e2) {
    err(e2.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function submit() {
  if (!validate()) {
    err('请检查表单中的提示信息')
    return
  }
  saving.value = true
  try {
    const payload = {
      type: form.type,
      title: form.title.trim(),
      description: form.description,
      need_num: form.need_num === '' ? null : Number(form.need_num),
      contact_type: form.contact_type,
      contact: form.contact.trim(),
      deadline: form.deadline || null,
      image: form.image || null,
      competition: form.competition.trim() || null,
      roles: form.roles,
      grade_req: form.grade_req,
      major_req: form.major_req || null,
      stage: form.stage || null
    }
    if (isEdit.value) {
      delete payload.type
      await api('/posts/' + editId.value, { method: 'PATCH', body: payload })
      ok('修改已保存')
    } else {
      await api('/posts', { method: 'POST', body: payload })
      ok('发布成功，快去看看效果吧')
    }
    router.push('/my')
  } catch (e) {
    err(e.message)
  } finally {
    saving.value = false
  }
}

async function loadForEdit() {
  loading.value = true
  try {
    const p = await api('/posts/' + editId.value)
    form.type = p.type
    form.title = p.title
    form.description = p.description
    form.need_num = p.need_num ?? ''
    form.contact_type = p.contact_type
    form.contact = p.contact || ''
    form.deadline = p.deadline || ''
    form.image = p.image || ''
    form.competition = p.competition || ''
    form.roles = p.roles || []
    form.grade_req = p.grade_req || []
    form.major_req = p.major_req || ''
    form.stage = p.stage || ''
  } catch (e) {
    err(e.message)
    router.push('/my')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    meta.value = await api('/meta')
  } catch (e) {
    /* 名录拉不到也能自填 */
  }
  if (isEdit.value) loadForEdit()
})
</script>

<template>
  <div>
    <PageHead
      :crumbs="[
        { label: '首页', to: '/' },
        { label: isEdit ? '编辑招募' : '发布招募' }
      ]"
      :title="isEdit ? '编辑招募' : '发布招募'"
      :desc="isEdit ? '更新你的招募信息，让更多同学看到' : '填得越结构化，越容易被对的人搜到'"
    />

    <div v-if="loading" class="card card-pad">
      <div class="skeleton" style="height: 44px; width: 40%" />
      <div class="skeleton" style="height: 44px; width: 100%; margin-top: 18px" />
      <div class="skeleton" style="height: 180px; width: 100%; margin-top: 18px" />
    </div>

    <form v-else class="card form-card" @submit.prevent="submit">
      <div class="form-body">
        <div class="field">
          <div class="field-label">招募类型<span class="req">*</span></div>
          <div class="field-body">
            <div class="chip-row">
              <button
                v-for="t in TYPES"
                :key="t.value"
                type="button"
                class="chip"
                :class="{ active: form.type === t.value }"
                :disabled="isEdit"
                @click="form.type = t.value"
              >
                <AppIcon v-if="form.type === t.value" name="check" :size="14" />
                {{ t.label }}
              </button>
            </div>
            <div class="field-hint">
              {{ form.type === 'team' ? '你正在组建队伍，寻找合适的队友加入' : '你希望加入一支已有的队伍，一起参加比赛' }}
            </div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">参加的比赛<span class="opt">选填</span></div>
          <div class="field-body">
            <div class="comp-box">
              <div class="comp-input">
                <AppIcon name="flag" :size="15" />
                <input
                  v-model="form.competition"
                  placeholder="搜比赛名或别名，如「正大杯」「市调」「美赛」"
                  @focus="compFocused = true"
                  @blur="compFocused = false"
                />
                <button
                  v-if="form.competition"
                  type="button"
                  class="comp-clear"
                  @click="form.competition = ''"
                >
                  <AppIcon name="close" :size="13" />
                </button>
              </div>
              <div v-if="compFocused && !compExact && compSuggestions.length" class="comp-sug">
                <button
                  v-for="c in compSuggestions"
                  :key="c.name"
                  type="button"
                  @mousedown.prevent="form.competition = c.name; compFocused = false"
                >
                  <span class="sug-name">{{ c.name }}</span>
                  <span class="sug-meta">{{ c.level }}</span>
                </button>
              </div>
            </div>
            <div class="field-hint">
              从名录里选可以避免「市调 / 正大杯」各写各的，别人按别名也能搜到你
            </div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">比赛阶段<span class="opt">选填</span></div>
          <div class="field-body">
            <div class="chip-row">
              <button
                v-for="s in STAGES"
                :key="s.code"
                type="button"
                class="chip chip-sm"
                :class="{ active: form.stage === s.code }"
                @click="form.stage = form.stage === s.code ? '' : s.code"
              >
                {{ s.label }}
              </button>
            </div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">{{ roleTitle }}<span class="opt">选填</span></div>
          <div class="field-body">
            <div class="chip-row">
              <button
                v-for="r in ROLES"
                :key="r.code"
                type="button"
                class="chip chip-sm"
                :class="{ active: form.roles.includes(r.code) }"
                @click="toggle(form.roles, r.code)"
              >
                <AppIcon v-if="form.roles.includes(r.code)" name="check" :size="12" />
                {{ r.label }}
              </button>
            </div>
            <div class="field-hint">{{ roleHint }}</div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">年级要求<span class="opt">选填</span></div>
          <div class="field-body">
            <div class="chip-row">
              <button
                v-for="g in GRADES"
                :key="g.code"
                type="button"
                class="chip chip-sm"
                :class="{ active: form.grade_req.includes(g.code) }"
                @click="toggle(form.grade_req, g.code)"
              >
                {{ g.label }}
              </button>
            </div>
            <div class="field-row" style="margin-top: 10px">
              <input
                v-model="form.major_req"
                class="input"
                placeholder="专业要求，如「经管类」，留空表示不限"
                maxlength="40"
              />
            </div>
            <div class="field-hint">不勾选年级表示不限；专业要求会作为匹配依据之一</div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">招募名称<span class="req">*</span></div>
          <div class="field-body">
            <input
              v-model="form.title"
              class="input"
              :class="{ invalid: errors.title }"
              maxlength="50"
              placeholder="请输入招募名称，如：正大杯市调 招募数据分析与答辩"
            />
            <div class="field-foot">
              <span v-if="errors.title" class="field-error">{{ errors.title }}</span>
              <span v-else class="field-hint">一句话说明比赛和目标，更容易被找到</span>
              <span class="counter" :class="{ over: titleLen > 50 }">{{ titleLen }} / 50</span>
            </div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">
            招募描述<span class="req">*</span>
            <span class="opt">10–500 字</span>
          </div>
          <div class="field-body">
            <RichEditor v-model="form.description" :max-text="500" placeholder="请描述比赛方向、队友要求、时间安排等，越具体越容易匹配…" />
            <div v-if="errors.description" class="field-error" style="margin-top: 8px">{{ errors.description }}</div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">
            需求人数<span class="opt">选填</span>
          </div>
          <div class="field-body">
            <div class="field-row">
              <div>
                <input
                  v-model="form.need_num"
                  class="input"
                  :class="{ invalid: errors.need_num }"
                  type="number"
                  min="1"
                  max="99"
                  placeholder="1–99"
                />
                <div v-if="errors.need_num" class="field-error">{{ errors.need_num }}</div>
                <div v-else class="field-hint">还差几人，留空表示不限</div>
              </div>
              <div>
                <div class="contact-row">
                  <select v-model="form.contact_type" class="select contact-type">
                    <option v-for="(label, key) in CONTACT_TEXT" :key="key" :value="key">{{ label }}</option>
                  </select>
                  <input
                    v-model="form.contact"
                    class="input"
                    :class="{ invalid: errors.contact }"
                    :placeholder="CONTACT_PLACEHOLDER[form.contact_type]"
                  />
                </div>
                <div v-if="errors.contact" class="field-error">{{ errors.contact }}</div>
                <div v-else class="field-hint">登录用户可在详情页查看并复制</div>
              </div>
            </div>
          </div>
        </div>

        <div class="field">
          <div class="field-label">
            报名截止<span class="opt">选填</span>
          </div>
          <div class="field-body">
            <div class="field-row">
              <div>
                <input v-model="form.deadline" class="input" type="date" />
                <div class="field-hint">到期后招募仍在，但会提示已截止</div>
              </div>
              <div>
                <div class="cover-box" @click="pickCover">
                  <template v-if="form.image">
                    <img :src="form.image" alt="封面预览" />
                    <button type="button" class="cover-remove" @click.stop="form.image = ''">
                      <AppIcon name="close" :size="13" />
                    </button>
                  </template>
                  <template v-else>
                    <AppIcon :name="uploading ? 'refresh' : 'image'" :size="20" />
                    <span>{{ uploading ? '上传中…' : '上传封面图' }}</span>
                    <small>建议 16:9，≤ 2MB</small>
                  </template>
                </div>
                <input ref="coverInput" type="file" accept="image/*" hidden @change="onCover" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="form-foot">
        <button type="button" class="btn btn-ghost" @click="router.back()">取消</button>
        <button type="submit" class="btn btn-primary btn-lg submit-btn" :disabled="saving">
          {{ saving ? '提交中…' : isEdit ? '保存修改' : '发布招募' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.form-card {
  overflow: hidden;
}

.form-body {
  padding: 10px 32px 4px;
}

.field-foot {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 7px;
}

.field-foot .counter {
  margin-left: auto;
}

.contact-row {
  display: flex;
  gap: 10px;
}

.contact-type {
  width: 112px;
  flex: none;
}

.chip-sm {
  height: 30px;
  font-size: 12.5px;
  padding: 0 12px;
}

/* 比赛选择 */
.comp-box {
  position: relative;
}

.comp-input {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 42px;
  padding: 0 12px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: #fff;
  transition: all 0.18s ease;
}

.comp-input:focus-within {
  border-color: #b9c0da;
  box-shadow: 0 0 0 4px rgba(78, 85, 121, 0.07);
}

.comp-input svg {
  color: #a3aaba;
  flex: none;
}

.comp-input input {
  flex: 1;
  min-width: 0;
  height: 100%;
  border: 0;
  outline: none;
  background: transparent;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
}

.comp-clear {
  border: 0;
  background: #f1f3f9;
  color: #8a92a6;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  cursor: pointer;
  flex: none;
}

.comp-sug {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 6px);
  z-index: 20;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
  max-height: 260px;
  overflow-y: auto;
}

.comp-sug button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 13px;
  border: 0;
  border-bottom: 1px solid #f4f5f9;
  background: #fff;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
}

.comp-sug button:last-child {
  border-bottom: 0;
}

.comp-sug button:hover {
  background: #f7f9fd;
}

.sug-name {
  font-size: 13px;
  font-weight: 600;
  color: #262b3c;
  flex: 1;
}

.sug-meta {
  font-size: 11px;
  color: var(--text-3);
}

.cover-box {
  height: 92px;
  border: 1px dashed #d7dce9;
  border-radius: 12px;
  background: #fbfcfe;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  cursor: pointer;
  color: #8d95ab;
  position: relative;
  overflow: hidden;
  transition: all 0.18s ease;
}

.cover-box:hover {
  border-color: #bfc7dd;
  background: #f7f9fd;
  color: #5d6684;
}

.cover-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-box span {
  font-size: 12px;
  font-weight: 600;
}

.cover-box small {
  font-size: 10.5px;
  color: #b0b7c6;
}

.cover-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 0;
  background: rgba(30, 36, 50, 0.62);
  color: #fff;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.form-foot {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 32px 26px;
  border-top: 1px solid #f4f5f9;
  background: #fdfdff;
}

.submit-btn {
  min-width: 168px;
}
</style>
