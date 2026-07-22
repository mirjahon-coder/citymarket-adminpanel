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
    # Asosiy nom
    name = Column(String(200), nullable=False)
    name_uz = Column(String(200), nullable=True)
    name_ru = Column(String(200), nullable=True)
    name_en = Column(String(200), nullable=True)
    # Meta
    slug = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    # Rasmlar
    icon_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)   # asosiy rasm
    banner_url = Column(String(500), nullable=True)
    cover_url = Column(String(500), nullable=True)
    # Joylashuv va tartib
    location = Column(String(300), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    # Holat flaglari
    is_active = Column(Boolean, default=True)
    show_on_home = Column(Boolean, default=False)
    show_in_menu = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False)
    filter_enabled = Column(Boolean, default=False)
    show_in_discount = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="category")
    children = relationship("Category", foreign_keys=[parent_id], backref="parent", remote_side="Category.id")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    # Nomlar
    name = Column(String(300), nullable=False)
    name_uz = Column(String(300), nullable=True)
    name_ru = Column(String(300), nullable=True)
    name_en = Column(String(300), nullable=True)
    # Identifikatorlar
    sku = Column(String(100), nullable=True)
    barcode = Column(String(100), nullable=True)
    brand = Column(String(200), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    model_name = Column(String(200), nullable=True)
    # Kategoriya
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory = Column(String(200), nullable=True)
    tags = Column(JSON, nullable=True)  # ['tag1', 'tag2']
    # Tavsiflar
    short_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)
    # Rasmlar
    main_image_url = Column(String(500), nullable=True)
    gallery_images = Column(JSON, nullable=True)   # ['url1','url2']
    image_360_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    # Narxlar
    price = Column(Float, nullable=False, default=0)          # original narx
    sale_price = Column(Float, nullable=True)                 # sotuv narxi
    purchase_price = Column(Float, nullable=True)             # xarid narxi
    cashback_percent = Column(Float, nullable=True, default=0)
    bonus_points = Column(Float, nullable=True, default=0)
    vat_percent = Column(Float, nullable=True, default=0)
    # Ombor
    warehouse_name = Column(String(200), nullable=True)
    stock = Column(Integer, default=0)
    min_quantity = Column(Integer, default=1)
    max_order_qty = Column(Integer, nullable=True)
    user_order_limit = Column(Integer, nullable=True)
    # Yetkazib berish
    weight = Column(Float, nullable=True)
    length_cm = Column(Float, nullable=True)
    width_cm = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    delivery_type = Column(String(100), nullable=True)
    delivery_price = Column(Float, nullable=True, default=0)
    free_delivery_from = Column(Float, nullable=True)
    # Variantlar va xususiyatlar
    variants = Column(JSON, nullable=True)  # [{type,name,price,stock,sku,barcode,image_url}]
    specs = Column(JSON, nullable=True)     # [{key,value}]
    # SEO
    seo_title = Column(String(300), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(String(500), nullable=True)
    canonical_url = Column(String(500), nullable=True)
    # Statistikalar
    views_count = Column(Integer, default=0)
    sold_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    # Holat (asosiy)
    is_active = Column(Boolean, default=True)
    is_in_stock = Column(Boolean, default=True)
    # Holat (qo'shimcha flaglar)
    is_new = Column(Boolean, default=False)
    is_popular = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_bestseller = Column(Boolean, default=False)
    is_flash_sale = Column(Boolean, default=False)
    is_day_product = Column(Boolean, default=False)
    is_week_product = Column(Boolean, default=False)
    is_month_product = Column(Boolean, default=False)
    is_trend = Column(Boolean, default=False)
    has_discount = Column(Boolean, default=False)
    discount_ending = Column(Boolean, default=False)
    is_free_delivery = Column(Boolean, default=False)
    has_cashback = Column(Boolean, default=False)
    has_warranty = Column(Boolean, default=False)
    is_original = Column(Boolean, default=False)
    is_certified = Column(Boolean, default=False)
    is_import = Column(Boolean, default=False)
    is_local = Column(Boolean, default=False)
    is_returnable = Column(Boolean, default=False)
    is_exchangeable = Column(Boolean, default=False)
    is_online_payment = Column(Boolean, default=True)
    is_installment = Column(Boolean, default=False)
    show_description = Column(Boolean, default=True)
    show_specs = Column(Boolean, default=True)
    allow_reviews = Column(Boolean, default=True)
    allow_qa = Column(Boolean, default=True)
    allow_rating = Column(Boolean, default=True)
    allow_wishlist = Column(Boolean, default=True)
    allow_compare = Column(Boolean, default=True)
    show_in_recommended = Column(Boolean, default=False)
    show_on_home = Column(Boolean, default=False)
    show_in_banner = Column(Boolean, default=False)
    show_in_carousel = Column(Boolean, default=False)
    is_secret = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=True)
    # Timestamps
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
    target_audience = Column(String(50), default="yoshlar")
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
    probability_type = Column(String(50), default="count")
    probability_value = Column(Float, default=10.0)
    total_count = Column(Integer, default=10)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    baraban = relationship("Baraban", back_populates="prizes")
