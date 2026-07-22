from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[schemas.CustomerUserOut])
def get_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    query = db.query(models.CustomerUser)
    if search:
        query = query.filter(
            models.CustomerUser.full_name.ilike(f"%{search}%") |
            models.CustomerUser.phone.ilike(f"%{search}%") |
            models.CustomerUser.email.ilike(f"%{search}%")
        )
    if is_blocked is not None:
        query = query.filter(models.CustomerUser.is_blocked == is_blocked)
    return query.offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=schemas.CustomerUserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    user = db.query(models.CustomerUser).filter(models.CustomerUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user


@router.get("/{user_id}/orders", response_model=List[schemas.OrderOut])
def get_user_orders(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    user = db.query(models.CustomerUser).filter(models.CustomerUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    orders = db.query(models.Order).options(joinedload(models.Order.items)).filter(
        models.Order.customer_id == user_id
    ).all()
    return orders


@router.post("/{user_id}/block")
def block_user(user_id: int, data: schemas.BlockUserRequest, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    user = db.query(models.CustomerUser).filter(models.CustomerUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.is_blocked = True
    user.block_reason = data.reason
    db.commit()
    return {"message": "Foydalanuvchi bloklandi"}


@router.post("/{user_id}/unblock")
def unblock_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    user = db.query(models.CustomerUser).filter(models.CustomerUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.is_blocked = False
    user.block_reason = None
    db.commit()
    return {"message": "Foydalanuvchi blokdan chiqarildi"}
