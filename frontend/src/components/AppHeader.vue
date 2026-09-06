<script setup>
import { SITE_NAME } from '@/config'
</script>

<template>
  <header class="site-header">
    <div class="header-inner">
      <RouterLink :to="{ name: 'home' }" class="brand">{{ SITE_NAME }}</RouterLink>

      <nav class="nav">
        <RouterLink :to="{ name: 'home' }" class="nav-link" active-class="is-active">
          首页
        </RouterLink>
        <RouterLink :to="{ name: 'articles' }" class="nav-link" active-class="is-active">
          文章
        </RouterLink>
        <RouterLink :to="{ name: 'about' }" class="nav-link" active-class="is-active">
          关于
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #e4e2dc;
  backdrop-filter: blur(8px);
}

.header-inner {
  max-width: 860px;
  margin: 0 auto;
  padding: 0.85rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
  text-decoration: none;
}

.brand:hover {
  color: #2d6a4f;
}

.nav {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.nav-link {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #5c5c5c;
  text-decoration: none;
}

.nav-link:hover,
.nav-link.is-active {
  color: #2d6a4f;
  background: #f6f5f2;
}
</style>
