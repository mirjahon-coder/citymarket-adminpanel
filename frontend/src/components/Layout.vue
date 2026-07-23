<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img class="brand-logo" src="/city-market-logo.svg" alt="City Market" />
        <div>
          <h2>City<span>Market</span></h2>
          <p>Operations center</p>
        </div>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section">Workspace</div>
        <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
          <span class="icon">▦</span> Dashboard
        </router-link>
        <div class="nav-section">Katalog</div>
        <router-link to="/categories" class="nav-item" :class="{ active: route.path === '/categories' }">
          <span class="icon">◫</span> Kategoriyalar
        </router-link>
        <router-link to="/products" class="nav-item" :class="{ active: route.path === '/products' }">
          <span class="icon">□</span> Mahsulotlar
        </router-link>
        <div class="nav-section">Xususiyatlar</div>
        <router-link to="/baraban" class="nav-item" :class="{ active: route.path === '/baraban' }">
          <span class="icon">◇</span> Baraban
        </router-link>
        <div class="nav-section">Foydalanuvchilar</div>
        <router-link to="/users" class="nav-item" :class="{ active: route.path === '/users' }">
          <span class="icon">◎</span> Mijozlar
        </router-link>
        <router-link to="/admins" class="nav-item" :class="{ active: route.path === '/admins' }">
          <span class="icon">⌁</span> Adminlar
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="admin-profile">
          <div class="avatar">{{ (authStore.user?.username || 'A').charAt(0).toUpperCase() }}</div>
          <div class="admin-name"><strong>{{ authStore.user?.username || 'Admin' }}</strong><span>Administrator</span></div>
        </div>
        <button class="btn-logout" @click="handleLogout"><span>↗</span> Chiqish</button>
      </div>
    </aside>
    <main class="main-content">
      <div class="topbar">
        <div class="topbar-title"><span class="topbar-kicker">City Market</span><strong>{{ pageTitle }}</strong></div>
        <div class="topbar-right">
          <div class="topbar-search">⌕ <span>Qidirish...</span><kbd>⌘ K</kbd></div>
          <button class="notification" aria-label="Bildirishnomalar">♢<i></i></button>
          <span class="badge badge-success"><i></i> Tizim faol</span>
          <span class="text-muted">{{ currentDate }}</span>
        </div>
      </div>
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const pageTitle = computed(() => {
  const map = {
    '/': 'Dashboard',
    '/categories': 'Kategoriyalar',
    '/products': 'Mahsulotlar',
    '/baraban': 'Baraban',
    '/users': 'Mijozlar',
    '/admins': 'Adminlar',
  }
  return map[route.path] || 'Admin Panel'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('uz-UZ', { year: 'numeric', month: 'long', day: 'numeric' })
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
