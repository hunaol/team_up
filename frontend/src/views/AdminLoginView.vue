<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminApi, setAdminToken } from '../api'
import { setAdminLogged } from '../store'
import { err, ok } from '../toast'
import AppIcon from '../components/AppIcon.vue'

const route = useRoute()
const router = useRouter()

const form = reactive({ username: '', password: '' })
const busy = ref(false)
const showPwd = ref(false)

async function submit() {
  if (!form.username.trim() || !form.password) {
    err('请输入管理员账号和密码')
    return
  }
  busy.value = true
  try {
    const res = await adminApi('/admin/login', {
      method: 'POST',
      body: { username: form.username.trim(), password: form.password },
      token: ''
    })
    setAdminToken(res.token)
    setAdminLogged(true)
    ok('管理员登录成功')
    const redirect = route.query.redirect ? String(route.query.redirect) : '/admin'
    router.push(redirect)
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth">
    <div class="admin-card">
      <div class="admin-head">
        <span class="brand-mark">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M3.2 9.4 12 5.2l8.8 4.2L12 13.6 3.2 9.4Z" />
            <path d="M6.6 11.4v4.2c0 1.9 2.4 3.2 5.4 3.2s5.4-1.3 5.4-3.2v-4.2" />
            <path d="M20.8 9.6v4.6" />
          </svg>
        </span>
        <div>
          <div class="admin-brand">比赛队招募 · 管理后台</div>
          <div class="admin-brand-sub">CAMPUS RECRUIT ADMIN</div>
        </div>
      </div>

      <h1 class="admin-title">管理员登录</h1>
      <p class="admin-sub">请输入管理员账号与密码，登录后可管理用户与招募内容</p>

      <form class="admin-fields" @submit.prevent="submit">
        <label class="auth-field">
          <span>管理员账号</span>
          <input v-model="form.username" class="input" placeholder="请输入账号" autocomplete="username" />
        </label>

        <label class="auth-field">
          <span>密码</span>
          <div class="pwd-wrap">
            <input v-model="form.password" class="input" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码"
              autocomplete="current-password" />
            <button type="button" class="pwd-eye" @click="showPwd = !showPwd">
              <AppIcon :name="showPwd ? 'eye' : 'lock'" :size="15" />
            </button>
          </div>
        </label>

        <button class="btn btn-primary btn-lg btn-block" :disabled="busy" type="submit">
          {{ busy ? '登录中…' : '登录管理后台' }}
        </button>
      </form>

      <div class="admin-foot">
        <router-link to="/" class="link-btn">返回前台首页</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px 20px;
  background:
    radial-gradient(900px 460px at 50% -30%, #e9edf9 0%, transparent 62%),
    var(--bg);
}

.admin-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 32px 34px 26px;
  box-shadow: 0 40px 90px -55px rgba(24, 32, 60, 0.55);
}

.admin-head {
  display: flex;
  align-items: center;
  gap: 11px;
  padding-bottom: 22px;
  border-bottom: 1px solid #f3f4f9;
  margin-bottom: 22px;
}

.admin-brand {
  font-size: 13px;
  font-weight: 700;
  color: #262b3c;
}

.admin-brand-sub {
  font-size: 9.5px;
  letter-spacing: 0.16em;
  color: #b0b7c6;
  margin-top: 2px;
}

.admin-title {
  font-size: 22px;
  font-weight: 750;
  letter-spacing: -0.025em;
  color: #1b2030;
}

.admin-sub {
  margin-top: 8px;
  font-size: 12.5px;
  color: var(--text-3);
  line-height: 1.7;
}

.admin-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.auth-field>span {
  font-size: 12.5px;
  font-weight: 600;
  color: #4b5266;
}

.pwd-wrap {
  position: relative;
}

.pwd-wrap .input {
  padding-right: 44px;
}

.pwd-eye {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: 0;
  background: transparent;
  color: #a3aaba;
  cursor: pointer;
  border-radius: 8px;
}

.pwd-eye:hover {
  color: var(--primary);
}

.admin-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f9;
}

.admin-hint {
  font-size: 11px;
  color: #b6bccb;
}
</style>
