import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine
import models
from routers import auth, categories, products, baraban, users, dashboard
from utils.auth import get_password_hash

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

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(baraban.router)
app.include_router(users.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

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