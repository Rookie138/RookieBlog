<template>
  <div class="layout">
    <aside class="sidebar">
      <RouterLink :to="{ name: 'articles' }" class="brand">博客管理</RouterLink>
      <nav class="nav">
        <RouterLink :to="{ name: 'articles' }" class="nav-link">文章列表</RouterLink>
        <RouterLink :to="{ name: 'article-create' }" class="nav-link">写文章</RouterLink>
      </nav>
    </aside>

    <div class="main">
      <header class="topbar">
        <span class="muted">{{ userStore.user?.username }}</span>
        <button type="button" class="link-btn" @click="onLogout">退出</button>
      </header>
      <div class="content">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

function onLogout() {
  userStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 220px 1fr;
}

.sidebar {
  padding: 1.25rem 1rem;
  background: #fff;
  border-right: 1px solid #e4e2dc;
}

.brand {
  display: block;
  margin-bottom: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-link {
  padding: 0.45rem 0.7rem;
  border-radius: 6px;
  color: #5c5c5c;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #2d6a4f;
  background: #f6f5f2;
}

.main {
  min-width: 0;
}

.topbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #e4e2dc;
}

.content {
  padding: 1.5rem 1.5rem 3rem;
}

.link-btn {
  border: none;
  background: none;
  color: #5c5c5c;
  cursor: pointer;
}

.link-btn:hover {
  color: #2d6a4f;
}
</style>
