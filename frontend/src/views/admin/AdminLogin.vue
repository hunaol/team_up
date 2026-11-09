<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, setAdminToken } from '../../api'
import { toast } from '../../toast'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const submitting = ref(false)

async function onSubmit() {
  if (!form.username.trim() || !form.password) {
    toast('请输入账号和密码', 'err')
    return
  }
  submitting.value = true
  try {
    const data = await api('/admin/login', {
      method: 'POST',
      body: { username: form.username.trim(), password: form.password },
      token: ''
    })
    setAdminToken(data.token)
    toast('登录成功')
    router.replace('/admin')
  } catch (e) {
    toast(e.message, 'err')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-wrap" style="min-height: 100vh">
    <div class="auth-card">
      <h2>管理平台</h2>
      <div class="sub">比赛队友招募 · 管理员登录</div>

      <div class="field">
        <label>账号</label>
        <input v-model="form.username" placeholder="管理员账号" @keyup.enter="onSubmit" />
      </div>
      <div class="field">
        <label>密码</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="密码"
          @keyup.enter="onSubmit"
        />
      </div>

      <button class="btn block" :disabled="submitting" @click="onSubmit">
        {{ submitting ? '登录中…' : '登录' }}
      </button>
    </div>
  </div>
</template>
