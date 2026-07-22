<template>
  <div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">🔑 Adminlar</div>
        <button class="btn btn-primary" @click="showModal=true">+ Admin qo'shish</button>
      </div>

      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Login</th>
              <th>Holati</th>
              <th>Yaratilgan</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in admins" :key="a.id">
              <td>{{ a.id }}</td>
              <td class="fw-600">{{ a.username }}</td>
              <td><span :class="a.is_active ? 'badge badge-success' : 'badge badge-danger'">{{ a.is_active ? 'Faol' : 'Nofaol' }}</span></td>
              <td>{{ formatDate(a.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">Yangi admin qo'shish</div>
          <button class="btn-icon" @click="showModal=false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="error" class="alert alert-error">{{ error }}</div>
          <div class="form-group">
            <label class="form-label">Login *</label>
            <input v-model="form.username" type="text" class="form-control" placeholder="username" />
          </div>
          <div class="form-group">
            <label class="form-label">Parol *</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="kuchli parol kiriting" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showModal=false">Bekor</button>
          <button class="btn btn-primary" @click="save" :disabled="saving">{{ saving ? 'Saqlanmoqda...' : 'Qo\'shish' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const admins = ref([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({ username: '', password: '' })

function formatDate(d) { return d ? new Date(d).toLocaleDateString('uz-UZ') : '-' }

async function load() {
  loading.value = true
  try {
    const res = await api.get('/api/auth/admins')
    admins.value = res.data
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!form.value.username || !form.value.password) { error.value = 'Login va parol majburiy'; return }
  saving.value = true; error.value = ''
  try {
    await api.post('/api/auth/admins', form.value)
    showModal.value = false
    form.value = { username: '', password: '' }
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Xatolik'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
