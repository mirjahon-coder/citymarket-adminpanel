from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models, schemas
from utils.auth import get_current_customer

router = APIRouter(tags=["customer commerce"])


def get_cart(customer, db):
    cart = customer.cart
    if not cart:
        cart = models.Cart(customer_id=customer.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def cart_response(cart):
    items = []
    total = 0.0
    for item in cart.items:
        price = item.product.sale_price if item.product.sale_price is not None else item.product.price
        total += price * item.quantity
        items.append({"id": item.id, "product_id": item.product_id, "quantity": item.quantity,
                      "product_name": item.product.name, "unit_price": price})
    return {"id": cart.id, "items": items, "total_price": total}


@router.get("/api/cart", response_model=schemas.CartOut)
def get_cart_items(customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    cart = get_cart(customer, db)
    return cart_response(cart)


@router.post("/api/cart/items", response_model=schemas.CartOut)
def add_cart_item(data: schemas.CartItemCreate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == data.product_id, models.Product.is_active == True).first()
    if not product:
        raise HTTPException(404, "Mahsulot topilmadi")
    if data.quantity < 1 or data.quantity > product.stock:
        raise HTTPException(400, "Mahsulot qoldig'i yetarli emas")
    cart = get_cart(customer, db)
    item = next((entry for entry in cart.items if entry.product_id == product.id), None)
    if item:
        item.quantity += data.quantity
    else:
        db.add(models.CartItem(cart_id=cart.id, product_id=product.id, quantity=data.quantity))
    db.commit()
    db.refresh(cart)
    return cart_response(cart)


@router.put("/api/cart/items/{item_id}", response_model=schemas.CartOut)
def update_cart_item(item_id: int, data: schemas.CartItemUpdate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    item = db.query(models.CartItem).join(models.Cart).filter(models.CartItem.id == item_id, models.Cart.customer_id == customer.id).first()
    if not item:
        raise HTTPException(404, "Savat mahsuloti topilmadi")
    if data.quantity < 1 or data.quantity > item.product.stock:
        raise HTTPException(400, "Miqdor noto'g'ri")
    item.quantity = data.quantity
    db.commit()
    return cart_response(item.cart)


@router.delete("/api/cart/items/{item_id}")
def delete_cart_item(item_id: int, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    item = db.query(models.CartItem).join(models.Cart).filter(models.CartItem.id == item_id, models.Cart.customer_id == customer.id).first()
    if not item:
        raise HTTPException(404, "Savat mahsuloti topilmadi")
    db.delete(item)
    db.commit()
    return {"message": "Mahsulot savatdan olib tashlandi"}


@router.post("/api/orders", response_model=schemas.OrderOut)
def create_order(data: schemas.OrderCreate, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    cart = get_cart(customer, db)
    if not cart.items:
        raise HTTPException(400, "Savat bo'sh")
    order = models.Order(customer_id=customer.id, status="pending", total_price=0)
    db.add(order)
    total = 0.0
    for item in list(cart.items):
        product = item.product
        if item.quantity > product.stock:
            raise HTTPException(400, f"{product.name} uchun qoldiq yetarli emas")
        price = product.sale_price if product.sale_price is not None else product.price
        order.items.append(models.OrderItem(product_id=product.id, product_name=product.name, quantity=item.quantity, unit_price=price))
        product.stock -= item.quantity
        product.sold_count += item.quantity
        total += price * item.quantity
        db.delete(item)
    order.total_price = total
    db.commit()
    db.refresh(order)
    return order


@router.get("/api/orders", response_model=list[schemas.OrderOut])
def list_orders(customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    return db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.customer_id == customer.id).order_by(models.Order.created_at.desc()).all()


@router.get("/api/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    order = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id, models.Order.customer_id == customer.id).first()
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")
    return order


@router.post("/api/orders/{order_id}/cancel")
def cancel_order(order_id: int, customer=Depends(get_current_customer), db: Session = Depends(get_db)):
    order = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id, models.Order.customer_id == customer.id).first()
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")
    if order.status not in {"pending", "new"}:
        raise HTTPException(400, "Bu buyurtmani bekor qilib bo'lmaydi")
    order.status = "cancelled"
    for item in order.items:
        if item.product_id:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
    db.commit()
    return {"message": "Buyurtma bekor qilindi", "status": order.status}
