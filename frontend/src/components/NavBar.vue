<script setup>
import { useRouter } from 'vue-router'
import { auth, logout } from '../store'

const router = useRouter()

async function onLogout() {
  await logout()
  router.push('/')
}
</script>

<template>
  <header class="nav">
    <div class="nav-inner">
      <router-link to="/" class="brand">
        <span class="logo" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round">
            <circle cx="9" cy="8" r="3.2" />
            <path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5" />
            <circle cx="17.5" cy="9" r="2.4" />
            <path d="M15.8 14.4c2.7-.3 4.7 1.5 4.7 4.6" />
          </svg>
        </span>
        比赛队友招募
      </router-link>
      <router-link to="/" class="link">首页</router-link>
      <router-link to="/publish" class="link">发布招募</router-link>
      <template v-if="auth.user">
        <router-link to="/my" class="link">我的发布</router-link>
        <router-link to="/favorites" class="link">我的收藏</router-link>
      </template>
      <template v-if="auth.user">
        <span class="user-chip"><b>{{ auth.user.name }}</b>（{{ auth.user.student_id }}）</span>
        <button class="btn plain sm" @click="onLogout">退出</button>
      </template>
      <router-link v-else to="/login" class="btn sm">登录 / 注册</router-link>
    </div>
  </header>
</template>
