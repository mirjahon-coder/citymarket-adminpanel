<template>
  <div>
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">📨 SMS yuborish</div>
          <div class="text-muted">Admin paneldan tezkor SMS xabarlarini jo‘natish</div>
        </div>
        <button class="btn btn-primary" @click="sendSms" :disabled="sending">
          {{ sending ? 'Yuborilmoqda...' : 'SMS jo‘natish' }}
        </button>
      </div>

      <div v-if="message" :class="message.type === 'error' ? 'alert alert-error' : 'alert alert-success'">{{ message.text }}</div>

      <div class="form-group">
        <label class="form-label">Telefon raqam</label>
        <input v-model="form.phone" class="form-control" placeholder="998901234567" />
      </div>
      <div class="form-group">
        <label class="form-label">Xabar matni</label>
        <textarea v-model="form.message" class="form-control textarea" placeholder="SMS matnini kiriting"></textarea>
      </div>
    </div>

    <div class="card" style="margin-top: 20px;">
      <div class="card-header">
        <div class="card-title">🕘 So‘nggi SMSlar</div>
      </div>
      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else-if="history.length === 0" class="empty-state">Hech qanday SMS yozuvi yo‘q</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Telefon</th>
              <th>Holat</th>
              <th>SMS holati</th>
              <th>Yaratilgan</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in history" :key="item.id">
              <td>{{ item.phone }}</td>
              <td><span :class="item.status === 'sent' ? 'badge badge-success' : 'badge badge-warning'">{{ item.status }}</span></td>
              <td>{{ item.sms_status }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const form = ref({ phone: '', message: 'Assalomu alaykum, bu test SMS xabari' })
const message = ref(null)
const sending = ref(false)
const loading = ref(true)
const history = ref([])

function formatDate(value) {
  return value ? new Date(value).toLocaleString('uz-UZ') : '-'
}

async function loadHistory() {
  loading.value = true
  try {
    const res = await api.get('/api/sms/history')
    history.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function sendSms() {
  if (!form.value.phone || !form.value.message) {
    message.value = { type: 'error', text: 'Telefon raqam va xabar matni majburiy' }
    return
  }

  sending.value = true
  message.value = null
  try {
    const res = await api.post('/api/sms/send', form.value)
    message.value = { type: 'success', text: res.data.message || 'SMS yuborildi' }
    form.value.phone = ''
    form.value.message = 'Assalomu alaykum, bu test SMS xabari'
    await loadHistory()
  } catch (e) {
    message.value = { type: 'error', text: e.response?.data?.detail || 'SMS yuborishda xatolik yuz berdi' }
  } finally {
    sending.value = false
  }
}

onMounted(loadHistory)
</script>
