from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from utils.auth import verify_password, get_password_hash, create_access_token, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.Token)
def register_customer(data: schemas.CustomerRegister, db: Session = Depends(get_db)):
    if db.query(models.CustomerUser).filter(models.CustomerUser.phone == data.phone).first():
        raise HTTPException(status_code=409, detail="Bu telefon raqami allaqachon ro'yxatdan o'tgan")
    customer = models.CustomerUser(phone=data.phone, full_name=data.full_name, password_hash=get_password_hash(data.password))
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"access_token": create_access_token({"sub": f"customer:{customer.id}"}), "token_type": "bearer"}

@router.post("/customer-login", response_model=schemas.Token)
def customer_login(data: schemas.CustomerRegister, db: Session = Depends(get_db)):
    customer = db.query(models.CustomerUser).filter(models.CustomerUser.phone == data.phone).first()
    if not customer or not customer.password_hash or not verify_password(data.password, customer.password_hash):
        raise HTTPException(status_code=401, detail="Telefon yoki parol noto'g'ri")
    if customer.is_blocked or not customer.is_active:
        raise HTTPException(status_code=403, detail="Foydalanuvchi bloklangan")
    return {"access_token": create_access_token({"sub": f"customer:{customer.id}"}), "token_type": "bearer"}

@router.post("/verify-sms", response_model=schemas.Token)
def verify_sms(data: schemas.CustomerRegister, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="SMS integratsiyasi hozircha yoqilmagan")


@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == request.username).first()
    if not admin or not verify_password(request.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol noto'g'ri"
        )
    if not admin.is_active:
        raise HTTPException(status_code=400, detail="Foydalanuvchi bloklangan")
    
    token = create_access_token(data={"sub": f"admin:{admin.username}"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.AdminUserOut)
def get_me(current_admin=Depends(get_current_admin)):
    return current_admin


@router.post("/admins", response_model=schemas.AdminUserOut)
def create_admin(data: schemas.AdminUserCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    existing = db.query(models.AdminUser).filter(models.AdminUser.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu username allaqachon mavjud")
    
    hashed = get_password_hash(data.password)
    admin = models.AdminUser(username=data.username, hashed_password=hashed)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.get("/admins", response_model=list[schemas.AdminUserOut])
def list_admins(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return db.query(models.AdminUser).all()
