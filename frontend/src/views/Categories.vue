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
              <th>Slug</th>
              <th>Ota kategoriya</th>
              <th>Tartib</th>
              <th>Holati</th>
              <th>Asosiy</th>
              <th>Yaratilgan</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in filtered" :key="cat.id">
              <td>{{ cat.id }}</td>
              <td>
                <div class="fw-600">{{ cat.name }}</div>
                <div class="text-muted" style="font-size:12px;">{{ cat.name_ru || '' }}</div>
              </td>
              <td><code style="font-size:12px;color:#1565c0;">{{ cat.slug || '-' }}</code></td>
              <td>{{ getParentName(cat.parent_id) }}</td>
              <td>{{ cat.sort_order }}</td>
              <td>
                <span :class="cat.is_active ? 'badge badge-success' : 'badge badge-danger'">
                  {{ cat.is_active ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td>
                <span :class="cat.show_on_home ? 'badge badge-success' : 'badge badge-secondary'">
                  {{ cat.show_on_home ? 'Ha' : 'Yo‘q' }}
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

    <!-- Drawer -->
    <div v-if="showModal" class="drawer-overlay" @click.self="closeModal">
      <div class="drawer">
        <div class="drawer-header">
          <div class="modal-title">{{ editing ? 'Kategoriyani tahrirlash' : 'Yangi kategoriya' }}</div>
          <button class="btn-icon" @click="closeModal">✕</button>
        </div>
        <div class="drawer-body">
          <div v-if="formError" class="alert alert-error" style="margin-bottom:16px;">{{ formError }}</div>
          <div class="form-section-title">Asosiy ma'lumot</div>
          <div class="form-group">
            <label class="form-label">Kategoriya nomi *</label>
            <input v-model="form.name" type="text" class="form-control" placeholder="Masalan: Elektronika" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nomi (UZ)</label>
              <input v-model="form.name_uz" type="text" class="form-control" placeholder="O'zbekcha nomi" />
            </div>
            <div class="form-group">
              <label class="form-label">Slug</label>
              <input v-model="form.slug" type="text" class="form-control" placeholder="elektronika" />
            </div>
          </div>
          <div class="form-section-title">Tuzilma</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Ota kategoriya</label>
              <select v-model="form.parent_id" class="form-control">
                <option :value="null">Yo'q, asosiy kategoriya</option>
                <option v-for="c in parentOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Tartib raqami</label>
              <input v-model.number="form.sort_order" type="number" class="form-control" placeholder="0" min="0" />
            </div>
          </div>
          <div class="form-section-title">Ko'rinish</div>
          <div class="checkbox-grid">
            <label class="checkbox-item"><input type="checkbox" v-model="form.is_active" /><span>Faol</span></label>
            <label class="checkbox-item"><input type="checkbox" v-model="form.show_in_menu" /><span>Menyuda ko'rsatish</span></label>
            <label class="checkbox-item"><input type="checkbox" v-model="form.show_on_home" /><span>Asosiy sahifada ko'rsatish</span></label>
          </div>
        </div>
        <div class="drawer-footer">
          <button class="btn btn-outline" @click="closeModal">Bekor qilish</button>
          <button class="btn btn-primary" @click="saveItem" :disabled="saving">
            {{ saving ? 'Saqlanmoqda...' : '💾 Saqlash' }}
          </button>
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

const defaultForm = () => ({
  name: '', name_uz: '', name_ru: '', name_en: '',
  slug: '', description: '', location: '',
  icon_url: '', image_url: '', banner_url: '', cover_url: '',
  parent_id: null, sort_order: 0,
  is_active: true, show_on_home: false, show_in_menu: true,
  is_popular: false, is_new: false, is_recommended: false,
  filter_enabled: false, show_in_discount: false
})

const form = ref(defaultForm())

const filtered = computed(() =>
  items.value.filter(c => c.name.toLowerCase().includes(search.value.toLowerCase()))
)

const parentOptions = computed(() => {
  if (!editing.value) return items.value
  return items.value.filter(c => c.id !== editing.value.id)
})

function formatDate(d) { return d ? new Date(d).toLocaleDateString('uz-UZ') : '-' }
function getParentName(id) { return id ? items.value.find(c => c.id === id)?.name || '-' : '-' }

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
  form.value = defaultForm()
  formError.value = ''
  showModal.value = true
}

function openEdit(cat) {
  editing.value = cat
  form.value = { ...defaultForm(), ...cat }
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

<style scoped>
.form-section-title {
  font-weight: 700;
  font-size: 13px;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 20px 0 12px;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--border);
}
.checkbox-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.15s;
  font-size: 13px;
}
.checkbox-item:hover { background: #f0f4ff; }
.checkbox-item input[type="checkbox"] { width: 16px; height: 16px; accent-color: var(--primary); }
</style>
