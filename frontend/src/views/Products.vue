<template>
  <div>
    <!-- Ro'yxat -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">Mahsulotlar</div>
        <button class="btn btn-primary" @click="openAdd">+ Mahsulot qo'shish</button>
      </div>
      <div class="search-bar">
        <input v-model="search" type="text" class="search-input" placeholder="Mahsulot qidirish..." />
        <select v-model="filterCat" class="form-control" style="width:200px;">
          <option value="">Barcha kategoriyalar</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div v-if="loading" class="loading-wrap"><div class="spinner"></div></div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="empty-icon">📦</div><p>Mahsulotlar topilmadi</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th><th>Rasm</th><th>Nomi</th><th>Narxi</th>
              <th>Sotuv narxi</th><th>Ombor</th><th>Kategoriya</th><th>Holati</th><th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id">
              <td>{{ p.id }}</td>
              <td>
                <img v-if="p.main_image_url" :src="p.main_image_url" style="width:40px;height:40px;object-fit:cover;border-radius:6px;" />
                <span v-else class="empty-icon" style="font-size:24px;">📦</span>
              </td>
              <td>
                <div class="fw-600">{{ p.name }}</div>
                <div class="text-muted" style="font-size:12px;">{{ p.brand || p.sku || '' }}</div>
              </td>
              <td>{{ formatPrice(p.price) }}</td>
              <td>
                <span v-if="p.has_discount" class="text-danger fw-600">{{ formatPrice(p.sale_price) }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td><span :class="p.stock <= 5 ? 'text-danger fw-600' : ''">{{ p.stock }}</span></td>
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

    <!-- Full-screen wizard -->
    <div v-if="showModal" class="wizard-overlay">
      <div class="wizard-container">
        <!-- Wizard header -->
        <div class="wizard-header">
          <div class="wizard-title">
            {{ editing ? 'Mahsulotni tahrirlash' : 'Yangi mahsulot qo\'shish' }}
          </div>
          <button class="btn-icon" @click="closeModal">✕</button>
        </div>

        <!-- Steps nav -->
        <div class="wizard-steps">
          <div
            v-for="(s, i) in steps"
            :key="i"
            class="wizard-step"
            :class="{ active: step === i, done: step > i }"
            @click="goStep(i)"
          >
            <div class="step-circle">{{ step > i ? '✓' : i + 1 }}</div>
            <div class="step-label">{{ s }}</div>
          </div>
        </div>

        <!-- Body -->
        <div class="wizard-body">
          <div v-if="formError" class="alert alert-error" style="margin-bottom:16px;">{{ formError }}</div>

          <!-- QADAM 1: Asosiy ma'lumotlar -->
          <div v-if="step === 0">
            <div class="form-section-title">📝 Nomlar</div>
            <div class="form-group">
              <label class="form-label">Mahsulot nomi (asosiy) *</label>
              <input v-model="form.name" type="text" class="form-control" placeholder="Mahsulot nomi" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nomi (UZ)</label>
                <input v-model="form.name_uz" type="text" class="form-control" placeholder="O'zbekcha" />
              </div>
              <div class="form-group">
                <label class="form-label">Nomi (RU)</label>
                <input v-model="form.name_ru" type="text" class="form-control" placeholder="Русский" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Nomi (EN)</label>
              <input v-model="form.name_en" type="text" class="form-control" placeholder="English" />
            </div>

            <div class="form-section-title">🔖 Identifikatorlar</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">SKU</label>
                <input v-model="form.sku" type="text" class="form-control" placeholder="SKU-001" />
              </div>
              <div class="form-group">
                <label class="form-label">Barcode</label>
                <input v-model="form.barcode" type="text" class="form-control" placeholder="1234567890" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Brand</label>
                <input v-model="form.brand" type="text" class="form-control" placeholder="Samsung, Apple..." />
              </div>
              <div class="form-group">
                <label class="form-label">Ishlab chiqaruvchi</label>
                <input v-model="form.manufacturer" type="text" class="form-control" placeholder="Kompaniya nomi" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Model</label>
              <input v-model="form.model_name" type="text" class="form-control" placeholder="Galaxy S24 Ultra" />
            </div>

            <div class="form-section-title">📂 Kategoriya</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Kategoriya</label>
                <select v-model="form.category_id" class="form-control">
                  <option :value="null">— Tanlang —</option>
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Subkategoriya</label>
                <input v-model="form.subcategory" type="text" class="form-control" placeholder="Subkategoriya nomi" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Taglar (vergul bilan ajrating)</label>
              <input v-model="tagsInput" type="text" class="form-control" placeholder="oziq-ovqat, meva, yangi" />
            </div>
          </div>

          <!-- QADAM 2: Tavsiflar -->
          <div v-if="step === 1">
            <div class="form-section-title">📄 Tavsiflar</div>
            <div class="form-group">
              <label class="form-label">Qisqa tavsif</label>
              <textarea v-model="form.short_description" class="form-control textarea" style="min-height:80px;" placeholder="Mahsulot haqida qisqacha..."></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Tavsif</label>
              <textarea v-model="form.description" class="form-control textarea" style="min-height:100px;" placeholder="Batafsil tavsif..."></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">To'liq tavsif</label>
              <textarea v-model="form.full_description" class="form-control textarea" style="min-height:140px;" placeholder="To'liq tavsif, xususiyatlar, foydalanish..."></textarea>
            </div>
          </div>

          <!-- QADAM 3: Rasmlar & Video -->
          <div v-if="step === 2">
            <div class="form-section-title">🖼️ Asosiy rasm</div>
            <div class="form-group">
              <label class="form-label">Asosiy rasm URL *</label>
              <input v-model="form.main_image_url" type="url" class="form-control" placeholder="https://..." />
              <img v-if="form.main_image_url" :src="form.main_image_url" style="margin-top:8px;max-height:120px;border-radius:8px;" />
            </div>

            <div class="form-section-title">🖼️ Galereya rasmlari</div>
            <div v-for="(img, i) in galleryList" :key="i" class="flex gap-8" style="margin-bottom:8px;align-items:center;">
              <input v-model="galleryList[i]" type="url" class="form-control" :placeholder="'Rasm URL #' + (i+1)" />
              <button class="btn btn-sm btn-danger" @click="removeGallery(i)">✕</button>
            </div>
            <button class="btn btn-outline btn-sm" @click="addGallery">+ Rasm qo'shish</button>

            <div class="form-section-title">🔮 360° Rasm & Video</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">360° rasm URL (ixtiyoriy)</label>
                <input v-model="form.image_360_url" type="url" class="form-control" placeholder="https://..." />
              </div>
              <div class="form-group">
                <label class="form-label">Video URL (YouTube va boshqa)</label>
                <input v-model="form.video_url" type="url" class="form-control" placeholder="https://youtube.com/..." />
              </div>
            </div>
          </div>

          <!-- QADAM 4: Narx & Ombor -->
          <div v-if="step === 3">
            <div class="form-section-title">💰 Narxlar</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Asl narx (so'm) *</label>
                <input v-model.number="form.price" type="number" class="form-control" placeholder="0" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">Sotuv narxi (so'm)</label>
                <input v-model.number="form.sale_price" type="number" class="form-control" placeholder="0" min="0" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Xarid narxi (so'm)</label>
                <input v-model.number="form.purchase_price" type="number" class="form-control" placeholder="0" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">Cashback %</label>
                <input v-model.number="form.cashback_percent" type="number" class="form-control" placeholder="0" min="0" max="100" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Bonus ball</label>
                <input v-model.number="form.bonus_points" type="number" class="form-control" placeholder="0" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">QQS %</label>
                <input v-model.number="form.vat_percent" type="number" class="form-control" placeholder="0" min="0" max="100" />
              </div>
            </div>

            <div class="form-section-title">🏭 Ombor</div>
            <div class="form-group">
              <label class="form-label">Ombor nomi</label>
              <input v-model="form.warehouse_name" type="text" class="form-control" placeholder="Asosiy ombor" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Soni</label>
                <input v-model.number="form.stock" type="number" class="form-control" placeholder="0" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">Minimal son</label>
                <input v-model.number="form.min_quantity" type="number" class="form-control" placeholder="1" min="1" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Maksimal buyurtma</label>
                <input v-model.number="form.max_order_qty" type="number" class="form-control" placeholder="Cheksiz" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">Bir foydalanuvchi uchun limit</label>
                <input v-model.number="form.user_order_limit" type="number" class="form-control" placeholder="Cheksiz" min="1" />
              </div>
            </div>
          </div>

          <!-- QADAM 5: Yetkazib berish -->
          <div v-if="step === 4">
            <div class="form-section-title">📦 O'lchamlar</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Og'irligi (kg)</label>
                <input v-model.number="form.weight" type="number" step="0.01" class="form-control" placeholder="0.5" />
              </div>
              <div class="form-group">
                <label class="form-label">Uzunligi (sm)</label>
                <input v-model.number="form.length_cm" type="number" step="0.1" class="form-control" placeholder="30" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Eni (sm)</label>
                <input v-model.number="form.width_cm" type="number" step="0.1" class="form-control" placeholder="20" />
              </div>
              <div class="form-group">
                <label class="form-label">Balandligi (sm)</label>
                <input v-model.number="form.height_cm" type="number" step="0.1" class="form-control" placeholder="10" />
              </div>
            </div>

            <div class="form-section-title">🚚 Yetkazib berish</div>
            <div class="form-group">
              <label class="form-label">Yetkazib berish turi</label>
              <select v-model="form.delivery_type" class="form-control">
                <option value="">— Tanlang —</option>
                <option value="standard">Standart</option>
                <option value="express">Ekspres</option>
                <option value="same_day">Bugun</option>
                <option value="pickup">O'zi olib ketish</option>
                <option value="courier">Kuryer</option>
              </select>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Yetkazish narxi (so'm)</label>
                <input v-model.number="form.delivery_price" type="number" class="form-control" placeholder="0" min="0" />
              </div>
              <div class="form-group">
                <label class="form-label">Bepul yetkazish chegarasi (so'm)</label>
                <input v-model.number="form.free_delivery_from" type="number" class="form-control" placeholder="100000" min="0" />
              </div>
            </div>
          </div>

          <!-- QADAM 6: Variantlar -->
          <div v-if="step === 5">
            <div class="form-section-title">🎨 Variantlar</div>
            <p class="text-muted" style="font-size:13px;margin-bottom:16px;">Rang, hajm, xotira, material va boshqa variantlarni qo'shing.</p>

            <div v-for="(v, i) in form.variants" :key="i" class="variant-card">
              <div class="variant-card-header">
                <b>Variant #{{ i + 1 }}</b>
                <button class="btn btn-sm btn-danger" @click="removeVariant(i)">✕ O'chirish</button>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Turi</label>
                  <select v-model="v.type" class="form-control">
                    <option value="rang">Rang</option>
                    <option value="hajm">Hajm</option>
                    <option value="xotira">Xotira</option>
                    <option value="material">Material</option>
                    <option value="model">Model</option>
                    <option value="boshqa">Boshqa</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Nomi/Qiymati</label>
                  <input v-model="v.name" type="text" class="form-control" placeholder="Qizil, XL, 256GB..." />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Narxi (so'm)</label>
                  <input v-model.number="v.price" type="number" class="form-control" placeholder="Ixtiyoriy" />
                </div>
                <div class="form-group">
                  <label class="form-label">Soni</label>
                  <input v-model.number="v.stock" type="number" class="form-control" placeholder="0" />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">SKU</label>
                  <input v-model="v.sku" type="text" class="form-control" placeholder="SKU-001-RED" />
                </div>
                <div class="form-group">
                  <label class="form-label">Barcode</label>
                  <input v-model="v.barcode" type="text" class="form-control" placeholder="1234567890" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Rasm URL</label>
                <input v-model="v.image_url" type="url" class="form-control" placeholder="https://..." />
              </div>
            </div>
            <button class="btn btn-outline" @click="addVariant">+ Variant qo'shish</button>
          </div>

          <!-- QADAM 7: Texnik xususiyatlar -->
          <div v-if="step === 6">
            <div class="form-section-title">⚙️ Texnik xususiyatlar</div>
            <p class="text-muted" style="font-size:13px;margin-bottom:16px;">Dinamik kalit-qiymat juftliklari. Masalan: Brend → Samsung, RAM → 8GB</p>

            <div v-for="(spec, i) in form.specs" :key="i" class="flex gap-8" style="margin-bottom:8px;align-items:center;">
              <input v-model="spec.key" type="text" class="form-control" style="flex:1;" placeholder="Kalit (Masalan: RAM)" />
              <span style="color:#999;flex-shrink:0;">→</span>
              <input v-model="spec.value" type="text" class="form-control" style="flex:1;" placeholder="Qiymati (Masalan: 8GB)" />
              <button class="btn btn-sm btn-danger" @click="removeSpec(i)">✕</button>
            </div>
            <button class="btn btn-outline" style="margin-top:8px;" @click="addSpec">+ Xususiyat qo'shish</button>

            <div class="form-section-title">🔍 SEO</div>
            <div class="form-group">
              <label class="form-label">SEO Title</label>
              <input v-model="form.seo_title" type="text" class="form-control" placeholder="Sahifa sarlavhasi..." />
            </div>
            <div class="form-group">
              <label class="form-label">SEO Description</label>
              <textarea v-model="form.seo_description" class="form-control textarea" placeholder="Meta tavsif..."></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">SEO Keywords</label>
                <input v-model="form.seo_keywords" type="text" class="form-control" placeholder="kalit1, kalit2..." />
              </div>
              <div class="form-group">
                <label class="form-label">Canonical URL</label>
                <input v-model="form.canonical_url" type="url" class="form-control" placeholder="https://..." />
              </div>
            </div>
          </div>

          <!-- QADAM 8: Holat -->
          <div v-if="step === 7">
            <div class="form-section-title">✅ Asosiy holat</div>
            <div class="checkbox-grid">
              <label class="checkbox-item" v-for="f in flagsMain" :key="f.key">
                <input type="checkbox" v-model="form[f.key]" />
                <span>{{ f.label }}</span>
              </label>
            </div>

            <div class="form-section-title" style="margin-top:20px;">🏷️ Marketing flaglari</div>
            <div class="checkbox-grid">
              <label class="checkbox-item" v-for="f in flagsMarketing" :key="f.key">
                <input type="checkbox" v-model="form[f.key]" />
                <span>{{ f.label }}</span>
              </label>
            </div>

            <div class="form-section-title" style="margin-top:20px;">🚀 Ko'rsatish sozlamalari</div>
            <div class="checkbox-grid">
              <label class="checkbox-item" v-for="f in flagsDisplay" :key="f.key">
                <input type="checkbox" v-model="form[f.key]" />
                <span>{{ f.label }}</span>
              </label>
            </div>

            <div class="form-section-title" style="margin-top:20px;">🔧 Xizmat va imkoniyatlar</div>
            <div class="checkbox-grid">
              <label class="checkbox-item" v-for="f in flagsService" :key="f.key">
                <input type="checkbox" v-model="form[f.key]" />
                <span>{{ f.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="wizard-footer">
          <div style="display:flex;gap:12px;align-items:center;">
            <span class="text-muted" style="font-size:13px;">Qadam {{ step + 1 }} / {{ steps.length }}</span>
            <button v-if="step > 0" class="btn btn-outline" @click="prevStep">← Orqaga</button>
          </div>
          <div style="display:flex;gap:12px;">
            <button class="btn btn-outline" @click="closeModal">Bekor qilish</button>
            <button v-if="step < steps.length - 1" class="btn btn-primary" @click="nextStep">Keyingi →</button>
            <button v-else class="btn btn-primary" @click="saveItem" :disabled="saving">
              {{ saving ? 'Saqlanmoqda...' : '💾 Saqlash' }}
            </button>
          </div>
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
const step = ref(0)
const tagsInput = ref('')
const galleryList = ref([])

const steps = [
  'Asosiy', 'Tavsif', 'Rasmlar', 'Narx & Ombor',
  'Yetkazish', 'Variantlar', 'Xususiyatlar & SEO', 'Holat'
]

const flagsMain = [
  { key: 'is_active', label: '✅ Faol' },
  { key: 'is_in_stock', label: '📦 Omborda mavjud' },
  { key: 'is_moderated', label: '🔍 Moderatsiyadan o\'tgan' },
  { key: 'is_archived', label: '📁 Arxivlangan' },
  { key: 'is_secret', label: '🔒 Maxfiy mahsulot' },
  { key: 'has_discount', label: '💸 Chegirmada' },
  { key: 'discount_ending', label: '⏰ Chegirma tugamoqda' },
]
const flagsMarketing = [
  { key: 'is_new', label: '🆕 Yangi mahsulot' },
  { key: 'is_popular', label: '🔥 Mashhur' },
  { key: 'is_recommended', label: '⭐ Tavsiya etiladi' },
  { key: 'is_premium', label: '💎 Premium' },
  { key: 'is_bestseller', label: '🏆 Bestseller' },
  { key: 'is_flash_sale', label: '⚡ Flash Sale' },
  { key: 'is_day_product', label: '📅 Kun mahsuloti' },
  { key: 'is_week_product', label: '📆 Hafta mahsuloti' },
  { key: 'is_month_product', label: '🗓️ Oy mahsuloti' },
  { key: 'is_trend', label: '📈 Trend mahsulot' },
]
const flagsDisplay = [
  { key: 'show_on_home', label: '🏠 Asosiy sahifada' },
  { key: 'show_in_banner', label: '🖼️ Bannerda' },
  { key: 'show_in_carousel', label: '🎠 Karuselda' },
  { key: 'show_in_recommended', label: '💡 Tavsiya etilganlar' },
  { key: 'show_description', label: '📋 Tavsifni ko\'rsatish' },
  { key: 'show_specs', label: '🔧 Xarakt. ko\'rsatish' },
]
const flagsService = [
  { key: 'is_free_delivery', label: '🚀 Bepul yetkazish' },
  { key: 'has_cashback', label: '💰 Cashback mavjud' },
  { key: 'has_warranty', label: '🛡️ Rasmiy kafolat' },
  { key: 'is_original', label: '✔️ Original mahsulot' },
  { key: 'is_certified', label: '📜 Sertifikatlangan' },
  { key: 'is_import', label: '🌍 Import mahsulot' },
  { key: 'is_local', label: '🇺🇿 Mahalliy mahsulot' },
  { key: 'is_returnable', label: '↩️ Qaytarish mumkin' },
  { key: 'is_exchangeable', label: '🔄 Almashtirish mumkin' },
  { key: 'is_online_payment', label: '💳 Onlayn to\'lov' },
  { key: 'is_installment', label: '📅 Bo\'lib to\'lash' },
  { key: 'allow_reviews', label: '💬 Sharhlarga ruxsat' },
  { key: 'allow_qa', label: '❓ Savol-javob ruxsat' },
  { key: 'allow_rating', label: '⭐ Reytingga ruxsat' },
  { key: 'allow_wishlist', label: '❤️ Wishlistga qo\'shish' },
  { key: 'allow_compare', label: '⚖️ Taqqoslashga qo\'shish' },
]

const defaultForm = () => ({
  name: '', name_uz: '', name_ru: '', name_en: '',
  sku: '', barcode: '', brand: '', manufacturer: '', model_name: '',
  category_id: null, subcategory: '', tags: [],
  short_description: '', description: '', full_description: '',
  main_image_url: '', gallery_images: [], image_360_url: '', video_url: '',
  price: 0, sale_price: null, purchase_price: null,
  cashback_percent: 0, bonus_points: 0, vat_percent: 0,
  warehouse_name: '', stock: 0, min_quantity: 1,
  max_order_qty: null, user_order_limit: null,
  weight: null, length_cm: null, width_cm: null, height_cm: null,
  delivery_type: '', delivery_price: 0, free_delivery_from: null,
  variants: [], specs: [],
  seo_title: '', seo_description: '', seo_keywords: '', canonical_url: '',
  is_active: true, is_in_stock: true, is_new: false, is_popular: false,
  is_recommended: false, is_premium: false, is_bestseller: false,
  is_flash_sale: false, is_day_product: false, is_week_product: false,
  is_month_product: false, is_trend: false, has_discount: false,
  discount_ending: false, is_free_delivery: false, has_cashback: false,
  has_warranty: false, is_original: false, is_certified: false,
  is_import: false, is_local: false, is_returnable: false,
  is_exchangeable: false, is_online_payment: true, is_installment: false,
  show_description: true, show_specs: true, allow_reviews: true,
  allow_qa: true, allow_rating: true, allow_wishlist: true,
  allow_compare: true, show_in_recommended: false, show_on_home: false,
  show_in_banner: false, show_in_carousel: false, is_secret: false,
  is_archived: false, is_moderated: true
})

const form = ref(defaultForm())

const filtered = computed(() => {
  let list = items.value
  if (search.value) list = list.filter(p => p.name.toLowerCase().includes(search.value.toLowerCase()))
  if (filterCat.value) list = list.filter(p => p.category_id === filterCat.value)
  return list
})

function formatPrice(v) { return v ? Number(v).toLocaleString('uz-UZ') + ' so\'m' : '—' }
function getCatName(id) { return categories.value.find(c => c.id === id)?.name || '—' }

function goStep(i) { step.value = i }
function nextStep() {
  if (step.value === 0 && !form.value.name.trim()) { formError.value = 'Mahsulot nomi majburiy'; return }
  formError.value = ''
  step.value++
}
function prevStep() { step.value-- }

function addGallery() { galleryList.value.push('') }
function removeGallery(i) { galleryList.value.splice(i, 1) }
function addVariant() {
  form.value.variants.push({ type: 'rang', name: '', price: null, stock: 0, sku: '', barcode: '', image_url: '' })
}
function removeVariant(i) { form.value.variants.splice(i, 1) }
function addSpec() { form.value.specs.push({ key: '', value: '' }) }
function removeSpec(i) { form.value.specs.splice(i, 1) }

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
  tagsInput.value = ''
  galleryList.value = []
  formError.value = ''
  step.value = 0
  showModal.value = true
}

function openEdit(p) {
  editing.value = p
  form.value = { ...defaultForm(), ...p }
  tagsInput.value = (p.tags || []).join(', ')
  galleryList.value = [...(p.gallery_images || [])]
  form.value.variants = p.variants ? JSON.parse(JSON.stringify(p.variants)) : []
  form.value.specs = p.specs ? JSON.parse(JSON.stringify(p.specs)) : []
  formError.value = ''
  step.value = 0
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function saveItem() {
  if (!form.value.name.trim()) { formError.value = 'Mahsulot nomi majburiy'; step.value = 0; return }
  saving.value = true; formError.value = ''
  try {
    const payload = { ...form.value }
    payload.tags = tagsInput.value ? tagsInput.value.split(',').map(t => t.trim()).filter(Boolean) : []
    payload.gallery_images = galleryList.value.filter(Boolean)
    payload.variants = form.value.variants.filter(v => v.name)
    payload.specs = form.value.specs.filter(s => s.key)
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
  gap: 8px;
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
.variant-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 12px;
  background: #f8faff;
}
.variant-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
</style>
