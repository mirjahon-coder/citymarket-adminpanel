<template>
  <div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">👥 Mijozlar</div>
        <div class="flex gap-8">
          <span class="badge badge-primary">Jami: {{ items.length }}</span>
        </div>
      </div>

      <div class="search-bar">
        <input v-model="search" type="text" class="search-input" placeholder="Ism, telefon yoki email..." />
        <select v-model="filterBlocked" class="form-control" style="width:160px;">
          <option value="">Barchasi</option>
          <option value="false">Faol</option>
          <option value="true">Bloklangan</option>
        </select>
      </div>

      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="empty-icon">👥</div>
        <p>Mijozlar topilmadi</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Ism</th>
              <th>Telefon</th>
              <th>Email</th>
              <th>Holati</th>
              <th>Ro'yxatdan</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filtered" :key="u.id">
              <td>{{ u.id }}</td>
              <td class="fw-600">{{ u.full_name || '-' }}</td>
              <td>{{ u.phone || '-' }}</td>
              <td>{{ u.email || '-' }}</td>
              <td>
                <span v-if="u.is_blocked" class="badge badge-danger">🚫 Bloklangan</span>
                <span v-else class="badge badge-success">✅ Faol</span>
              </td>
              <td>{{ formatDate(u.created_at) }}</td>
              <td>
                <div class="flex gap-8">
                  <button class="btn btn-sm btn-outline" @click="viewUser(u)">👁️ Ko'rish</button>
                  <button v-if="!u.is_blocked" class="btn btn-sm btn-danger" @click="blockUser(u)">🚫 Bloklash</button>
                  <button v-else class="btn btn-sm btn-success" @click="unblockUser(u.id)">✅ Blokni ochish</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User detail modal -->
    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail=false">
      <div class="modal" style="max-width:640px;">
        <div class="modal-header">
          <div class="modal-title">👤 {{ detailUser?.full_name || 'Foydalanuvchi' }}</div>
          <button class="btn-icon" @click="showDetail=false">✕</button>
        </div>
        <div class="modal-body">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
            <div><div class="text-muted">Ism</div><div class="fw-600">{{ detailUser?.full_name || '-' }}</div></div>
            <div><div class="text-muted">Telefon</div><div class="fw-600">{{ detailUser?.phone || '-' }}</div></div>
            <div><div class="text-muted">Email</div><div class="fw-600">{{ detailUser?.email || '-' }}</div></div>
            <div><div class="text-muted">Holati</div>
              <span v-if="detailUser?.is_blocked" class="badge badge-danger">🚫 Bloklangan</span>
              <span v-else class="badge badge-success">✅ Faol</span>
            </div>
            <div><div class="text-muted">Ro'yxatdan o'tgan</div><div>{{ formatDate(detailUser?.created_at) }}</div></div>
            <div><div class="text-muted">Oxirgi kirish</div><div>{{ formatDate(detailUser?.last_login) || '-' }}</div></div>
          </div>
          <div v-if="detailUser?.is_blocked && detailUser?.block_reason">
            <div class="alert alert-error">Blok sababi: {{ detailUser.block_reason }}</div>
          </div>

          <hr class="divider" />
          <div class="card-title mb-16">🛒 Buyurtmalar tarixi</div>
          <div v-if="detailOrders.length === 0" class="empty-state" style="padding:20px;">
            <p>Buyurtmalar yo'q</p>
          </div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Holati</th>
                  <th>Jami summa</th>
                  <th>Mahsulotlar</th>
                  <th>Sana</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in detailOrders" :key="o.id">
                  <td>#{{ o.id }}</td>
                  <td><span class="badge badge-primary">{{ o.status }}</span></td>
                  <td class="fw-600">{{ formatPrice(o.total_price) }}</td>
                  <td>{{ o.items?.map(i => `${i.product_name} x${i.quantity}`).join(', ') || '-' }}</td>
                  <td>{{ formatDate(o.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Block modal -->
    <div v-if="showBlockModal" class="modal-overlay" @click.self="showBlockModal=false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">🚫 Foydalanuvchini bloklash</div>
          <button class="btn-icon" @click="showBlockModal=false">✕</button>
        </div>
        <div class="modal-body">
          <p style="margin-bottom:14px;">{{ blockTarget?.full_name || 'Foydalanuvchi' }}ni bloklashni tasdiqlaysizmi?</p>
          <div class="form-group">
            <label class="form-label">Blok sababi (ixtiyoriy)</label>
            <textarea v-model="blockReason" class="form-control textarea" placeholder="Blok sababi..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showBlockModal=false">Bekor</button>
          <button class="btn btn-danger" @click="confirmBlock">🚫 Bloklash</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api.js'

const items = ref([])
const loading = ref(true)
const search = ref('')
const filterBlocked = ref('')
const showDetail = ref(false)
const detailUser = ref(null)
const detailOrders = ref([])
const showBlockModal = ref(false)
const blockTarget = ref(null)
const blockReason = ref('')

const filtered = computed(() => {
  let list = items.value
  if (search.value) {
    const s = search.value.toLowerCase()
    list = list.filter(u =>
      (u.full_name || '').toLowerCase().includes(s) ||
      (u.phone || '').includes(s) ||
      (u.email || '').toLowerCase().includes(s)
    )
  }
  if (filterBlocked.value !== '') {
    const blocked = filterBlocked.value === 'true'
    list = list.filter(u => u.is_blocked === blocked)
  }
  return list
})

function formatDate(d) { return d ? new Date(d).toLocaleDateString('uz-UZ') : null }
function formatPrice(v) { return v ? Number(v).toLocaleString('uz-UZ') + ' so\'m' : '0' }

async function load() {
  loading.value = true
  try {
    const res = await api.get('/api/users')
    items.value = res.data
  } finally {
    loading.value = false
  }
}

async function viewUser(u) {
  detailUser.value = u
  showDetail.value = true
  try {
    const res = await api.get(`/api/users/${u.id}/orders`)
    detailOrders.value = res.data
  } catch { detailOrders.value = [] }
}

function blockUser(u) {
  blockTarget.value = u
  blockReason.value = ''
  showBlockModal.value = true
}

async function confirmBlock() {
  await api.post(`/api/users/${blockTarget.value.id}/block`, { reason: blockReason.value || null })
  showBlockModal.value = false
  await load()
}

async function unblockUser(id) {
  if (!confirm('Foydalanuvchi blokini ochmoqchimisiz?')) return
  await api.post(`/api/users/${id}/unblock`)
  await load()
}

onMounted(load)
</script>
