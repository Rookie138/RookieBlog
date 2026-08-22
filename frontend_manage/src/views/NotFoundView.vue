<template>
  <div class="wrap">
    <h1>404</h1>
    <p class="muted">页面不存在</p>
    <RouterLink :to="{ name: 'articles' }">回到文章列表</RouterLink>
  </div>
</template>

<style scoped>
.wrap {
  padding: 4rem 1.5rem;
  text-align: center;
}
</style>
