import hashlib
import json
import logging
import os
import random
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from utils.auth import verify_password, get_password_hash, create_access_token, get_current_admin

logger = logging.getLogger(__name__)

DEVSMS_API_TOKEN = os.getenv("DEVSMS_API_TOKEN")
DEVSMS_URL = "https://devsms.uz/api/send_sms.php"
OTP_SECRET = os.getenv("OTP_SECRET", "otp-secret")
OTP_TTL_SECONDS = 120
OTP_RESEND_INTERVAL_SECONDS = 60
OTP_MAX_PER_HOUR = 3
OTP_MAX_ATTEMPTS = 5
SERVICE_NAME = "City Market"
SMS_TEMPLATE_TYPE = 3

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

def normalize_phone(phone: str) -> str:
    if not phone or not isinstance(phone, str):
        raise HTTPException(status_code=400, detail="Telefon raqam noto'g'ri formatda")
    digits = ''.join(ch for ch in phone if ch.isdigit())
    if digits.startswith('998') and len(digits) == 12:
        return digits
    if digits.startswith('0') and len(digits) == 10:
        return '998' + digits[1:]
    if digits.startswith('+998') and len(digits) == 13:
        return digits[1:]
    raise HTTPException(status_code=400, detail="Telefon raqam noto'g'ri formatda")


def hash_otp(phone: str, otp_code: str) -> str:
    payload = f"{phone}|{otp_code}|{OTP_SECRET}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def generate_otp() -> str:
    return f"{random.randint(0, 9999):04d}"


def send_dev_sms(phone: str, otp_code: str | None = None, message: str | None = None) -> dict:
    if not DEVSMS_API_TOKEN:
        raise HTTPException(status_code=500, detail="SMS xizmatini sozlashda muammo bor")

    payload = {
        "phone": phone,
        "type": "universal_otp",
        "template_type": SMS_TEMPLATE_TYPE,
        "service_name": SERVICE_NAME,
    }
    if otp_code is not None:
        payload["otp_code"] = otp_code
    if message is not None:
        payload["message"] = message
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEVSMS_API_TOKEN}',
    }
    request = urllib.request.Request(DEVSMS_URL, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='ignore')
        logger.warning('DevSMS HTTP error phone=%s status=%s body=%s', phone, exc.code, body)
        return {"success": False, "error": "http_error", "body": body}
    except Exception as exc:
        logger.exception('DevSMS connection error for phone=%s', phone)
        return {"success": False, "error": "connection_error", "body": str(exc)}

    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        logger.warning('DevSMS returned non-json body for phone=%s body=%s', phone, body)
        return {"success": False, "error": "invalid_response", "body": body}

    return result


@router.post('/register/request-otp')
def request_register_otp(data: schemas.RegisterOtpRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(data.phone)
    now = datetime.utcnow()

    recent_sms = db.query(models.PhoneOtp).filter(models.PhoneOtp.phone == phone).order_by(models.PhoneOtp.created_at.desc()).first()
    if recent_sms and recent_sms.sent_at and (now - recent_sms.sent_at).total_seconds() < OTP_RESEND_INTERVAL_SECONDS:
        raise HTTPException(status_code=429, detail='Iltimos, bir oz kuting va qayta urinib ko"ring')

    one_hour_ago = now - timedelta(hours=1)
    recent_count = db.query(models.PhoneOtp).filter(models.PhoneOtp.phone == phone, models.PhoneOtp.created_at >= one_hour_ago).count()
    if recent_count >= OTP_MAX_PER_HOUR:
        raise HTTPException(status_code=429, detail='Siz uchun soatiga ruxsat etilgan so"rovlar soni tugadi')

    otp_code = generate_otp()
    otp_hash = hash_otp(phone, otp_code)
    expires_at = now + timedelta(seconds=OTP_TTL_SECONDS)

    otp_record = models.PhoneOtp(
        phone=phone,
        otp_hash=otp_hash,
        status='pending',
        sms_status='pending',
        attempts=0,
        expires_at=expires_at,
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    result = send_dev_sms(phone, otp_code)
    otp_record.sent_at = datetime.utcnow()
    otp_record.sms_id = result.get('sms_id')
    otp_record.request_id = result.get('request_id')
    otp_record.response_body = json.dumps(result, ensure_ascii=False)
    otp_record.sms_status = 'success' if result.get('success') else 'failed'
    if not result.get('success'):
        otp_record.status = 'failed'
        db.commit()
        logger.warning('DevSMS failed for phone=%s result=%s', phone, result)
        raise HTTPException(status_code=502, detail='SMS yuborib bo"lmadi, keyinroq urinib ko"ring')

    db.commit()
    return {"success": True, "message": "Kod yuborildi", "expires_in": OTP_TTL_SECONDS}


@router.post('/register/verify-otp')
def verify_register_otp(data: schemas.RegisterOtpVerify, db: Session = Depends(get_db)):
    phone = normalize_phone(data.phone)
    now = datetime.utcnow()

    otp_record = db.query(models.PhoneOtp).filter(models.PhoneOtp.phone == phone, models.PhoneOtp.status == 'pending').order_by(models.PhoneOtp.created_at.desc()).first()
    if not otp_record:
        raise HTTPException(status_code=400, detail='Kod noto"g"ri yoki eskirgan')
    if now > otp_record.expires_at:
        otp_record.status = 'expired'
        db.commit()
        raise HTTPException(status_code=400, detail='Kod eskirgan, qayta yuboring')
    if otp_record.attempts >= OTP_MAX_ATTEMPTS:
        otp_record.status = 'blocked'
        db.commit()
        raise HTTPException(status_code=400, detail='Juda ko"p urinish, keyinroq urinib ko"ring')

    if hash_otp(phone, data.otp_code) != otp_record.otp_hash:
        otp_record.attempts += 1
        if otp_record.attempts >= OTP_MAX_ATTEMPTS:
            otp_record.status = 'blocked'
        db.commit()
        raise HTTPException(status_code=400, detail='Kod noto"g"ri')

    otp_record.status = 'verified'
    db.commit()

    customer = db.query(models.CustomerUser).filter(models.CustomerUser.phone == phone).first()
    if customer and not customer.phone_verified:
        customer.phone_verified = True
        customer.phone_verified_at = now
        db.commit()

    return {"success": True, "message": "Telefon raqam tasdiqlandi"}


@router.post('/register/complete', response_model=schemas.Token)
def complete_registration(data: schemas.RegisterComplete, db: Session = Depends(get_db)):
    phone = normalize_phone(data.phone)
    now = datetime.utcnow()
    otp_record = db.query(models.PhoneOtp).filter(models.PhoneOtp.phone == phone, models.PhoneOtp.status == 'verified').order_by(models.PhoneOtp.created_at.desc()).first()
    if not otp_record:
        raise HTTPException(status_code=400, detail='Telefon tasdiqlanmagan yoki kod eskirgan')

    customer = db.query(models.CustomerUser).filter(models.CustomerUser.phone == phone).first()
    if customer:
        if data.full_name:
            customer.full_name = data.full_name
        if data.password:
            customer.password_hash = get_password_hash(data.password)
        if not customer.phone_verified:
            customer.phone_verified = True
            customer.phone_verified_at = now
    else:
        password_hash = get_password_hash(data.password) if data.password else None
        customer = models.CustomerUser(
            phone=phone,
            full_name=data.full_name,
            password_hash=password_hash,
            phone_verified=True,
            phone_verified_at=now,
        )
        db.add(customer)

    db.commit()
    db.refresh(customer)
    token = create_access_token({"sub": f"customer:{customer.id}"})
    return {"access_token": token, "token_type": "bearer"}


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
