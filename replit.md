# Do'kon Admin Panel

Oziq-ovqat va uy-ro'zg'or buyumlari do'koni uchun admin boshqaruv paneli. Vue.js frontend + FastAPI backend.

## Run & Operate

- Backend: `cd backend && uvicorn main:app --reload --port 8000` — FastAPI server
- Frontend: `cd frontend && npm run dev` — Vue.js admin panel (port 3000)
- Default login: `admin` / `admin123`

## Stack

- **Frontend**: Vue 3 + Vite + Vue Router + Pinia + Axios — `frontend/` papkasida
- **Backend**: FastAPI + SQLAlchemy + Psycopg2 — `backend/` papkasida
- **Database**: PostgreSQL (DATABASE_URL env)

## Where things live

- `frontend/` — Vue.js admin panel (login, dashboard, kategoriyalar, mahsulotlar, baraban, foydalanuvchilar)
- `backend/` — FastAPI REST API
- `backend/models.py` — SQLAlchemy modellari
- `backend/routers/` — API routerlari
- `backend/schemas.py` — Pydantic schemalar

## Architecture decisions

- Frontend Vite proxy orqali `/api` so'rovlarini backend 8000-portiga yo'naltiradi
- JWT token localStorage'da saqlanadi
- Baraban tizimi: "count" (necha marta ichida 1 ta) va "percent" (foiz) turlari
- Default admin avtomatik yaratiladi (admin/admin123)

## Product

- Dashboard: statistikalar ko'rish
- Kategoriyalar: CRUD
- Mahsulotlar: to'liq ma'lumot, chegirma, video, rasm
- Baraban: yoshlar/kattallar uchun sovg'ali baraban tizimi
- Mijozlar: bloklash, buyurtmalar tarixi
- Adminlar: yangi admin qo'shish

## User preferences

- Vue.js frontend (oddiy CSS, ko'k/oq palitra)
- FastAPI backend
- PostgreSQL database
- `frontend/` va `backend/` papkalar strukturasi

## Gotchas

- Backend va frontend alohida portlarda ishlaydi (8000 va 3000)
- `DATABASE_URL` runtime tomonidan ta'minlanadi
