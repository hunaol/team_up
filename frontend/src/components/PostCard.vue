<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import StatusPill from './StatusPill.vue'
import MatchBadge from './MatchBadge.vue'
import { TYPE_TEXT, daysLeft, gradeLabel, roleLabel, stageLabel, STAGE_TONE, gradientOf, relTime } from '../utils'

const props = defineProps({
  post: { type: Object, required: true }
})

const grad = computed(() => gradientOf(props.post.id || 1))
const left = computed(() => daysLeft(props.post.deadline))
const roles = computed(() => (props.post.roles || []).slice(0, 3))
const moreRoles = computed(() => Math.max(0, (props.post.roles || []).length - 3))
const grades = computed(() => (props.post.grade_req || []).map(gradeLabel))
</script>

<template>
  <router-link :to="`/post/${post.id}`" class="pcard">
    <div class="pcard-top">
      <div
        class="pcard-thumb"
        :style="{ background: `linear-gradient(140deg, ${grad[0]}, ${grad[1]})` }"
      >
        <img v-if="post.image" :src="post.image" :alt="post.title" />
        <AppIcon v-else :name="post.type === 'team' ? 'users' : 'user'" :size="24" />
      </div>
      <div class="pcard-head">
        <div class="pcard-title">{{ post.title }}</div>
        <div class="pcard-sub">
          <span class="pill pill-accent">{{ TYPE_TEXT[post.type] }}</span>
          <StatusPill :status="post.status" />
          <span v-if="post.stage" class="tag" :class="STAGE_TONE[post.stage]">{{ stageLabel(post.stage) }}</span>
        </div>
      </div>
    </div>

    <div v-if="post.competition" class="pcard-comp">
      <AppIcon name="flag" :size="13" />
      <span>{{ post.competition }}</span>
    </div>

    <p class="pcard-desc">{{ post.description_text || post.description }}</p>

    <div v-if="roles.length || grades.length" class="tag-row pcard-tags">
      <span v-for="r in roles" :key="r" class="tag">{{ roleLabel(r) }}</span>
      <span v-if="moreRoles" class="tag">+{{ moreRoles }}</span>
      <span v-if="grades.length" class="tag tag-violet">{{ grades.join('/') }}</span>
    </div>

    <div class="pcard-foot">
      <span>
        <AppIcon name="users" :size="13" />
        {{ post.need_num ? '缺 ' + post.need_num + ' 人' : '人数不限' }}
      </span>
      <span v-if="post.deadline">
        <AppIcon name="calendar" :size="13" />
        {{ left === null ? post.deadline : left > 0 ? `剩 ${left} 天` : '已截止' }}
      </span>
      <MatchBadge v-if="post.match" :score="post.match.score" style="margin-left: auto" />
      <span v-else class="pcard-time">{{ relTime(post.created_at) }}</span>
    </div>
  </router-link>
</template>

<style scoped>
.pcard {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  height: 100%;
}

.pcard:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: #e4e7f2;
}

.pcard-top {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.pcard-thumb {
  width: 58px;
  height: 58px;
  border-radius: 13px;
  overflow: hidden;
  flex: none;
  display: grid;
  place-items: center;
  color: #8d99bd;
}

.pcard-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pcard-head {
  min-width: 0;
  flex: 1;
}

.pcard-title {
  font-size: 14.5px;
  font-weight: 650;
  color: #1f2434;
  letter-spacing: -0.01em;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pcard:hover .pcard-title {
  color: var(--accent);
}

.pcard-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.pcard-comp {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 600;
  color: #5b6382;
  background: #f7f8fd;
  border-radius: 8px;
  padding: 5px 9px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pcard-comp span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pcard-desc {
  font-size: 12.5px;
  color: var(--text-2);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pcard-tags {
  gap: 5px;
}

.pcard-foot {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 10px;
  border-top: 1px solid #f4f5f9;
  font-size: 11.5px;
  color: #98a0b3;
  margin-top: auto;
}

.pcard-foot span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pcard-time {
  margin-left: auto;
  color: #b0b7c6;
}
</style>
