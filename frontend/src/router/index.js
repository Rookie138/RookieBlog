import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'
import ArticlesView from '@/views/ArticlesView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import { SITE_NAME } from '@/config'

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
      // 标题在详情页拿到数据后会被替换成文章标题，这里的默认值用于加载阶段
      meta: { title: '文章详情' },
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
  document.title = to.meta.title ? `${to.meta.title} · ${SITE_NAME}` : SITE_NAME
})

export default router
