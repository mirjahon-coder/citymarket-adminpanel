<template>
  <div>
    <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
    <template v-else>
      <div class="dashboard-intro">
        <div>
          <span class="eyebrow">Bugungi ko'rinish</span>
          <h1>Xush kelibsiz, {{ authName }}</h1>
          <p>Marketplace faoliyatini bir joydan nazorat qiling.</p>
        </div>
        <div class="intro-date"><span class="live-dot"></span> Ma'lumotlar yangilanmoqda</div>
      </div>

      <div class="stats-grid">
        <div class="stat-card blue">
          <div class="stat-icon stat-icon-blue">□</div>
          <div class="stat-value">{{ stats.total_products }}</div>
          <div class="stat-label">Jami mahsulotlar</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-icon stat-icon-violet">◫</div>
          <div class="stat-value">{{ stats.total_categories }}</div>
          <div class="stat-label">Kategoriyalar</div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon stat-icon-green">◎</div>
          <div class="stat-value">{{ stats.total_customers }}</div>
          <div class="stat-label">Mijozlar</div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon stat-icon-amber">↗</div>
          <div class="stat-value">{{ stats.total_orders }}</div>
          <div class="stat-label">Buyurtmalar</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-icon stat-icon-blue">$</div>
          <div class="stat-value">{{ formatMoney(stats.total_revenue) }}</div>
          <div class="stat-label">Jami daromad</div>
        </div>
        <div class="stat-card orange">
          <div class="stat-icon stat-icon-violet">◇</div>
          <div class="stat-value">{{ stats.active_barabanlar }}</div>
          <div class="stat-label">Faol barabanlar</div>
        </div>
        <div class="stat-card red">
          <div class="stat-icon stat-icon-red">!</div>
          <div class="stat-value">{{ stats.blocked_customers }}</div>
          <div class="stat-label">Bloklangan mijozlar</div>
        </div>
        <div class="stat-card orange">
          <div class="stat-icon stat-icon-amber">△</div>
          <div class="stat-value">{{ stats.low_stock_products }}</div>
          <div class="stat-label">Kam qoldiq (≤5)</div>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="card revenue-card">
          <div class="card-header"><div><div class="eyebrow">Savdo faolligi</div><div class="card-title">Daromad ko'rsatkichi</div></div><span class="period-chip">Oxirgi 30 kun ˅</span></div>
          <div class="revenue-total">{{ formatMoney(stats.total_revenue) }} <span>+12.8%</span></div>
          <div class="mini-chart"><span v-for="(height, index) in chartBars" :key="index" :style="{ height: height + '%' }"></span></div>
          <div class="chart-axis"><span>01 Iyun</span><span>15 Iyun</span><span>30 Iyun</span></div>
        </div>
        <div class="card attention-card">
          <div class="card-header"><div class="card-title">Diqqat talab qiladi</div><span class="badge badge-warning">{{ stats.low_stock_products }} ta</span></div>
          <div class="attention-row"><span class="attention-icon amber">△</span><div><strong>Kam qoldiqdagi mahsulotlar</strong><small>Omborni tekshirish kerak</small></div><router-link to="/products">→</router-link></div>
          <div class="attention-row"><span class="attention-icon red">!</span><div><strong>Bloklangan mijozlar</strong><small>Faoliyatni ko'rib chiqing</small></div><router-link to="/users">→</router-link></div>
        </div>
      </div>

      <div class="card quick-actions-card">
        <div class="card-header">
          <div><div class="eyebrow">Ish jarayoni</div><div class="card-title">Tezkor amallar</div></div>
          <span class="text-muted">Ko'p ishlatiladigan bo'limlar</span>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
          <router-link to="/products" class="btn btn-primary">+ Mahsulot qo'shish</router-link>
          <router-link to="/categories" class="btn btn-outline">◫ Kategoriya qo'shish</router-link>
          <router-link to="/baraban" class="btn btn-outline">◇ Baraban sozlash</router-link>
          <router-link to="/users" class="btn btn-outline">◎ Mijozlarni ko'rish</router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'
import { useAuthStore } from '../stores/auth.js'

const loading = ref(true)
const authStore = useAuthStore()
const authName = authStore.user?.username || 'Admin'
const chartBars = [38, 52, 44, 66, 57, 78, 62, 88, 74, 92, 80, 96, 84, 100]
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
