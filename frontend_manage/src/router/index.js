import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '登录', guestOnly: true },
    },
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'articles',
          component: () => import('@/views/ArticleListView.vue'),
          meta: { title: '文章列表', requiresAuth: true },
        },
        {
          path: 'articles/new',
          name: 'article-create',
          component: () => import('@/views/ArticleEditView.vue'),
          meta: { title: '写文章', requiresAuth: true },
        },
        {
          path: 'articles/:slug',
          name: 'article-edit',
          component: () => import('@/views/ArticleEditView.vue'),
          meta: { title: '编辑文章', requiresAuth: true },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { title: '未找到' },
    },
  ],
})

router.beforeEach((to) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && userStore.isLoggedIn) {
    return { name: 'articles' }
  }

  const siteName = '博客管理'
  document.title = to.meta.title ? `${to.meta.title} · ${siteName}` : siteName
})

export default router
