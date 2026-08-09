import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import Base, engine
import models
from routers import auth, categories, products, baraban, users, dashboard, commerce, customer_features, admin_features, click, sms
from utils.auth import get_password_hash, verify_password

app = FastAPI(
    title="City Market API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customer_features.router)
app.include_router(commerce.router)
app.include_router(auth.router)
app.include_router(sms.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(baraban.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(admin_features.router)
app.include_router(click.router)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend_dist"
if not FRONTEND_DIR.exists():
    candidate = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if candidate.exists():
        FRONTEND_DIR = candidate

if (FRONTEND_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE customer_users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"))
        connection.execute(text("ALTER TABLE customer_users ADD COLUMN IF NOT EXISTS birth_date VARCHAR(20)"))
        connection.execute(text("ALTER TABLE customer_users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE NOT NULL"))
        connection.execute(text("ALTER TABLE customer_users ADD COLUMN IF NOT EXISTS phone_verified_at TIMESTAMP"))
        connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS click_trans_id BIGINT"))
        connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS click_paydoc_id BIGINT"))
        connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'pending' NOT NULL"))
        connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP"))

    db = Session(engine)

    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.username == admin_username
        ).first()

        if not admin and admin_password:
            admin = models.AdminUser(
                username=admin_username,
                hashed_password=get_password_hash(admin_password)
            )

            db.add(admin)
            db.commit()

            print("✅ Default admin yaratildi")
        elif admin and admin_password and not verify_password(admin_password, admin.hashed_password):
            admin.hashed_password = get_password_hash(admin_password)
            db.commit()
            print("✅ Admin paroli environment qiymati bilan yangilandi")
        elif admin:
            print("✅ Admin allaqachon mavjud")
        else:
            print("ℹ️ Admin yaratilmagan: ADMIN_PASSWORD environment o'zgaruvchisini belgilang")

    finally:
        db.close()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "Do'kon Admin API v2 ishlayapti"
    }


@app.get("/", include_in_schema=False)
def frontend_index():
    if not (FRONTEND_DIR / "index.html").is_file():
        return {"status": "ok", "message": "City Market API ishlayapti. Frontend build topilmadi."}
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/{full_path:path}", include_in_schema=False)
def frontend_fallback(full_path: str):
    requested_file = FRONTEND_DIR / full_path
    if requested_file.is_file():
        return FileResponse(requested_file)
    if (FRONTEND_DIR / "index.html").is_file():
        return FileResponse(FRONTEND_DIR / "index.html")
    return {"detail": "Not Found"}