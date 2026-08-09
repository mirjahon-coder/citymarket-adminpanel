import json
import logging
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from utils.auth import get_current_admin
from routers.auth import send_dev_sms

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.get("/status", response_model=schemas.SmsStatusResponse, summary="SMS provayder holatini olish")
def get_sms_status() -> schemas.SmsStatusResponse:
    configured = bool(os.getenv("DEVSMS_API_TOKEN"))
    return schemas.SmsStatusResponse(
        provider="devsms",
        configured=configured,
        message="SMS provayder sozlangan" if configured else "DEVSMS_API_TOKEN topilmadi",
    )


@router.post("/send", response_model=schemas.SmsSendResponse, summary="SMS yuborish")
def send_sms(
    payload: schemas.SmsSendRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    normalized_phone = payload.phone
    try:
        from routers.auth import normalize_phone

        normalized_phone = normalize_phone(payload.phone)
    except HTTPException:
        pass

    result = send_dev_sms(normalized_phone, message=payload.message)
    if not result.get("success"):
        raise HTTPException(status_code=502, detail="SMS yuborib bo'lmadi")

    otp_record = models.PhoneOtp(
        phone=normalized_phone,
        otp_hash="manual-sms",
        status="sent",
        sms_status="success",
        attempts=0,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        sent_at=datetime.utcnow(),
        sms_id=result.get("sms_id"),
        request_id=result.get("request_id"),
        response_body=json.dumps(result, ensure_ascii=False),
    )
    db.add(otp_record)
    db.commit()

    return schemas.SmsSendResponse(
        success=True,
        message="SMS muvaffaqiyatli yuborildi",
        provider_response=result,
    )


@router.get("/history", response_model=list[schemas.SmsRequestOut], summary="So'nggi SMS tarixini olish")
def sms_history(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    records = db.query(models.PhoneOtp).order_by(models.PhoneOtp.created_at.desc()).limit(20).all()
    return records
