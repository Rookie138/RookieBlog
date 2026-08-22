import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { loginApi, readStoredUser } from '@/api/auth'
import { TOKEN_KEY } from '@/api/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(readStoredUser())
  const loading = ref(false)

  const isLoggedIn = computed(() => Boolean(token.value && user.value))

  function setToken(value) {
    token.value = value
    if (value) localStorage.setItem(TOKEN_KEY, value)
    else localStorage.removeItem(TOKEN_KEY)
  }

  async function login(credentials) {
    loading.value = true
    try {
      const data = await loginApi(credentials)
      setToken(data.token)
      user.value = data.user
      return data
    } finally {
      loading.value = false
    }
  }

  function logout() {
    setToken('')
    user.value = null
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    login,
    logout,
  }
})
