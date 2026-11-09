<script setup>
import { useRouter } from 'vue-router'
import { setAdminToken } from '../../api'

const router = useRouter()

function onLogout() {
  setAdminToken('')
  router.push('/admin/login')
}
</script>

<template>
  <div class="admin-wrap">
    <aside class="admin-side">
      <div class="brand">管理平台</div>
      <nav class="menu">
        <router-link to="/admin">数据概览</router-link>
        <router-link to="/admin/users">用户管理</router-link>
        <router-link to="/admin/posts">帖子管理</router-link>
      </nav>
      <button class="logout" @click="onLogout">退出登录</button>
    </aside>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>
