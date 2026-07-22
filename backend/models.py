from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    has_discount = Column(Boolean, default=False)
    stock = Column(Integer, default=0)
    sku = Column(String(100), nullable=True)
    brand = Column(String(200), nullable=True)
    weight = Column(Float, nullable=True)
    dimensions = Column(String(200), nullable=True)
    video_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)

    product = relationship("Product", back_populates="images")


class CustomerUser(Base):
    __tablename__ = "customer_users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    full_name = Column(String(200), nullable=True)
    email = Column(String(200), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer_users.id"), nullable=False)
    status = Column(String(50), default="pending")
    total_price = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("CustomerUser", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(300), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")


class Baraban(Base):
    __tablename__ = "barabanlar"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    target_audience = Column(String(50), default="yoshlar")  # yoshlar, kattallar
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prizes = relationship("BarabanPrize", back_populates="baraban", cascade="all, delete-orphan")


class BarabanPrize(Base):
    __tablename__ = "baraban_prizes"

    id = Column(Integer, primary_key=True, index=True)
    baraban_id = Column(Integer, ForeignKey("barabanlar.id"), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_mega_prize = Column(Boolean, default=False)
    probability_type = Column(String(50), default="count")  # count, percent
    probability_value = Column(Float, default=10.0)  # Foiz yoki necha marta 1da bitta
    total_count = Column(Integer, default=10)  # Umumiy sondan nechta sovg'a
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    baraban = relationship("Baraban", back_populates="prizes")
