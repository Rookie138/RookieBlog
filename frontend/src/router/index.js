import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'
import ArticlesView from '@/views/ArticlesView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: '首页' } },
    { path: '/about', name: 'about', component: AboutView, meta: { title: '关于' } },
    { path: '/articles', name: 'articles', component: ArticlesView, meta: { title: '文章' } },
    {
      path: '/articles/:slug',
      name: 'article-detail',
      component: ArticleDetailView,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: { title: '未找到' },
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const siteName = '学习笔记'
  document.title = to.meta.title ? `${to.meta.title} · ${siteName}` : siteName
})

export default router
