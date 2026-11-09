<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { toast } from '../toast'
import { CONTACT_PLACEHOLDER } from '../utils'

const router = useRouter()
const form = reactive({
  type: 'team',
  title: '',
  description: '',
  need_num: '',
  contact_type: 'wechat',
  contact: ''
})
const errors = reactive({})
const submitting = ref(false)

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (form.title.trim().length < 2 || form.title.trim().length > 50) {
    errors.title = '赛事名称需为 2–50 字符'
  }
  if (form.description.trim().length < 10 || form.description.trim().length > 500) {
    errors.description = '描述需为 10–500 字符'
  }
  if (form.need_num !== '') {
    const n = Number(form.need_num)
    if (!Number.isInteger(n) || n < 1 || n > 99) errors.need_num = '需求人数需为 1–99 的整数'
  }
  const contact = form.contact.trim()
  if (form.contact_type === 'qq' && !/^\d{5,12}$/.test(contact)) {
    errors.contact = 'QQ 号需为 5–12 位数字'
  } else if (form.contact_type === 'phone' && !/^1[3-9]\d{9}$/.test(contact)) {
    errors.contact = '请输入正确的 11 位手机号'
  } else if (contact.length < 5 || contact.length > 100) {
    errors.contact = '联系方式为必填项（5–100 字符）'
  }
  return Object.keys(errors).length === 0
}

async function onSubmit() {
  if (!validate()) return
  submitting.value = true
  try {
    const body = {
      type: form.type,
      title: form.title.trim(),
      description: form.description.trim(),
      need_num: form.need_num === '' ? null : Number(form.need_num),
      contact_type: form.contact_type,
      contact: form.contact.trim()
    }
    const p = await api('/posts', { method: 'POST', body })
    toast('发布成功')
    router.push('/post/' + p.id)
  } catch (e) {
    toast(e.message, 'err')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="container" style="padding-top: 40px; max-width: 640px">
    <div class="card">
      <h2 style="margin: 0 0 24px; font-size: 24px; font-weight: 500">发布招募</h2>

      <div class="field">
        <label><b>*</b> 类型</label>
        <div class="tabs">
          <button :class="{ active: form.type === 'team' }" @click="form.type = 'team'">
            找队友（我组队缺人）
          </button>
          <button :class="{ active: form.type === 'join' }" @click="form.type = 'join'">
            找队伍（我想加入队伍）
          </button>
        </div>
      </div>

      <div class="field">
        <label><b>*</b> 赛事名称</label>
        <input v-model="form.title" placeholder="如：全国大学生数学建模竞赛" maxlength="50" />
        <div class="error" v-if="errors.title">{{ errors.title }}</div>
      </div>

      <div class="field">
        <label><b>*</b> 描述（10–500 字）</label>
        <textarea
          v-model="form.description"
          rows="4"
          placeholder="说明需求方向、要求、时间安排等，例如：希望找一名会 Python 的同学，负责数据处理…"
          maxlength="500"
        ></textarea>
        <div class="error" v-if="errors.description">{{ errors.description }}</div>
      </div>

      <div class="field">
        <label>需求人数（选填）</label>
        <input v-model="form.need_num" placeholder="1–99" inputmode="numeric" />
        <div class="error" v-if="errors.need_num">{{ errors.need_num }}</div>
      </div>

      <div class="field">
        <label><b>*</b> 联系方式</label>
        <div class="contact-row">
          <select v-model="form.contact_type" @change="errors.contact = ''">
            <option value="wechat">微信</option>
            <option value="qq">QQ</option>
            <option value="phone">手机号</option>
          </select>
          <input
            v-model="form.contact"
            :placeholder="CONTACT_PLACEHOLDER[form.contact_type]"
            :inputmode="form.contact_type === 'wechat' ? 'text' : 'numeric'"
            maxlength="100"
          />
        </div>
        <div class="hint">登录用户可见，游客不可见</div>
        <div class="error" v-if="errors.contact">{{ errors.contact }}</div>
      </div>

      <button class="btn block" :disabled="submitting" @click="onSubmit">
        {{ submitting ? '发布中…' : '发布' }}
      </button>
    </div>
  </div>
</template>
