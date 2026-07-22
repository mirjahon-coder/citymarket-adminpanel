<template>
  <div>
    <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
    <template v-else>
      <div class="stats-grid">
        <div class="stat-card blue">
          <div class="stat-icon">📦</div>
          <div class="stat-value">{{ stats.total_products }}</div>
          <div class="stat-label">Jami mahsulotlar</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-icon">📂</div>
          <div class="stat-value">{{ stats.total_categories }}</div>
          <div class="stat-label">Kategoriyalar</div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon">👥</div>
          <div class="stat-value">{{ stats.total_customers }}</div>
          <div class="stat-label">Mijozlar</div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon">🛒</div>
          <div class="stat-value">{{ stats.total_orders }}</div>
          <div class="stat-label">Buyurtmalar</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-icon">💰</div>
          <div class="stat-value">{{ formatMoney(stats.total_revenue) }}</div>
          <div class="stat-label">Jami daromad</div>
        </div>
        <div class="stat-card orange">
          <div class="stat-icon">🎡</div>
          <div class="stat-value">{{ stats.active_barabanlar }}</div>
          <div class="stat-label">Faol barabanlar</div>
        </div>
        <div class="stat-card red">
          <div class="stat-icon">🚫</div>
          <div class="stat-value">{{ stats.blocked_customers }}</div>
          <div class="stat-label">Bloklangan mijozlar</div>
        </div>
        <div class="stat-card orange">
          <div class="stat-icon">⚠️</div>
          <div class="stat-value">{{ stats.low_stock_products }}</div>
          <div class="stat-label">Kam qoldiq (≤5)</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">Tezkor havolalar</div>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <router-link to="/products" class="btn btn-primary">📦 Mahsulot qo'shish</router-link>
          <router-link to="/categories" class="btn btn-outline">📂 Kategoriya qo'shish</router-link>
          <router-link to="/baraban" class="btn btn-outline">🎡 Baraban sozlash</router-link>
          <router-link to="/users" class="btn btn-outline">👥 Mijozlarni ko'rish</router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const loading = ref(true)
const stats = ref({
  total_products: 0, total_categories: 0, total_customers: 0,
  total_orders: 0, total_revenue: 0, active_barabanlar: 0,
  blocked_customers: 0, low_stock_products: 0
})

function formatMoney(val) {
  if (!val) return '0'
  return Number(val).toLocaleString('uz-UZ') + ' so\'m'
}

onMounted(async () => {
  try {
    const res = await api.get('/api/dashboard/stats')
    stats.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>
