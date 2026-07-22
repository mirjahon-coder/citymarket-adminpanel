from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/baraban", tags=["baraban"])


@router.get("", response_model=List[schemas.BarabanOut])
def get_barabanlar(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(models.Baraban).options(joinedload(models.Baraban.prizes)).all()


@router.post("", response_model=schemas.BarabanOut)
def create_baraban(data: schemas.BarabanCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    baraban = models.Baraban(**data.model_dump())
    db.add(baraban)
    db.commit()
    db.refresh(baraban)
    return baraban


@router.get("/{baraban_id}", response_model=schemas.BarabanOut)
def get_baraban(baraban_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    baraban = db.query(models.Baraban).options(joinedload(models.Baraban.prizes)).filter(models.Baraban.id == baraban_id).first()
    if not baraban:
        raise HTTPException(status_code=404, detail="Baraban topilmadi")
    return baraban


@router.put("/{baraban_id}", response_model=schemas.BarabanOut)
def update_baraban(baraban_id: int, data: schemas.BarabanUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    baraban = db.query(models.Baraban).filter(models.Baraban.id == baraban_id).first()
    if not baraban:
        raise HTTPException(status_code=404, detail="Baraban topilmadi")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(baraban, key, value)
    db.commit()
    db.refresh(baraban)
    return baraban


@router.delete("/{baraban_id}")
def delete_baraban(baraban_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    baraban = db.query(models.Baraban).filter(models.Baraban.id == baraban_id).first()
    if not baraban:
        raise HTTPException(status_code=404, detail="Baraban topilmadi")
    db.delete(baraban)
    db.commit()
    return {"message": "Baraban o'chirildi"}


# Sovg'alar (prizes)
@router.post("/{baraban_id}/prizes", response_model=schemas.BarabanPrizeOut)
def add_prize(baraban_id: int, data: schemas.BarabanPrizeCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    baraban = db.query(models.Baraban).filter(models.Baraban.id == baraban_id).first()
    if not baraban:
        raise HTTPException(status_code=404, detail="Baraban topilmadi")
    prize = models.BarabanPrize(baraban_id=baraban_id, **data.model_dump())
    db.add(prize)
    db.commit()
    db.refresh(prize)
    return prize


@router.put("/{baraban_id}/prizes/{prize_id}", response_model=schemas.BarabanPrizeOut)
def update_prize(baraban_id: int, prize_id: int, data: schemas.BarabanPrizeUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    prize = db.query(models.BarabanPrize).filter(
        models.BarabanPrize.id == prize_id,
        models.BarabanPrize.baraban_id == baraban_id
    ).first()
    if not prize:
        raise HTTPException(status_code=404, detail="Sovg'a topilmadi")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(prize, key, value)
    db.commit()
    db.refresh(prize)
    return prize


@router.delete("/{baraban_id}/prizes/{prize_id}")
def delete_prize(baraban_id: int, prize_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    prize = db.query(models.BarabanPrize).filter(
        models.BarabanPrize.id == prize_id,
        models.BarabanPrize.baraban_id == baraban_id
    ).first()
    if not prize:
        raise HTTPException(status_code=404, detail="Sovg'a topilmadi")
    db.delete(prize)
    db.commit()
    return {"message": "Sovg'a o'chirildi"}
