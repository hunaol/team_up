<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { auth } from '../store'
import { thousand } from '../utils'
import AppIcon from '../components/AppIcon.vue'
import PostCard from '../components/PostCard.vue'

const stats = ref(null)
const posts = ref([])
const rec = ref([])
const loading = ref(true)

const cards = computed(() => {
  const s = stats.value || {}
  return [
    {
      key: 'posts',
      label: '累计发布',
      value: thousand(s.total_posts ?? 0),
      icon: 'megaphone',
      tone: 'blue'
    },
    {
      key: 'people',
      label: '总参与人数',
      value: thousand(s.participants ?? 0),
      icon: 'users',
      tone: 'green'
    },
    {
      key: 'active',
      label: '活跃招募',
      value: thousand(s.active_posts ?? 0),
      icon: 'sparkles',
      tone: 'orange'
    },
    {
      key: 'rate',
      label: '招募成功率',
      value: (s.success_rate ?? 0) + '%',
      icon: 'trend',
      tone: 'purple'
    }
  ]
})

const greet = computed(() => {
  const h = new Date().getHours()
  const base = h < 6 ? '夜深了' : h < 12 ? '早上好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
  return auth.user ? `${base}，${auth.user.name}` : base
})

onMounted(async () => {
  try {
    const [s, p] = await Promise.all([
      api('/stats/overview'),
      api('/posts')
    ])
    stats.value = s
    posts.value = p.slice(0, 6)
  } catch (e) {
    /* 首页允许静默降级 */
  } finally {
    loading.value = false
  }
  if (auth.user) {
    try {
      const list = await api('/recommended?limit=6')
      rec.value = list.filter((p) => (p.match?.score || 0) >= 45).slice(0, 3)
    } catch (e) {
      /* 资料不完整时没有推荐，忽略 */
    }
  }
})
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="hero-text">
        <span class="hero-eyebrow">{{ greet }}</span>
        <h1 class="hero-title">寻找志同道合的你</h1>
        <p class="hero-sub">加入比赛队，携手并肩，在竞赛中成长与突破</p>
        <div class="hero-actions">
          <router-link to="/publish" class="btn btn-dark btn-pill btn-lg">
            发布招募
            <AppIcon name="arrowRight" :size="16" />
          </router-link>
          <router-link to="/posts" class="hero-link">
            浏览招募广场
            <AppIcon name="chevronRight" :size="14" />
          </router-link>
        </div>
      </div>
      <div class="hero-art">
        <img src="/hero-campus.svg" alt="校园" />
      </div>
    </section>

    <section class="stat-grid home-stats">
      <div v-for="c in cards" :key="c.key" class="stat-card">
        <span class="stat-icon" :class="c.tone">
          <AppIcon :name="c.icon" />
        </span>
        <div class="stat-main">
          <div class="stat-label">{{ c.label }}</div>
          <div class="stat-value">{{ c.value }}</div>
        </div>
      </div>
    </section>

    <section v-if="rec.length" class="section">
      <div class="section-head">
        <div>
          <h2 class="section-title">
            <AppIcon name="sparkles" :size="16" style="color: var(--accent); vertical-align: -2px" />
            为你推荐
          </h2>
          <p class="section-desc">按你的技能、意向比赛与年级算出的匹配度</p>
        </div>
        <router-link to="/posts?sort=match" class="link-btn">
          查看全部
          <AppIcon name="arrowRight" :size="14" />
        </router-link>
      </div>
      <div class="post-grid">
        <PostCard v-for="p in rec" :key="p.id" :post="p" />
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2 class="section-title">最新招募</h2>
          <p class="section-desc">正在寻找队友的同学们，或许就在这里</p>
        </div>
        <router-link to="/posts" class="link-btn">
          查看更多
          <AppIcon name="arrowRight" :size="14" />
        </router-link>
      </div>

      <div v-if="loading" class="post-grid">
        <div v-for="i in 3" :key="i" class="card skeleton-card">
          <div class="skeleton" style="width: 66px; height: 66px; border-radius: 14px" />
          <div style="flex: 1">
            <div class="skeleton" style="height: 14px; width: 70%" />
            <div class="skeleton" style="height: 12px; width: 40%; margin-top: 10px" />
          </div>
        </div>
      </div>

      <div v-else-if="posts.length" class="post-grid">
        <PostCard v-for="p in posts" :key="p.id" :post="p" />
      </div>

      <div v-else class="card">
        <div class="empty">
          <div class="empty-art"><AppIcon name="megaphone" :size="34" /></div>
          <div class="empty-title">还没有人发布招募</div>
          <p class="empty-desc">成为第一个发起招募的人，找到你的比赛搭档</p>
          <router-link to="/publish" class="btn btn-primary btn-sm" style="margin-top: 6px">
            发布招募
          </router-link>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="feature-grid">
        <div class="card feature">
          <span class="stat-icon blue"><AppIcon name="shield" /></span>
          <div>
            <h3 class="feature-title">真实校园身份</h3>
            <p class="feature-desc">学号 + 姓名登录，减少陌生社交成本，队友都是同校同学。</p>
          </div>
        </div>
        <div class="card feature">
          <span class="stat-icon green"><AppIcon name="chat" /></span>
          <div>
            <h3 class="feature-title">联系方式直达</h3>
            <p class="feature-desc">登录后即可查看微信 / QQ / 手机号，沟通不绕弯。</p>
          </div>
        </div>
        <div class="card feature">
          <span class="stat-icon orange"><AppIcon name="clock" /></span>
          <div>
            <h3 class="feature-title">30 天有效周期</h3>
            <p class="feature-desc">招募信息自动过期，广场里的帖子始终新鲜有效。</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  padding-top: 4px;
}

/* Hero */
.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
  align-items: center;
  gap: 24px;
  min-height: 246px;
  border-radius: var(--r-xl);
  background:
    radial-gradient(660px 320px at 90% 10%, rgba(20, 184, 166, 0.2), transparent 62%),
    radial-gradient(560px 280px at 2% 98%, rgba(6, 182, 212, 0.18), transparent 64%),
    radial-gradient(420px 240px at 56% 108%, rgba(139, 92, 246, 0.12), transparent 60%),
    linear-gradient(115deg, #f5fbfa 0%, #eef8f8 46%, #f6f5ff 100%);
  border: 1px solid #e6eaf8;
  overflow: hidden;
  padding: 34px 40px;
  box-shadow: var(--shadow-sm);
}

.hero::after {
  content: "";
  position: absolute;
  right: -60px;
  top: -80px;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0));
}

.hero-text {
  position: relative;
  z-index: 2;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--accent);
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid #e2e7fb;
  border-radius: 999px;
  padding: 4px 12px;
  margin-bottom: 14px;
  font-weight: 600;
}

.hero-title {
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.2;
  color: #1b2030;
}

.hero-sub {
  margin-top: 10px;
  font-size: 14px;
  color: #6b7490;
  letter-spacing: 0.01em;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 24px;
}

.hero-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #58618a;
}

.hero-link:hover {
  color: var(--accent);
}

.hero-art {
  position: relative;
  z-index: 1;
  align-self: stretch;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  margin: -34px -20px -34px 0;
}

.hero-art img {
  width: 100%;
  max-width: 520px;
  height: 100%;
  object-fit: cover;
  object-position: center bottom;
  border-radius: 0 22px 22px 0;
  mask-image: linear-gradient(to right, transparent, #000 18%, #000 100%);
  -webkit-mask-image: linear-gradient(to right, transparent, #000 18%, #000 100%);
}

.home-stats {
  margin-top: 20px;
}

.section {
  margin-top: 34px;
}

.section-head {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: #1e2333;
}

.section-desc {
  font-size: 12.5px;
  color: var(--text-3);
  margin-top: 4px;
}

.section-head .link-btn {
  margin-left: auto;
  padding-bottom: 3px;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.skeleton-card {
  display: flex;
  gap: 13px;
  padding: 18px;
  align-items: flex-start;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.feature {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 20px;
}

.feature-title {
  font-size: 14px;
  font-weight: 650;
  color: #232838;
}

.feature-desc {
  font-size: 12.5px;
  color: var(--text-3);
  line-height: 1.7;
  margin-top: 5px;
}

@media (max-width: 1100px) {
  .post-grid,
  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .hero {
    grid-template-columns: 1fr;
    padding: 28px;
  }
  .hero-art {
    display: none;
  }
}

@media (max-width: 720px) {
  .post-grid,
  .feature-grid {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 26px;
  }
}
</style>
