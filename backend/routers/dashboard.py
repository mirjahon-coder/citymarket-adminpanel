from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    total_products = db.query(func.count(models.Product.id)).scalar() or 0
    total_categories = db.query(func.count(models.Category.id)).scalar() or 0
    total_customers = db.query(func.count(models.CustomerUser.id)).scalar() or 0
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    total_revenue = db.query(func.sum(models.Order.total_price)).scalar() or 0.0
    active_barabanlar = db.query(func.count(models.Baraban.id)).filter(models.Baraban.is_active == True).scalar() or 0
    blocked_customers = db.query(func.count(models.CustomerUser.id)).filter(models.CustomerUser.is_blocked == True).scalar() or 0
    low_stock_products = db.query(func.count(models.Product.id)).filter(models.Product.stock <= 5).scalar() or 0

    return schemas.DashboardStats(
        total_products=total_products,
        total_categories=total_categories,
        total_customers=total_customers,
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        active_barabanlar=active_barabanlar,
        blocked_customers=blocked_customers,
        low_stock_products=low_stock_products,
    )
