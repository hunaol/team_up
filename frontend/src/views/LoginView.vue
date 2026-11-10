<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, setToken } from '../api'
import { admin, setUser } from '../store'
import { err, ok } from '../toast'
import AppIcon from '../components/AppIcon.vue'

const route = useRoute()
const router = useRouter()

const mode = ref('login')
const form = reactive({ student_id: '', name: '' })
const errors = reactive({})
const busy = ref(false)

const isLogin = computed(() => mode.value === 'login')
const redirect = computed(() => (route.query.redirect ? String(route.query.redirect) : '/'))
/** 管理员登录态下进到学生页：不是「没登录」，是「这个功能要学生身份」 */
const adminOnly = computed(() => admin.logged && !localStorage.getItem('user'))

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

function switchMode(m) {
  mode.value = m
  Object.keys(errors).forEach((k) => delete errors[k])
}

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])
  if (!/^[A-Za-z0-9]{5,20}$/.test(form.student_id.trim())) {
    errors.student_id = '学号需为 5–20 位字母或数字'
  }
  if (form.name.trim().length < 2) errors.name = '姓名至少 2 个字'
  else if (form.name.trim().length > 20) errors.name = '姓名不能超过 20 个字'
  return Object.keys(errors).length === 0
}

async function submit() {
  if (!validate()) return
  busy.value = true
  try {
    const body = { student_id: form.student_id.trim(), name: form.name.trim() }
    const res = await api(isLogin.value ? '/auth/login' : '/auth/register', {
      method: 'POST',
      body
    })
    setToken(res.token)
    setUser(res.user)
    ok(isLogin.value ? `欢迎回来，${res.user.name}` : '注册成功，开始寻找队友吧')
    router.push(redirect.value)
  } catch (e) {
    err(e.message)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth">
    <div class="auth-card">
      <section class="auth-side">
        <div class="auth-brand">
          <span class="brand-mark" style="background: rgba(255, 255, 255, 0.16); box-shadow: none">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3.2 9.4 12 5.2l8.8 4.2L12 13.6 3.2 9.4Z" />
              <path d="M6.6 11.4v4.2c0 1.9 2.4 3.2 5.4 3.2s5.4-1.3 5.4-3.2v-4.2" />
              <path d="M20.8 9.6v4.6" />
            </svg>
          </span>
          <span>
            <b>比赛队招募</b>
            <i>校园招募平台</i>
          </span>
        </div>

        <h2 class="auth-quote">寻找志同道合的你</h2>
        <p class="auth-quote-sub">加入比赛队，携手并肩，在竞赛中成长与突破。</p>

        <ul class="auth-points">
          <li><AppIcon name="shield" :size="15" />学号实名，队友都是同校同学</li>
          <li><AppIcon name="chat" :size="15" />登录后直接获取联系方式</li>
          <li><AppIcon name="sparkles" :size="15" />数学建模 / 互联网+ / 电子设计 全赛道</li>
        </ul>

        <div class="auth-deco" aria-hidden="true">
          <span class="deco-circle c1" />
          <span class="deco-circle c2" />
          <span class="deco-circle c3" />
        </div>
      </section>

      <section class="auth-form">
        <button class="auth-back" type="button" @click="goBack">
          <AppIcon name="chevronLeft" :size="15" />
          返回
        </button>

        <div class="auth-tabs">
          <button class="auth-tab" :class="{ active: isLogin }" @click="switchMode('login')">登录</button>
          <button class="auth-tab" :class="{ active: !isLogin }" @click="switchMode('register')">注册</button>
        </div>

        <div v-if="adminOnly" class="auth-admin-note">
          <AppIcon name="shield" :size="14" />
          <span>
            你已以<b>管理员</b>身份登录，当前页面是学生功能，需要学生账号。
            <router-link to="/admin">回管理后台</router-link>
          </span>
        </div>

        <h1 class="auth-title">{{ isLogin ? '欢迎回来' : '创建你的校园账号' }}</h1>
        <p class="auth-sub">
          {{ isLogin ? '使用学号与姓名即可登录，无需密码' : '填写学号与姓名完成注册，即刻开始招募' }}
        </p>

        <form class="auth-fields" @submit.prevent="submit">
          <label class="auth-field">
            <span>学号</span>
            <input
              v-model="form.student_id"
              class="input"
              :class="{ invalid: errors.student_id }"
              placeholder="请输入你的学号"
              autocomplete="username"
            />
            <small v-if="errors.student_id" class="field-error">{{ errors.student_id }}</small>
          </label>

          <label class="auth-field">
            <span>姓名</span>
            <input
              v-model="form.name"
              class="input"
              :class="{ invalid: errors.name }"
              placeholder="请输入真实姓名"
              autocomplete="name"
            />
            <small v-if="errors.name" class="field-error">{{ errors.name }}</small>
          </label>

          <button class="btn btn-primary btn-lg btn-block" :disabled="busy" type="submit">
            {{ busy ? '处理中…' : isLogin ? '登录' : '注册并登录' }}
            <AppIcon name="arrowRight" :size="16" />
          </button>
        </form>

        <p class="auth-foot">
          {{ isLogin ? '还没有账号？' : '已经有账号了？' }}
          <button class="link-btn" @click="switchMode(isLogin ? 'register' : 'login')">
            {{ isLogin ? '立即注册' : '去登录' }}
          </button>
        </p>

        <router-link to="/admin/login" class="auth-admin">
          <AppIcon name="lock" :size="13" />
          管理员入口
        </router-link>
      </section>
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
    radial-gradient(1000px 500px at 12% -10%, #eef2fb 0%, transparent 60%),
    radial-gradient(800px 400px at 100% 110%, #f0f4ec 0%, transparent 55%),
    var(--bg);
}

.auth-card {
  width: 100%;
  max-width: 940px;
  display: grid;
  grid-template-columns: 1.02fr 0.98fr;
  background: #fff;
  border-radius: 24px;
  border: 1px solid var(--line);
  box-shadow: 0 40px 90px -50px rgba(24, 32, 60, 0.5);
  overflow: hidden;
}

.auth-side {
  position: relative;
  padding: 40px 38px;
  background: linear-gradient(160deg, #4e5579 0%, #414863 55%, #363c54 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 2;
}

.auth-brand b {
  display: block;
  font-size: 14px;
  letter-spacing: 0.02em;
}

.auth-brand i {
  display: block;
  font-style: normal;
  font-size: 10.5px;
  letter-spacing: 0.14em;
  color: rgba(255, 255, 255, 0.55);
}

.auth-quote {
  position: relative;
  z-index: 2;
  margin-top: auto;
  font-size: 28px;
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.auth-quote-sub {
  position: relative;
  z-index: 2;
  margin-top: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.8;
}

.auth-points {
  position: relative;
  z-index: 2;
  list-style: none;
  padding: 0;
  margin: 26px 0 0;
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.auth-points li {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.82);
}

.auth-points svg {
  color: rgba(255, 255, 255, 0.55);
}

.auth-deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.09);
}

.c1 {
  width: 380px;
  height: 380px;
  right: -170px;
  top: -120px;
}

.c2 {
  width: 250px;
  height: 250px;
  right: -90px;
  top: -50px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.06), transparent 70%);
}

.c3 {
  width: 520px;
  height: 520px;
  left: -260px;
  bottom: -320px;
}

.auth-form {
  padding: 58px 42px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.auth-back {
  position: absolute;
  top: 18px;
  left: 18px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 6px 10px 6px 6px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--text-3);
  font-family: inherit;
  font-size: 12.5px;
  cursor: pointer;
  transition: background 0.16s ease, color 0.16s ease;
}

.auth-back:hover {
  background: #f3f4f9;
  color: var(--primary);
}

.auth-admin-note {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin-bottom: 14px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--accent-soft);
  color: #0f6f66;
  font-size: 12px;
  line-height: 1.6;
}

.auth-admin-note svg {
  flex: none;
  margin-top: 2px;
}

.auth-admin-note b {
  font-weight: 700;
}

.auth-admin-note a {
  color: var(--accent-strong);
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px solid currentColor;
}

.auth-tabs {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  background: #f3f4f9;
  border-radius: 999px;
  align-self: flex-start;
  margin-bottom: 24px;
}

.auth-tab {
  height: 32px;
  padding: 0 20px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #6d7488;
  font-size: 12.5px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.18s ease;
}

.auth-tab.active {
  background: #fff;
  color: #2b3143;
  box-shadow: 0 2px 8px rgba(24, 32, 60, 0.1);
}

.auth-title {
  font-size: 24px;
  font-weight: 750;
  letter-spacing: -0.025em;
  color: #1b2030;
}

.auth-sub {
  margin-top: 8px;
  font-size: 12.5px;
  color: var(--text-3);
  line-height: 1.7;
}

.auth-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 26px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.auth-field > span {
  font-size: 12.5px;
  font-weight: 600;
  color: #4b5266;
}

.auth-field .input {
  height: 46px;
}

.auth-foot {
  margin-top: 20px;
  font-size: 12.5px;
  color: var(--text-3);
  text-align: center;
}

.auth-admin {
  position: absolute;
  top: 18px;
  right: 20px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: #a8afbf;
}

.auth-admin:hover {
  color: var(--primary);
}

@media (max-width: 900px) {
  .auth-card {
    grid-template-columns: 1fr;
    max-width: 460px;
  }
  .auth-side {
    padding: 28px;
    min-height: 190px;
  }
  .auth-quote {
    font-size: 22px;
    margin-top: 26px;
  }
  .auth-points {
    display: none;
  }
  .auth-form {
    padding: 52px 26px 34px;
  }
}
</style>
