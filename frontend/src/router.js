import { createRouter, createWebHistory } from 'vue-router'
import { getAdminToken, getToken } from './api'

const routes = [
  { path: '/', component: () => import('./views/HomeView.vue') },
  { path: '/posts', component: () => import('./views/PostsView.vue') },
  { path: '/post/:id', component: () => import('./views/PostDetailView.vue') },
  { path: '/publish', component: () => import('./views/PublishView.vue'), meta: { auth: true } },
  { path: '/post/:id/edit', component: () => import('./views/PublishView.vue'), meta: { auth: true } },
  { path: '/my', component: () => import('./views/MyPostsView.vue'), meta: { auth: true } },
  { path: '/favorites', component: () => import('./views/FavoritesView.vue'), meta: { auth: true } },
  { path: '/login', component: () => import('./views/LoginView.vue'), meta: { bare: true } },
  { path: '/admin/login', component: () => import('./views/AdminLoginView.vue'), meta: { bare: true } },
  { path: '/admin', component: () => import('./views/admin/AdminDashboard.vue'), meta: { admin: true } },
  { path: '/admin/users', component: () => import('./views/admin/AdminUsers.vue'), meta: { admin: true } },
  { path: '/admin/posts', component: () => import('./views/admin/AdminPosts.vue'), meta: { admin: true } },
  { path: '/:pathMatch(.*)*', component: () => import('./views/NotFoundView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    return saved || { top: 0 }
  }
})

router.beforeEach((to) => {
  if (to.meta.auth && !getToken()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && !getAdminToken()) {
    return { path: '/admin/login', query: { redirect: to.fullPath } }
  }
})

export default router
