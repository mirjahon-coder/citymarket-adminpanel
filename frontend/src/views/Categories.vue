<template>
  <div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">Kategoriyalar</div>
        <button class="btn btn-primary" @click="openAdd">+ Kategoriya qo'shish</button>
      </div>

      <div class="search-bar">
        <input v-model="search" type="text" class="search-input" placeholder="Qidirish..." />
      </div>

      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="empty-icon">📂</div>
        <p>Kategoriyalar topilmadi</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nomi</th>
              <th>Tavsif</th>
              <th>Holati</th>
              <th>Yaratilgan</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in filtered" :key="cat.id">
              <td>{{ cat.id }}</td>
              <td class="fw-600">{{ cat.name }}</td>
              <td>{{ cat.description || '-' }}</td>
              <td>
                <span :class="cat.is_active ? 'badge badge-success' : 'badge badge-danger'">
                  {{ cat.is_active ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td>{{ formatDate(cat.created_at) }}</td>
              <td>
                <div class="flex gap-8">
                  <button class="btn btn-sm btn-outline" @click="openEdit(cat)">✏️ Tahrir</button>
                  <button class="btn btn-sm btn-danger" @click="deleteItem(cat.id)">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">{{ editing ? 'Kategoriyani tahrirlash' : 'Yangi kategoriya' }}</div>
          <button class="btn-icon" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="formError" class="alert alert-error">{{ formError }}</div>
          <div class="form-group">
            <label class="form-label">Nomi *</label>
            <input v-model="form.name" type="text" class="form-control" placeholder="Kategoriya nomi" required />
          </div>
          <div class="form-group">
            <label class="form-label">Tavsif</label>
            <textarea v-model="form.description" class="form-control textarea" placeholder="Qisqacha tavsif"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Rasm URL</label>
            <input v-model="form.image_url" type="url" class="form-control" placeholder="https://" />
          </div>
          <div class="form-group">
            <label class="toggle">
              <div class="toggle-switch"><input type="checkbox" v-model="form.is_active" /><span class="toggle-slider"></span></div>
              Faol
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeModal">Bekor</button>
          <button class="btn btn-primary" @click="saveItem" :disabled="saving">{{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}</button>
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
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

const form = ref({ name: '', description: '', image_url: '', is_active: true })

const filtered = computed(() =>
  items.value.filter(c => c.name.toLowerCase().includes(search.value.toLowerCase()))
)

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('uz-UZ') : '-'
}

async function load() {
  loading.value = true
  try {
    const res = await api.get('/api/categories')
    items.value = res.data
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editing.value = null
  form.value = { name: '', description: '', image_url: '', is_active: true }
  formError.value = ''
  showModal.value = true
}

function openEdit(cat) {
  editing.value = cat
  form.value = { name: cat.name, description: cat.description || '', image_url: cat.image_url || '', is_active: cat.is_active }
  formError.value = ''
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function saveItem() {
  if (!form.value.name.trim()) { formError.value = 'Nomi majburiy'; return }
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await api.put(`/api/categories/${editing.value.id}`, form.value)
    } else {
      await api.post('/api/categories', form.value)
    }
    closeModal()
    await load()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Xatolik yuz berdi'
  } finally {
    saving.value = false
  }
}

async function deleteItem(id) {
  if (!confirm('Kategoriyani o\'chirmoqchimisiz?')) return
  await api.delete(`/api/categories/${id}`)
  await load()
}

onMounted(load)
</script>
