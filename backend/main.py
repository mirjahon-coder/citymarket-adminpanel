import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models
from routers import auth, categories, products, baraban, users, dashboard
from utils.auth import get_password_hash
from sqlalchemy.orm import Session

app = FastAPI(title="Do'kon Admin API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    # DEV: yangi sxema bilan qayta yaratish
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Default admin
    db = Session(engine)
    try:
        admin = models.AdminUser(
            username="admin",
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("✅ Jadvallar yangilandi. Default admin: admin / admin123")
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Do'kon Admin API v2 ishlayapti"}
