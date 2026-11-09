<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { TYPE_TEXT, fmtDate, gradientOf, relTime } from '../utils'
import { err, ok } from '../toast'
import AppIcon from '../components/AppIcon.vue'
import StatusPill from '../components/StatusPill.vue'
import PageHead from '../components/PageHead.vue'

const posts = ref([])
const loading = ref(true)
const busyId = ref(null)

const total = computed(() => posts.value.length)

async function load() {
  loading.value = true
  try {
    posts.value = await api('/my/favorites')
  } catch (e) {
    err(e.message)
  } finally {
    loading.value = false
  }
}

async function remove(p) {
  busyId.value = p.id
  try {
    await api(`/posts/${p.id}/favorite`, { method: 'DELETE' })
    posts.value = posts.value.filter((x) => x.id !== p.id)
    ok('已取消收藏')
  } catch (e) {
    err(e.message)
  } finally {
    busyId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead
      :crumbs="[{ label: '首页', to: '/' }, { label: '我的收藏' }]"
      title="我的收藏"
      :desc="`共收藏 ${total} 条招募，随时回来查看`"
    >
      <template #actions>
        <router-link to="/posts" class="btn btn-ghost">
          <AppIcon name="compass" :size="16" />
          去广场逛逛
        </router-link>
      </template>
    </PageHead>

    <div class="card list-card">
      <div v-if="loading" class="list-body">
        <div v-for="i in 3" :key="i" class="post-row">
          <div class="skeleton" style="width: 104px; height: 76px; border-radius: 12px" />
          <div style="flex: 1">
            <div class="skeleton" style="height: 15px; width: 40%" />
            <div class="skeleton" style="height: 12px; width: 60%; margin-top: 12px" />
          </div>
        </div>
      </div>

      <div v-else-if="posts.length" class="list-body">
        <div v-for="p in posts" :key="p.id" class="post-row">
          <router-link :to="`/post/${p.id}`" class="thumb">
            <img v-if="p.image" :src="p.image" :alt="p.title" />
            <span
              v-else
              class="thumb-fallback"
              :style="{ background: `linear-gradient(140deg, ${gradientOf(p.id + p.title)[0]}, ${gradientOf(p.id + p.title)[1]})` }"
            >
              <AppIcon name="building" />
            </span>
          </router-link>

          <div class="row-body">
            <router-link :to="`/post/${p.id}`" class="row-title">
              {{ p.title }}
              <StatusPill :status="p.status" />
              <span class="pill pill-accent">{{ TYPE_TEXT[p.type] }}</span>
            </router-link>
            <p class="row-desc">{{ p.description_text || p.description }}</p>
            <div class="row-meta">
              <span><AppIcon name="user" :size="13" />{{ p.author_name }}</span>
              <span><AppIcon name="users" :size="13" />需求 {{ p.need_num ? p.need_num + ' 人' : '不限' }}</span>
              <span><AppIcon name="calendar" :size="13" />截止 {{ p.deadline || '未设置' }}</span>
              <span><AppIcon name="clock" :size="13" />{{ relTime(p.created_at) }}</span>
            </div>
          </div>

          <div class="row-actions">
            <router-link :to="`/post/${p.id}`" class="btn btn-ghost btn-xs">查看详情</router-link>
            <button class="btn btn-danger-soft btn-xs" :disabled="busyId === p.id" @click="remove(p)">
              <AppIcon name="heart" :size="13" />
              取消收藏
            </button>
          </div>
        </div>
      </div>

      <div v-else class="list-body">
        <div class="empty">
          <div class="empty-art"><AppIcon name="bookmark" :size="34" /></div>
          <div class="empty-title">还没有收藏任何招募</div>
          <p class="empty-desc">在招募广场看到感兴趣的信息，点一下收藏就会出现在这里</p>
          <router-link to="/posts" class="btn btn-primary btn-sm" style="margin-top: 6px">去招募广场</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-card {
  overflow: hidden;
}

.list-body {
  padding: 4px 20px 8px;
}
</style>
