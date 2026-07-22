<template>
  <div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">Mahsulotlar</div>
        <button class="btn btn-primary" @click="openAdd">+ Mahsulot qo'shish</button>
      </div>

      <div class="search-bar">
        <input v-model="search" type="text" class="search-input" placeholder="Mahsulot qidirish..." />
        <select v-model="filterCat" class="form-control" style="width:180px;">
          <option value="">Barcha kategoriyalar</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <p>Mahsulotlar topilmadi</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nomi</th>
              <th>Narxi</th>
              <th>Chegirma narxi</th>
              <th>Miqdori</th>
              <th>Kategoriya</th>
              <th>Holati</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id">
              <td>{{ p.id }}</td>
              <td class="fw-600">{{ p.name }}</td>
              <td>{{ formatPrice(p.price) }}</td>
              <td>
                <span v-if="p.has_discount" class="text-danger fw-600">{{ formatPrice(p.discount_price) }}</span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span :class="p.stock <= 5 ? 'text-danger fw-600' : ''">{{ p.stock }}</span>
              </td>
              <td>{{ getCatName(p.category_id) }}</td>
              <td>
                <span :class="p.is_active ? 'badge badge-success' : 'badge badge-danger'">
                  {{ p.is_active ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td>
                <div class="flex gap-8">
                  <button class="btn btn-sm btn-outline" @click="openEdit(p)">✏️</button>
                  <button class="btn btn-sm btn-danger" @click="deleteItem(p.id)">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal" style="max-width:700px;">
        <div class="modal-header">
          <div class="modal-title">{{ editing ? 'Mahsulotni tahrirlash' : 'Yangi mahsulot' }}</div>
          <button class="btn-icon" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="formError" class="alert alert-error">{{ formError }}</div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nomi *</label>
              <input v-model="form.name" type="text" class="form-control" placeholder="Mahsulot nomi" />
            </div>
            <div class="form-group">
              <label class="form-label">Kategoriya</label>
              <select v-model="form.category_id" class="form-control">
                <option :value="null">Tanlang</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Narxi (so'm) *</label>
              <input v-model.number="form.price" type="number" class="form-control" placeholder="0" min="0" />
            </div>
            <div class="form-group">
              <label class="form-label">Miqdori</label>
              <input v-model.number="form.stock" type="number" class="form-control" placeholder="0" min="0" />
            </div>
          </div>

          <div class="form-group">
            <label class="toggle">
              <div class="toggle-switch"><input type="checkbox" v-model="form.has_discount" /><span class="toggle-slider"></span></div>
              Chegirma bor
            </label>
          </div>

          <div v-if="form.has_discount" class="form-group">
            <label class="form-label">Chegirma narxi (so'm)</label>
            <input v-model.number="form.discount_price" type="number" class="form-control" placeholder="0" min="0" />
          </div>

          <div class="form-group">
            <label class="form-label">Qisqacha tavsif</label>
            <textarea v-model="form.description" class="form-control textarea" placeholder="Qisqacha tavsif..."></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">To'liq tavsif</label>
            <textarea v-model="form.full_description" class="form-control textarea" style="min-height:120px;" placeholder="To'liq tavsif va qo'shimcha ma'lumotlar..."></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Brend</label>
              <input v-model="form.brand" type="text" class="form-control" placeholder="Brend nomi" />
            </div>
            <div class="form-group">
              <label class="form-label">SKU / Kod</label>
              <input v-model="form.sku" type="text" class="form-control" placeholder="SKU123" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Vazni (kg)</label>
              <input v-model.number="form.weight" type="number" step="0.01" class="form-control" placeholder="0.5" />
            </div>
            <div class="form-group">
              <label class="form-label">O'lchamlari</label>
              <input v-model="form.dimensions" type="text" class="form-control" placeholder="30x20x10 sm" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Video URL (YouTube yoki boshqa)</label>
            <input v-model="form.video_url" type="url" class="form-control" placeholder="https://youtube.com/watch?v=..." />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="toggle">
                <div class="toggle-switch"><input type="checkbox" v-model="form.is_active" /><span class="toggle-slider"></span></div>
                Faol
              </label>
            </div>
            <div class="form-group">
              <label class="toggle">
                <div class="toggle-switch"><input type="checkbox" v-model="form.is_featured" /><span class="toggle-slider"></span></div>
                Tavsiya etilgan
              </label>
            </div>
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
const categories = ref([])
const loading = ref(true)
const search = ref('')
const filterCat = ref('')
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')

const defaultForm = () => ({
  name: '', description: '', full_description: '', price: 0, discount_price: null,
  has_discount: false, stock: 0, sku: '', brand: '', weight: null, dimensions: '',
  video_url: '', is_active: true, is_featured: false, category_id: null
})

const form = ref(defaultForm())

const filtered = computed(() => {
  let list = items.value
  if (search.value) list = list.filter(p => p.name.toLowerCase().includes(search.value.toLowerCase()))
  if (filterCat.value) list = list.filter(p => p.category_id === filterCat.value)
  return list
})

function formatPrice(v) { return v ? Number(v).toLocaleString('uz-UZ') + ' so\'m' : '-' }
function getCatName(id) { return categories.value.find(c => c.id === id)?.name || '-' }

async function load() {
  loading.value = true
  try {
    const [pr, cr] = await Promise.all([api.get('/api/products'), api.get('/api/categories')])
    items.value = pr.data
    categories.value = cr.data
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

function openEdit(p) {
  editing.value = p
  form.value = { ...defaultForm(), ...p }
  formError.value = ''
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function saveItem() {
  if (!form.value.name.trim()) { formError.value = 'Nomi majburiy'; return }
  if (!form.value.price) { formError.value = 'Narxi majburiy'; return }
  saving.value = true; formError.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.has_discount) payload.discount_price = null
    if (editing.value) {
      await api.put(`/api/products/${editing.value.id}`, payload)
    } else {
      await api.post('/api/products', payload)
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
  if (!confirm('Mahsulotni o\'chirmoqchimisiz?')) return
  await api.delete(`/api/products/${id}`)
  await load()
}

onMounted(load)
</script>
