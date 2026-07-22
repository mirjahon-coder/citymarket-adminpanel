<template>
  <div>
    <!-- Baraban list -->
    <div class="card mb-16">
      <div class="card-header">
        <div class="card-title">🎡 Barabanlar</div>
        <button class="btn btn-primary" @click="openAddBaraban">+ Baraban qo'shish</button>
      </div>

      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else-if="barabanlar.length === 0" class="empty-state">
        <div class="empty-icon">🎡</div>
        <p>Barabanlar topilmadi. Yangi baraban qo'shing.</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nomi</th>
              <th>Auditoriya</th>
              <th>Sovg'alar</th>
              <th>Holati</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in barabanlar" :key="b.id" :class="{ 'selected-row': selected?.id === b.id }">
              <td>{{ b.id }}</td>
              <td class="fw-600">{{ b.name }}</td>
              <td>
                <span :class="b.target_audience === 'yoshlar' ? 'badge badge-primary' : 'badge badge-warning'">
                  {{ b.target_audience === 'yoshlar' ? '👦 Yoshlar' : '👨 Kattallar' }}
                </span>
              </td>
              <td>{{ b.prizes?.length || 0 }} ta sovg'a</td>
              <td>
                <span :class="b.is_active ? 'badge badge-success' : 'badge badge-danger'">
                  {{ b.is_active ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td>
                <div class="flex gap-8">
                  <button class="btn btn-sm btn-primary" @click="selectBaraban(b)">🎁 Sovg'alar</button>
                  <button class="btn btn-sm btn-outline" @click="openEditBaraban(b)">✏️</button>
                  <button class="btn btn-sm btn-danger" @click="deleteBaraban(b.id)">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Prizes section -->
    <div v-if="selected" class="card">
      <div class="card-header">
        <div class="card-title">🎁 "{{ selected.name }}" barabanining sovg'alari</div>
        <button class="btn btn-primary" @click="openAddPrize">+ Sovg'a qo'shish</button>
      </div>
      <div v-if="selected.prizes?.length === 0" class="empty-state">
        <div class="empty-icon">🎁</div>
        <p>Bu barabanda sovg'alar yo'q</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Sovg'a nomi</th>
              <th>Turi</th>
              <th>Ehtimollik</th>
              <th>Holati</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in selected.prizes" :key="p.id">
              <td>{{ p.id }}</td>
              <td class="fw-600">
                {{ p.name }}
                <span v-if="p.is_mega_prize" class="badge badge-warning" style="margin-left:6px;">⭐ Mega</span>
              </td>
              <td>
                {{ p.probability_type === 'count' ? 'Soniga ko\'ra' : 'Foiz bo\'yicha' }}
              </td>
              <td>
                <span v-if="p.probability_type === 'count'">
                  {{ p.total_count }} ta ichidan 1 ta
                </span>
                <span v-else>
                  {{ p.probability_value }}%
                </span>
              </td>
              <td>
                <span :class="p.is_active ? 'badge badge-success' : 'badge badge-danger'">
                  {{ p.is_active ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td>
                <div class="flex gap-8">
                  <button class="btn btn-sm btn-outline" @click="openEditPrize(p)">✏️</button>
                  <button class="btn btn-sm btn-danger" @click="deletePrize(p.id)">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Baraban Modal -->
    <div v-if="showBarabanModal" class="modal-overlay" @click.self="showBarabanModal=false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">{{ editingBaraban ? 'Barabanni tahrirlash' : 'Yangi baraban' }}</div>
          <button class="btn-icon" @click="showBarabanModal=false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Nomi *</label>
            <input v-model="barabanForm.name" type="text" class="form-control" placeholder="Baraban nomi" />
          </div>
          <div class="form-group">
            <label class="form-label">Auditoriya</label>
            <select v-model="barabanForm.target_audience" class="form-control">
              <option value="yoshlar">👦 Yoshlar uchun</option>
              <option value="kattallar">👨 Kattallar uchun</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Tavsif</label>
            <textarea v-model="barabanForm.description" class="form-control textarea"></textarea>
          </div>
          <div class="form-group">
            <label class="toggle">
              <div class="toggle-switch"><input type="checkbox" v-model="barabanForm.is_active" /><span class="toggle-slider"></span></div>
              Faol
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showBarabanModal=false">Bekor</button>
          <button class="btn btn-primary" @click="saveBaraban">Saqlash</button>
        </div>
      </div>
    </div>

    <!-- Prize Modal -->
    <div v-if="showPrizeModal" class="modal-overlay" @click.self="showPrizeModal=false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">{{ editingPrize ? 'Sovg\'ani tahrirlash' : 'Yangi sovg\'a' }}</div>
          <button class="btn-icon" @click="showPrizeModal=false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Sovg'a nomi *</label>
            <input v-model="prizeForm.name" type="text" class="form-control" placeholder="Sovg'a nomi" />
          </div>
          <div class="form-group">
            <label class="form-label">Tavsif</label>
            <textarea v-model="prizeForm.description" class="form-control textarea"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Rasm URL</label>
            <input v-model="prizeForm.image_url" type="url" class="form-control" placeholder="https://" />
          </div>
          <div class="form-group">
            <label class="toggle">
              <div class="toggle-switch"><input type="checkbox" v-model="prizeForm.is_mega_prize" /><span class="toggle-slider"></span></div>
              ⭐ Mega sovg'a
            </label>
          </div>
          <hr class="divider" />
          <div class="form-group">
            <label class="form-label">Tushish ehtimoli turi</label>
            <select v-model="prizeForm.probability_type" class="form-control">
              <option value="count">Soniga ko'ra (masalan, 10 tadan 1 ta)</option>
              <option value="percent">Foiz bo'yicha (masalan, 5%)</option>
            </select>
          </div>
          <div v-if="prizeForm.probability_type === 'count'" class="form-group">
            <label class="form-label">Necha marta aylanishda 1 ta tushadi</label>
            <input v-model.number="prizeForm.total_count" type="number" class="form-control" min="1" placeholder="10" />
            <p class="text-muted" style="margin-top:4px;">Masalan: 10 kiritsangiz, har 10 marta aylanishda 1 marta bu sovg'a tushadi</p>
          </div>
          <div v-else class="form-group">
            <label class="form-label">Tushish ehtimoli foizi (%)</label>
            <input v-model.number="prizeForm.probability_value" type="number" class="form-control" min="0" max="100" step="0.1" placeholder="5.0" />
            <p class="text-muted" style="margin-top:4px;">Masalan: 5 kiritsangiz, 5% ehtimollik bilan tushadi</p>
          </div>
          <div class="form-group">
            <label class="toggle">
              <div class="toggle-switch"><input type="checkbox" v-model="prizeForm.is_active" /><span class="toggle-slider"></span></div>
              Faol
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showPrizeModal=false">Bekor</button>
          <button class="btn btn-primary" @click="savePrize">Saqlash</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const barabanlar = ref([])
const loading = ref(true)
const selected = ref(null)

const showBarabanModal = ref(false)
const editingBaraban = ref(null)
const barabanForm = ref({ name: '', target_audience: 'yoshlar', description: '', is_active: true })

const showPrizeModal = ref(false)
const editingPrize = ref(null)
const prizeForm = ref({ name: '', description: '', image_url: '', is_mega_prize: false, probability_type: 'count', probability_value: 10, total_count: 10, is_active: true })

async function load() {
  loading.value = true
  try {
    const res = await api.get('/api/baraban')
    barabanlar.value = res.data
    if (selected.value) {
      selected.value = res.data.find(b => b.id === selected.value.id) || null
    }
  } finally {
    loading.value = false
  }
}

function selectBaraban(b) { selected.value = b }

function openAddBaraban() {
  editingBaraban.value = null
  barabanForm.value = { name: '', target_audience: 'yoshlar', description: '', is_active: true }
  showBarabanModal.value = true
}

function openEditBaraban(b) {
  editingBaraban.value = b
  barabanForm.value = { name: b.name, target_audience: b.target_audience, description: b.description || '', is_active: b.is_active }
  showBarabanModal.value = true
}

async function saveBaraban() {
  if (!barabanForm.value.name.trim()) return
  try {
    if (editingBaraban.value) {
      await api.put(`/api/baraban/${editingBaraban.value.id}`, barabanForm.value)
    } else {
      await api.post('/api/baraban', barabanForm.value)
    }
    showBarabanModal.value = false
    await load()
  } catch (e) { console.error(e) }
}

async function deleteBaraban(id) {
  if (!confirm('Barabanni o\'chirmoqchimisiz?')) return
  await api.delete(`/api/baraban/${id}`)
  if (selected.value?.id === id) selected.value = null
  await load()
}

function openAddPrize() {
  editingPrize.value = null
  prizeForm.value = { name: '', description: '', image_url: '', is_mega_prize: false, probability_type: 'count', probability_value: 10, total_count: 10, is_active: true }
  showPrizeModal.value = true
}

function openEditPrize(p) {
  editingPrize.value = p
  prizeForm.value = { ...p }
  showPrizeModal.value = true
}

async function savePrize() {
  if (!prizeForm.value.name.trim()) return
  try {
    if (editingPrize.value) {
      await api.put(`/api/baraban/${selected.value.id}/prizes/${editingPrize.value.id}`, prizeForm.value)
    } else {
      await api.post(`/api/baraban/${selected.value.id}/prizes`, prizeForm.value)
    }
    showPrizeModal.value = false
    await load()
  } catch (e) { console.error(e) }
}

async function deletePrize(prizeId) {
  if (!confirm('Sovg\'ani o\'chirmoqchimisiz?')) return
  await api.delete(`/api/baraban/${selected.value.id}/prizes/${prizeId}`)
  await load()
}

onMounted(load)
</script>

<style scoped>
.selected-row { background: #e3f2fd !important; }
</style>
