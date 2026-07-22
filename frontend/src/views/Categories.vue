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

          <!-- 1. Nomlar -->
          <div class="form-section-title">🌐 Nomlar</div>
          <div class="form-group">
            <label class="form-label">Kategoriya nomi (asosiy) *</label>
            <input v-model="form.name" type="text" class="form-control" placeholder="Kategoriya nomi" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nomi (UZ)</label>
              <input v-model="form.name_uz" type="text" class="form-control" placeholder="O'zbekcha nomi" />
            </div>
            <div class="form-group">
              <label class="form-label">Nomi (RU)</label>
              <input v-model="form.name_ru" type="text" class="form-control" placeholder="Русское название" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Nomi (EN)</label>
            <input v-model="form.name_en" type="text" class="form-control" placeholder="English name" />
          </div>

          <!-- 2. Meta -->
          <div class="form-section-title">🔗 Meta ma'lumotlar</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Slug</label>
              <input v-model="form.slug" type="text" class="form-control" placeholder="kategoriya-nomi" />
            </div>
            <div class="form-group">
              <label class="form-label">Joylashuvi</label>
              <input v-model="form.location" type="text" class="form-control" placeholder="Masalan: Toshkent" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Tavsif</label>
            <textarea v-model="form.description" class="form-control textarea" placeholder="Kategoriya haqida qisqacha..."></textarea>
          </div>

          <!-- 3. Rasmlar -->
          <div class="form-section-title">🖼️ Rasmlar</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Ikonka URL</label>
              <input v-model="form.icon_url" type="url" class="form-control" placeholder="https://.../icon.png" />
            </div>
            <div class="form-group">
              <label class="form-label">Asosiy rasm URL</label>
              <input v-model="form.image_url" type="url" class="form-control" placeholder="https://.../image.jpg" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Banner rasmi URL</label>
              <input v-model="form.banner_url" type="url" class="form-control" placeholder="https://.../banner.jpg" />
            </div>
            <div class="form-group">
              <label class="form-label">Cover rasmi URL</label>
              <input v-model="form.cover_url" type="url" class="form-control" placeholder="https://.../cover.jpg" />
            </div>
          </div>

          <!-- 4. Tartib -->
          <div class="form-section-title">📋 Tartib va aloqa</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Ota kategoriya</label>
              <select v-model="form.parent_id" class="form-control">
                <option :value="null">— Yo'q (asosiy kategoriya) —</option>
                <option v-for="c in parentOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Tartib raqami</label>
              <input v-model.number="form.sort_order" type="number" class="form-control" placeholder="0" min="0" />
            </div>
          </div>

          <!-- 5. Holat checkboxlar -->
          <div class="form-section-title">✅ Holat va ko'rinish</div>
          <div class="checkbox-grid">
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.is_active" />
              <span>Faol</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.show_in_menu" />
              <span>Menyuda ko'rsatish</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.show_on_home" />
              <span>Asosiy sahifada ko'rsatish</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.is_popular" />
              <span>Mashhur kategoriya</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.is_new" />
              <span>Yangi kategoriya</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.is_recommended" />
              <span>Tavsiya etilgan</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.filter_enabled" />
              <span>Filtrlashni yoqish</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="form.show_in_discount" />
              <span>Chegirma bo'limida ko'rsatish</span>
            </label>
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
