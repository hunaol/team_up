<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'

const route = useRoute()
const router = useRouter()

const tip = computed(() => {
  if (route.path.startsWith('/admin')) return '这个管理页面不存在，返回数据概览看看'
  return '页面走丢了，回到首页继续寻找队友吧'
})
</script>

<template>
  <div class="nf card">
    <div class="empty">
      <div class="empty-art"><AppIcon name="compass" :size="34" /></div>
      <div class="nf-code">404</div>
      <div class="empty-title">{{ tip }}</div>
      <div class="nf-actions">
        <button class="btn btn-ghost btn-sm" @click="router.back()">返回上一页</button>
        <router-link to="/" class="btn btn-primary btn-sm">回到首页</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.nf {
  margin-top: 40px;
}
.nf-code {
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #dfe3ee;
  line-height: 1;
}
.nf-actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}
</style>
