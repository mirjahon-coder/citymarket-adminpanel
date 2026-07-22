<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-logo">
        <h1>🛒 Do'kon Admin</h1>
        <p>Admin paneliga kirish</p>
      </div>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">Login</label>
          <input v-model="username" type="text" class="form-control" placeholder="adminni kiriting" required autocomplete="username" />
        </div>
        <div class="form-group">
          <label class="form-label">Parol</label>
          <input v-model="password" type="password" class="form-control" placeholder="parolni kiriting" required autocomplete="current-password" />
        </div>
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'Kirish...' : 'Kirish' }}
        </button>
      </form>
      <p class="text-muted" style="text-align:center;margin-top:16px;">Default: admin / admin123</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login yoki parol noto\'g\'ri'
  } finally {
    loading.value = false
  }
}
</script>
