from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.auth import get_current_admin

router = APIRouter(tags=["admin features"])


def crud_list(model, db):
    return db.query(model).all()


@router.get("/api/banners")
def list_banners(db: Session = Depends(get_db)):
    return crud_list(models.Banner, db)

@router.post("/api/banners")
def create_banner(data: schemas.BannerCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = models.Banner(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.put("/api/banners/{item_id}")
def update_banner(item_id: int, data: schemas.BannerCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = db.query(models.Banner).filter(models.Banner.id == item_id).first()
    if not item: raise HTTPException(404, "Banner topilmadi")
    for key, value in data.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.delete("/api/banners/{item_id}")
def delete_banner(item_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = db.query(models.Banner).filter(models.Banner.id == item_id).first()
    if not item: raise HTTPException(404, "Banner topilmadi")
    db.delete(item); db.commit(); return {"message": "Banner o'chirildi"}

@router.get("/api/promotions")
def list_promotions(db: Session = Depends(get_db)):
    return crud_list(models.Promotion, db)

@router.post("/api/promotions")
def create_promotion(data: schemas.PromotionCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = models.Promotion(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item); return item

@router.put("/api/promotions/{item_id}")
def update_promotion(item_id: int, data: schemas.PromotionCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = db.query(models.Promotion).filter(models.Promotion.id == item_id).first()
    if not item: raise HTTPException(404, "Aksiya topilmadi")
    for key, value in data.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/api/promotions/{item_id}")
def delete_promotion(item_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = db.query(models.Promotion).filter(models.Promotion.id == item_id).first()
    if not item: raise HTTPException(404, "Aksiya topilmadi")
    db.delete(item); db.commit(); return {"message": "Aksiya o'chirildi"}

@router.get("/api/roles")
def list_roles(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return crud_list(models.AdminRole, db)

@router.post("/api/roles")
def create_role(data: schemas.RoleCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = models.AdminRole(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item); return item

@router.put("/api/roles/{item_id}")
def update_role(item_id: int, data: schemas.RoleCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = db.query(models.AdminRole).filter(models.AdminRole.id == item_id).first()
    if not item: raise HTTPException(404, "Rol topilmadi")
    item.name = data.name; item.permissions = data.permissions
    db.commit(); db.refresh(item); return item

@router.delete("/api/roles/{item_id}")
def delete_role(item_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    item = db.query(models.AdminRole).filter(models.AdminRole.id == item_id).first()
    if not item: raise HTTPException(404, "Rol topilmadi")
    db.delete(item); db.commit(); return {"message": "Rol o'chirildi"}

@router.get("/api/audit-logs")
def audit_logs(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(200).all()

@router.get("/api/admins/{admin_id}/roles")
def list_admin_roles(admin_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    if not admin: raise HTTPException(404, "Admin topilmadi")
    return admin.roles

@router.post("/api/admins/{admin_id}/roles")
def assign_role(admin_id: int, data: schemas.RoleAssignment, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    role_id = data.role_id
    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    role = db.query(models.AdminRole).filter(models.AdminRole.id == role_id).first()
    if not admin or not role: raise HTTPException(404, "Admin yoki rol topilmadi")
    if role not in admin.roles: admin.roles.append(role)
    db.commit(); return {"message": "Rol biriktirildi"}

@router.put("/api/admins/{admin_id}/roles")
def replace_roles(admin_id: int, data: schemas.RoleAssignment, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    role = db.query(models.AdminRole).filter(models.AdminRole.id == data.role_id).first()
    if not admin or not role: raise HTTPException(404, "Admin yoki rol topilmadi")
    admin.roles = [role]
    db.commit()
    return {"message": "Admin roli yangilandi"}

@router.delete("/api/admins/{admin_id}/roles")
def remove_role(admin_id: int, role_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    role = db.query(models.AdminRole).filter(models.AdminRole.id == role_id).first()
    if not admin or not role: raise HTTPException(404, "Admin yoki rol topilmadi")
    if role in admin.roles: admin.roles.remove(role)
    db.commit(); return {"message": "Rol olib tashlandi"}
