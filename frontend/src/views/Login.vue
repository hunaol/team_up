<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, setToken } from '../api'
import { setUser } from '../store'
import { toast } from '../toast'

const route = useRoute()
const router = useRouter()

const tab = ref('login')
const form = reactive({ student_id: '', name: '' })
const errors = reactive({})
const submitting = ref(false)

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (tab.value === 'register' && !/^[A-Za-z0-9]{5,20}$/.test(form.student_id.trim())) {
    errors.student_id = '学号需为 5–20 位数字或字母'
  }
  if (tab.value === 'register' && (form.name.trim().length < 2 || form.name.trim().length > 20)) {
    errors.name = '姓名需为 2–20 个字符'
  }
  if (tab.value === 'login' && !form.student_id.trim()) errors.student_id = '请输入学号'
  if (tab.value === 'login' && !form.name.trim()) errors.name = '请输入姓名'
  return Object.keys(errors).length === 0
}

async function onSubmit() {
  if (!validate()) return
  submitting.value = true
  try {
    const path = tab.value === 'register' ? '/auth/register' : '/auth/login'
    const data = await api(path, {
      method: 'POST',
      body: { student_id: form.student_id.trim(), name: form.name.trim() }
    })
    setToken(data.token)
    setUser(data.user)
    toast(tab.value === 'register' ? '注册成功' : '登录成功')
    router.replace(route.query.redirect || '/')
  } catch (e) {
    toast(e.message, 'err')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <h2>比赛队友招募</h2>
      <div class="sub">使用学号和姓名{{ tab === 'register' ? '注册' : '登录' }}</div>

      <div class="auth-tabs">
        <button :class="{ active: tab === 'login' }" @click="tab = 'login'">登录</button>
        <button :class="{ active: tab === 'register' }" @click="tab = 'register'">注册</button>
      </div>

      <div class="field">
        <label>学号</label>
        <input v-model="form.student_id" placeholder="如 20240123" @keyup.enter="onSubmit" />
        <div class="error" v-if="errors.student_id">{{ errors.student_id }}</div>
      </div>

      <div class="field">
        <label>姓名</label>
        <input v-model="form.name" placeholder="真实姓名" @keyup.enter="onSubmit" />
        <div class="error" v-if="errors.name">{{ errors.name }}</div>
      </div>

      <button class="btn block" :disabled="submitting" @click="onSubmit">
        {{ submitting ? '请稍候…' : tab === 'register' ? '注册' : '登录' }}
      </button>

      <div class="hint" style="margin-top: 12px; font-size: 12px; color: var(--sub)">
        提示：登录信息用于帖子署名与账号唯一性，学号不会对外展示。
      </div>
    </div>
  </div>
</template>
