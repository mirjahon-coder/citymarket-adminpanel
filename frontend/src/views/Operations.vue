<template>
  <div class="operations-page">
    <div class="page-heading">
      <div><span class="eyebrow">City Market control</span><h1>Operatsiyalar</h1><p>Marketplace kampaniyalari, kassir va tizim nazorati.</p></div>
      <button class="btn btn-primary" @click="loadAll">↻ Yangilash</button>
    </div>

    <div class="operation-tabs">
      <button v-for="tab in tabs" :key="tab.key" :class="{ active: currentTab === tab.key }" @click="currentTab = tab.key">{{ tab.label }}</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <section v-if="currentTab === 'banners'" class="card">
      <div class="card-header"><div><div class="eyebrow">Marketing</div><div class="card-title">Bannerlar</div></div><button class="btn btn-primary" @click="openBanner">+ Banner</button></div>
      <div v-if="!banners.length" class="empty-state"><p>Bannerlar hali qo'shilmagan.</p></div>
      <div v-else class="ops-grid"><article v-for="banner in banners" :key="banner.id" class="ops-item"><img :src="banner.image_url" :alt="banner.title" /><div><strong>{{ banner.title }}</strong><small>{{ banner.link_url || 'Havola yo‘q' }}</small></div><button class="btn btn-sm btn-danger" @click="remove('/api/banners/' + banner.id, loadBanners)">O'chirish</button></article></div>
    </section>

    <section v-if="currentTab === 'promotions'" class="card">
      <div class="card-header"><div><div class="eyebrow">Savdo faolligi</div><div class="card-title">Aksiyalar</div></div><button class="btn btn-primary" @click="openPromotion">+ Aksiya</button></div>
      <div v-if="!promotions.length" class="empty-state"><p>Aksiyalar hali qo'shilmagan.</p></div>
      <div v-else class="table-wrap"><table><thead><tr><th>Nomi</th><th>Chegirma</th><th>Muddati</th><th>Holati</th><th></th></tr></thead><tbody><tr v-for="promotion in promotions" :key="promotion.id"><td class="fw-600">{{ promotion.title }}</td><td>{{ promotion.discount_percent }}%</td><td>{{ formatDate(promotion.ends_at) }}</td><td><span :class="promotion.is_active ? 'badge badge-success' : 'badge badge-danger'">{{ promotion.is_active ? 'Faol' : 'Nofaol' }}</span></td><td><button class="btn btn-sm btn-danger" @click="remove('/api/promotions/' + promotion.id, loadPromotions)">O'chirish</button></td></tr></tbody></table></div>
    </section>

    <section v-if="currentTab === 'cashier'" class="card narrow-card">
      <div class="card-header"><div><div class="eyebrow">Omad Barabani</div><div class="card-title">Kassir tekshiruvi</div></div><span class="badge badge-primary">QR nazorat</span></div>
      <p class="text-muted mb-16">Mijoz ko'rsatgan QR tokenni kiriting va yutuq holatini tekshiring.</p>
      <div class="form-group"><label class="form-label">QR token</label><input v-model="qrToken" class="form-control" placeholder="QR tokenni kiriting" /></div>
      <div class="flex gap-8"><button class="btn btn-outline" @click="verifyQr">Tekshirish</button><button v-if="winning" class="btn btn-success" @click="confirmPrize">Sovg'a berildi</button></div>
      <div v-if="winning" class="verify-result"><strong>{{ winning.prize_name }}</strong><span>{{ winning.status }} · #{{ winning.winning_id }}</span></div>
    </section>

    <section v-if="currentTab === 'notifications'" class="card narrow-card">
      <div class="card-header"><div><div class="eyebrow">Customer app</div><div class="card-title">Push xabar</div></div></div>
      <div class="form-group"><label class="form-label">Sarlavha</label><input v-model="notification.title" class="form-control" placeholder="Yangi aksiya" /></div>
      <div class="form-group"><label class="form-label">Xabar matni</label><textarea v-model="notification.body" class="form-control textarea" placeholder="Mijozlarga ko'rinadigan xabar..."></textarea></div>
      <div class="form-group"><label class="form-label">Mijoz ID (ixtiyoriy)</label><input v-model.number="notification.customer_id" type="number" class="form-control" placeholder="Bo'sh qoldirilsa umumiy" /></div>
      <button class="btn btn-primary" @click="sendNotification">Xabarni saqlash</button>
    </section>

    <section v-if="currentTab === 'roles'" class="card">
      <div class="card-header"><div><div class="eyebrow">Access control</div><div class="card-title">Rollar</div></div><button class="btn btn-primary" @click="openRole">+ Rol</button></div>
      <div class="ops-grid"><article v-for="role in roles" :key="role.id" class="ops-item role-item"><div class="role-symbol">⌁</div><div><strong>{{ role.name }}</strong><small>{{ (role.permissions || []).join(', ') || 'Ruxsatlar belgilanmagan' }}</small></div><button class="btn btn-sm btn-danger" @click="remove('/api/roles/' + role.id, loadRoles)">O'chirish</button></article></div>
    </section>

    <section v-if="currentTab === 'sms'" class="card">
      <div class="card-header"><div><div class="eyebrow">SMS</div><div class="card-title">SMS yuborish loglari</div></div></div>
      <div class="table-wrap"><table><thead><tr><th>Telefon</th><th>Holat</th><th>SMS holati</th><th>Urinishlar</th><th>Yuborilgan</th><th>Muddati</th></tr></thead><tbody><tr v-for="item in smsRequests" :key="item.id"><td class="fw-600">{{ item.phone }}</td><td>{{ item.status }}</td><td>{{ item.sms_status }}</td><td>{{ item.attempts }}</td><td>{{ formatDate(item.sent_at) }}</td><td>{{ formatDate(item.expires_at) }}</td></tr></tbody></table></div>
    </section>

    <section v-if="currentTab === 'audit'" class="card">
      <div class="card-header"><div><div class="eyebrow">Security</div><div class="card-title">Audit log</div></div></div>
      <div class="table-wrap"><table><thead><tr><th>Harakat</th><th>Entity</th><th>ID</th><th>Sana</th></tr></thead><tbody><tr v-for="entry in audit" :key="entry.id"><td class="fw-600">{{ entry.action }}</td><td>{{ entry.entity || '-' }}</td><td>{{ entry.entity_id || '-' }}</td><td>{{ formatDate(entry.created_at) }}</td></tr></tbody></table></div>
    </section>

    <div v-if="modal" class="modal-overlay" @click.self="modal = null"><div class="modal"><div class="modal-header"><div class="modal-title">{{ modal === 'banner' ? 'Yangi banner' : modal === 'promotion' ? 'Yangi aksiya' : 'Yangi rol' }}</div><button class="btn-icon" @click="modal = null">✕</button></div><div class="modal-body">
      <template v-if="modal === 'banner'"><div class="form-group"><label class="form-label">Nomi</label><input v-model="bannerForm.title" class="form-control" /></div><div class="form-group"><label class="form-label">Rasm URL</label><input v-model="bannerForm.image_url" class="form-control" /></div><div class="form-group"><label class="form-label">Havola</label><input v-model="bannerForm.link_url" class="form-control" /></div></template>
      <template v-else-if="modal === 'promotion'"><div class="form-group"><label class="form-label">Nomi</label><input v-model="promotionForm.title" class="form-control" /></div><div class="form-group"><label class="form-label">Chegirma foizi</label><input v-model.number="promotionForm.discount_percent" type="number" class="form-control" /></div><div class="form-group"><label class="form-label">Tugash sanasi</label><input v-model="promotionForm.ends_at" type="datetime-local" class="form-control" /></div></template>
      <template v-else><div class="form-group"><label class="form-label">Rol nomi</label><input v-model="roleForm.name" class="form-control" placeholder="Content manager" /></div><div class="form-group"><label class="form-label">Ruxsatlar, vergul bilan</label><input v-model="rolePermissions" class="form-control" placeholder="products.read, products.write" /></div></template>
    </div><div class="modal-footer"><button class="btn btn-outline" @click="modal = null">Bekor</button><button class="btn btn-primary" @click="saveModal">Saqlash</button></div></div></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const tabs = [{ key: 'banners', label: 'Bannerlar' }, { key: 'promotions', label: 'Aksiyalar' }, { key: 'cashier', label: 'Kassir' }, { key: 'notifications', label: 'Push xabar' }, { key: 'roles', label: 'Rollar' }, { key: 'sms', label: 'SMS log' }, { key: 'audit', label: 'Audit log' }]
const currentTab = ref('banners')
const banners = ref([]); const promotions = ref([]); const roles = ref([]); const smsRequests = ref([]); const audit = ref([])
const qrToken = ref(''); const winning = ref(null); const error = ref(''); const success = ref(''); const modal = ref(null)
const bannerForm = ref({ title: '', image_url: '', link_url: '', is_active: true, sort_order: 0 })
const promotionForm = ref({ title: '', description: '', discount_percent: 0, ends_at: null, is_active: true })
const roleForm = ref({ name: '', permissions: [] }); const rolePermissions = ref('')
const notification = ref({ title: '', body: '', customer_id: null })
function formatDate(value) { return value ? new Date(value).toLocaleDateString('uz-UZ') : '-' }
function clearMessage() { error.value = ''; success.value = '' }
async function loadBanners() { banners.value = (await api.get('/api/banners')).data }
async function loadPromotions() { promotions.value = (await api.get('/api/promotions')).data }
async function loadRoles() { roles.value = (await api.get('/api/roles')).data }
async function loadAudit() { audit.value = (await api.get('/api/audit-logs')).data }
async function loadSmsRequests() { smsRequests.value = (await api.get('/api/admin/sms-requests')).data }
async function loadAll() { clearMessage(); await Promise.all([loadBanners(), loadPromotions(), loadRoles(), loadSmsRequests(), loadAudit()]) }
function openBanner() { bannerForm.value = { title: '', image_url: '', link_url: '', is_active: true, sort_order: 0 }; modal.value = 'banner' }
function openPromotion() { promotionForm.value = { title: '', description: '', discount_percent: 0, ends_at: null, is_active: true }; modal.value = 'promotion' }
function openRole() { roleForm.value = { name: '', permissions: [] }; rolePermissions.value = ''; modal.value = 'role' }
async function saveModal() { clearMessage(); try { if (modal.value === 'banner') await api.post('/api/banners', bannerForm.value); if (modal.value === 'promotion') await api.post('/api/promotions', promotionForm.value); if (modal.value === 'role') await api.post('/api/roles', { ...roleForm.value, permissions: rolePermissions.value.split(',').map(item => item.trim()).filter(Boolean) }); modal.value = null; success.value = 'Saqlandi'; await loadAll() } catch (e) { error.value = e.response?.data?.detail || 'Saqlashda xatolik' } }
async function remove(url, reload) { if (!confirm('O\'chirishni tasdiqlaysizmi?')) return; await api.delete(url); await reload() }
async function verifyQr() { clearMessage(); winning.value = null; try { winning.value = (await api.post('/api/cashier/verify-check', { qr_token: qrToken.value })).data } catch (e) { error.value = e.response?.data?.detail || 'QR topilmadi' } }
async function confirmPrize() { await api.post('/api/cashier/confirm-prize', { qr_token: qrToken.value }); success.value = 'Sovg\'a berildi'; winning.value = null }
async function sendNotification() { clearMessage(); try { await api.post('/api/notifications/send', notification.value); success.value = 'Xabar saqlandi'; notification.value = { title: '', body: '', customer_id: null } } catch (e) { error.value = e.response?.data?.detail || 'Xatolik' } }
onMounted(loadAll)
</script>

<style scoped>
.page-heading { display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:24px; }
.page-heading h1 { margin-top:6px; font:600 27px 'Space Grotesk', sans-serif; }
.page-heading p { color:var(--text-secondary); margin-top:5px; }
.operation-tabs { display:flex; gap:6px; overflow:auto; margin-bottom:18px; padding-bottom:3px; }
.operation-tabs button { background:#fff; border:1px solid var(--border); color:var(--text-secondary); border-radius:8px; padding:9px 14px; white-space:nowrap; }
.operation-tabs button.active { color:#fff; background:var(--primary); border-color:var(--primary); }
.narrow-card { max-width:680px; }
.ops-grid { display:grid; gap:10px; }
.ops-item { display:flex; align-items:center; gap:13px; border:1px solid var(--border); border-radius:9px; padding:11px; }
.ops-item img { width:70px; height:45px; object-fit:cover; border-radius:6px; background:#eef2f6; }
.ops-item > div:not(.role-symbol) { display:flex; flex:1; flex-direction:column; gap:4px; }
.ops-item small { color:var(--text-muted); font-size:11px; }
.role-symbol { width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#e8f8f1; color:var(--success); font-size:20px; }
.verify-result { margin-top:18px; display:flex; flex-direction:column; gap:4px; padding:13px; background:var(--success-light); border-radius:8px; color:var(--success); }
@media (max-width:760px) { .page-heading { align-items:flex-start; gap:14px; flex-direction:column; } }
</style>
