from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database import get_db
import models
import schemas
from utils.auth import get_current_admin, get_current_customer, get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=schemas.CustomerUserOut)
def get_my_profile(customer=Depends(get_current_customer)):
    return customer

@router.put("/me", response_model=schemas.CustomerUserOut)
def update_my_profile(data: schemas.CustomerProfileUpdate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/me/addresses", response_model=list[schemas.AddressOut])
def get_my_addresses(customer=Depends(get_current_customer)):
    return customer.addresses

@router.post("/me/addresses", response_model=schemas.AddressOut)
def add_my_address(data: schemas.AddressCreate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    if data.is_default:
        for address in customer.addresses:
            address.is_default = False
    address = models.Address(customer_id=customer.id, **data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

@router.put("/me/addresses/{address_id}", response_model=schemas.AddressOut)
def update_my_address(address_id: int, data: schemas.AddressCreate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id, models.Address.customer_id == customer.id).first()
    if not address:
        raise HTTPException(404, "Manzil topilmadi")
    if data.is_default:
        for entry in customer.addresses:
            entry.is_default = False
    for key, value in data.model_dump().items():
        setattr(address, key, value)
    db.commit()
    db.refresh(address)
    return address

@router.delete("/me/addresses/{address_id}")
def delete_my_address(address_id: int, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id, models.Address.customer_id == customer.id).first()
    if not address:
        raise HTTPException(404, "Manzil topilmadi")
    db.delete(address)
    db.commit()
    return {"message": "Manzil o'chirildi"}

@router.get("/me/winnings", response_model=list[schemas.WinningOut])
def get_my_winnings(customer=Depends(get_current_customer)):
    return customer.winnings


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
