<template>
  <div class="login-page">
    <div class="login-orbit orbit-one"></div>
    <div class="login-orbit orbit-two"></div>
    <div class="login-side-copy">
      <div class="brand-lockup"><img class="login-brand-logo" src="/city-market-logo.svg" alt="City Market" /><strong>City<span>Market</span></strong></div>
      <p>Shahar savdosini boshqarishning yangi markazi.</p>
      <div class="login-metric"><strong>24/7</strong><span>nazorat ostida</span></div>
    </div>
    <div class="login-box">
      <div class="login-logo">
        <span class="login-label">CITY MARKET / ADMIN</span>
        <h1>Xush kelibsiz.</h1>
        <p>Panelga kirish uchun ma'lumotlaringizni kiriting.</p>
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
          <span>{{ loading ? 'Kirish...' : 'Panelga kirish' }}</span><b>↗</b>
        </button>
      </form>
      <p class="login-footnote">City Market boshqaruv tizimi <span>•</span> 2026</p>
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
