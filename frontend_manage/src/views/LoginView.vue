<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="onSubmit">
      <h1>管理端登录</h1>
      <p class="muted">使用管理员账号登录后，可以撰写和发布文章。</p>

      <label class="field">
        用户名
        <input v-model="username" type="text" autocomplete="username" required />
      </label>

      <label class="field">
        密码
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="submit" type="submit" :disabled="userStore.loading">
        {{ userStore.loading ? '登录中…' : '登录' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const error = ref('')

async function onSubmit() {
  error.value = ''
  try {
    await userStore.login({
      username: username.value,
      password: password.value,
    })
    router.push(route.query.redirect || { name: 'articles' })
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 380px;
  padding: 2rem;
  background: #fff;
  border: 1px solid #e4e2dc;
  border-radius: 10px;
}

.login-card h1 {
  margin: 0 0 0.4rem;
  font-size: 1.4rem;
}

.login-card .muted {
  margin: 0 0 1.5rem;
  font-size: 0.9rem;
}

.field {
  display: block;
  margin-bottom: 1rem;
}

.field input {
  display: block;
  width: 100%;
  margin-top: 0.35rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e4e2dc;
  border-radius: 8px;
  background: #fff;
}

.submit {
  width: 100%;
  margin-top: 0.4rem;
  padding: 0.6rem;
  border: none;
  border-radius: 8px;
  background: #2d6a4f;
  color: #fff;
  cursor: pointer;
}

.submit:disabled {
  opacity: 0.7;
  cursor: wait;
}
</style>
