import os
import hashlib
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(tags=["click"])

CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY")
CLICK_MERCHANT_USER_ID = os.getenv("CLICK_MERCHANT_USER_ID")

if not CLICK_SERVICE_ID or not CLICK_MERCHANT_ID or not CLICK_SECRET_KEY:
    raise RuntimeError("CLICK_SERVICE_ID, CLICK_MERCHANT_ID va CLICK_SECRET_KEY .env fayldan o'qilishi kerak")


def verify_click_sign(
    click_trans_id: int,
    service_id: int,
    click_paydoc_id: int,
    merchant_trans_id: int,
    amount: str,
    action: int,
    error: int,
    error_note: str,
    sign_time: str,
    sign_string: str
) -> bool:
    payload = (
        f"{click_trans_id}"
        f"{service_id}"
        f"{click_paydoc_id}"
        f"{merchant_trans_id}"
        f"{amount}"
        f"{action}"
        f"{error}"
        f"{error_note}"
        f"{sign_time}"
        f"{CLICK_SECRET_KEY}"
    )
    expected = hashlib.md5(payload.encode("utf-8")).hexdigest()
    return expected.lower() == sign_string.lower()


def build_error_response(code: int, note: str):
    return {"error": code, "error_note": note}


@router.post("/api/click/prepare")
def click_prepare(
    click_trans_id: int = Form(...),
    service_id: int = Form(...),
    click_paydoc_id: int = Form(...),
    merchant_trans_id: int = Form(...),
    amount: str = Form(...),
    action: int = Form(...),
    error: int = Form(0),
    error_note: str = Form(""),
    sign_time: str = Form(...),
    sign_string: str = Form(...),
    merchant_id: int | None = Form(None),
    merchant_user_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    if not verify_click_sign(
        click_trans_id,
        service_id,
        click_paydoc_id,
        merchant_trans_id,
        amount,
        action,
        error,
        error_note,
        sign_time,
        sign_string,
    ):
        raise HTTPException(status_code=401, detail="Invalid click signature")

    if str(service_id) != CLICK_SERVICE_ID:
        return build_error_response(-1, "Service ID noto'g'ri")

    if merchant_user_id is not None and CLICK_MERCHANT_USER_ID and str(merchant_user_id) != CLICK_MERCHANT_USER_ID:
        return build_error_response(-1, "Merchant user ID noto'g'ri")

    order = db.query(models.Order).filter(models.Order.id == merchant_trans_id).first()
    if not order:
        return build_error_response(-5, "Buyurtma topilmadi")

    try:
        amount_value = Decimal(amount)
    except Exception:
        return build_error_response(-2, "Summa noto'g'ri")

    if amount_value != Decimal(str(order.total_price)):
        return build_error_response(-2, "Summa noto'g'ri")

    order.click_trans_id = click_trans_id
    order.click_paydoc_id = click_paydoc_id
    order.payment_status = "pending"
    db.commit()
    return {"merchant_prepare_id": merchant_trans_id}


@router.post("/api/click/complete")
def click_complete(
    click_trans_id: int = Form(...),
    service_id: int = Form(...),
    click_paydoc_id: int = Form(...),
    merchant_trans_id: int = Form(...),
    amount: str = Form(...),
    action: int = Form(...),
    error: int = Form(0),
    error_note: str = Form(""),
    sign_time: str = Form(...),
    sign_string: str = Form(...),
    merchant_user_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    if not verify_click_sign(
        click_trans_id,
        service_id,
        click_paydoc_id,
        merchant_trans_id,
        amount,
        action,
        error,
        error_note,
        sign_time,
        sign_string,
    ):
        raise HTTPException(status_code=401, detail="Invalid click signature")

    if str(service_id) != CLICK_SERVICE_ID:
        return build_error_response(-1, "Service ID noto'g'ri")

    if merchant_user_id is not None and CLICK_MERCHANT_USER_ID and str(merchant_user_id) != CLICK_MERCHANT_USER_ID:
        return build_error_response(-1, "Merchant user ID noto'g'ri")

    order = db.query(models.Order).filter(models.Order.id == merchant_trans_id).first()
    if not order:
        return build_error_response(-5, "Buyurtma topilmadi")

    try:
        amount_value = Decimal(amount)
    except Exception:
        return build_error_response(-2, "Summa noto'g'ri")

    if amount_value != Decimal(str(order.total_price)):
        return build_error_response(-2, "Summa noto'g'ri")

    order.click_trans_id = click_trans_id
    order.click_paydoc_id = click_paydoc_id
    order.payment_status = "paid"
    order.paid_at = datetime.utcnow()
    db.commit()
    return {"merchant_confirm_id": merchant_trans_id}
