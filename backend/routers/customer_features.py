import base64
import io
import random
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.auth import get_current_customer, get_current_admin

router = APIRouter(tags=["customer features"])


def find_baraban(kind, db):
    audience = "yoshlar" if kind == "small" else "kattalar"
    baraban = db.query(models.Baraban).filter(models.Baraban.is_active == True, models.Baraban.target_audience == audience).first()
    if not baraban:
        baraban = db.query(models.Baraban).filter(models.Baraban.is_active == True).first()
    if not baraban:
        raise HTTPException(404, "Faol baraban topilmadi")
    return baraban


def spin(kind, customer, db):
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    used = db.query(models.SpinLog).filter(models.SpinLog.customer_id == customer.id, models.SpinLog.baraban_type == kind, models.SpinLog.created_at >= start).first()
    if used:
        raise HTTPException(409, f"Bugungi {kind} baraban aylantirilgan")
    baraban = find_baraban(kind, db)
    prizes = [p for p in baraban.prizes if p.is_active and p.total_count > 0]
    if not prizes:
        raise HTTPException(409, "Faol sovg'a mavjud emas")
    weights = [max(float(p.probability_value), 0.01) for p in prizes]
    prize = random.choices(prizes, weights=weights, k=1)[0]
    prize.total_count -= 1
    winning = models.Winning(customer_id=customer.id, baraban_type=kind, prize_name=prize.name, qr_token=secrets.token_urlsafe(24), expires_at=datetime.utcnow() + timedelta(days=7))
    db.add(winning)
    db.flush()
    db.add(models.SpinLog(customer_id=customer.id, baraban_type=kind, winning_id=winning.id))
    db.commit()
    db.refresh(winning)
    return winning


@router.get("/api/baraban/big", response_model=schemas.BarabanOut)
def big_baraban(db: Session = Depends(get_db)):
    return find_baraban("big", db)


@router.get("/api/baraban/small", response_model=schemas.BarabanOut)
def small_baraban(db: Session = Depends(get_db)):
    return find_baraban("small", db)


@router.post("/api/baraban/big/spin", response_model=schemas.WinningOut)
def spin_big(customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    return spin("big", customer, db)


@router.post("/api/baraban/small/spin", response_model=schemas.WinningOut)
def spin_small(customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    return spin("small", customer, db)

@router.get("/api/baraban/{baraban_id}/stats")
def baraban_stats(baraban_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    baraban = db.query(models.Baraban).filter(models.Baraban.id == baraban_id).first()
    if not baraban:
        raise HTTPException(404, "Baraban topilmadi")
    kind = "small" if baraban.target_audience == "yoshlar" else "big"
    spins = db.query(models.SpinLog).filter(models.SpinLog.baraban_type == kind).count()
    return {"baraban_id": baraban_id, "total_spins": spins}


@router.get("/api/winnings/{winning_id}/qr")
def winning_qr(winning_id: int, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    winning = db.query(models.Winning).filter(models.Winning.id == winning_id, models.Winning.customer_id == customer.id).first()
    if not winning:
        raise HTTPException(404, "Yutuq topilmadi")
    try:
        import qrcode
        image = qrcode.make(winning.qr_token)
        output = io.BytesIO()
        image.save(output, format="PNG")
        png = base64.b64encode(output.getvalue()).decode()
        return {"winning_id": winning.id, "qr_token": winning.qr_token, "qr_png_base64": png, "expires_at": winning.expires_at}
    except ImportError:
        return {"winning_id": winning.id, "qr_token": winning.qr_token, "expires_at": winning.expires_at}


@router.post("/api/cashier/verify-check")
def verify_check(data: schemas.CashierVerify, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    winning = db.query(models.Winning).filter(models.Winning.qr_token == data.qr_token).first()
    if not winning:
        raise HTTPException(404, "QR yutuq topilmadi")
    if winning.status != "available" or (winning.expires_at and winning.expires_at < datetime.utcnow()):
        raise HTTPException(400, "QR yaroqsiz yoki muddati o'tgan")
    return {"valid": True, "winning_id": winning.id, "prize_name": winning.prize_name, "status": winning.status}


@router.post("/api/cashier/confirm-prize")
def confirm_prize(data: schemas.CashierVerify, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    winning = db.query(models.Winning).filter(models.Winning.qr_token == data.qr_token).first()
    if not winning:
        raise HTTPException(404, "QR yutuq topilmadi")
    winning.status = "claimed"
    db.commit()
    return {"message": "Sovg'a berildi", "winning_id": winning.id}


@router.get("/api/cashier/audit")
def cashier_audit(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(models.Winning).order_by(models.Winning.created_at.desc()).limit(100).all()


@router.post("/api/notifications/register-device")
def register_device(data: schemas.DeviceTokenCreate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    notification = models.Notification(customer_id=customer.id, title="Device", body="Device registered", device_token=data.device_token)
    db.add(notification)
    db.commit()
    return {"message": "Device token saqlandi"}


@router.get("/api/notifications", response_model=list[schemas.NotificationOut])
def notifications(customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(models.Notification.customer_id == customer.id).order_by(models.Notification.created_at.desc()).all()

@router.get("/api/notifications/history", response_model=list[schemas.NotificationOut])
def notification_history(customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    return notifications(customer, db)


@router.post("/api/notifications/send")
def send_notification(data: schemas.NotificationCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    notification = models.Notification(**data.model_dump())
    db.add(notification)
    db.commit()
    return {"message": "Bildirishnoma saqlandi", "id": notification.id}


@router.post("/api/notifications/register")
def register_notification_alias(data: schemas.DeviceTokenCreate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    return register_device(data, customer, db)
